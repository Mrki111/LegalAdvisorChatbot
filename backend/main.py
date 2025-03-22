import os
from datetime import datetime
import psycopg
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from langchain_postgres import PostgresChatMessageHistory
from pydantic import BaseModel
from typing import List, Optional

# SQLAlchemy imports for audit logging (optional)
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base

# LangChain imports
from langchain_openai import ChatOpenAI
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate
)

load_dotenv()

# Environment and DB Setup
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("Missing OPENAI_API_KEY!")

POSTGRES_USER = os.environ.get("POSTGRES_USER")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")
POSTGRES_DB = os.environ.get("POSTGRES_DB")
POSTGRES_HOST = os.environ.get("POSTGRES_HOST")
DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:5432/{POSTGRES_DB}"

# SQLAlchemy setup for audit logs
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True)
    role = Column(String)  # "user" or "assistant"
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

# Define Pydantic models for API
class ChatRequest(BaseModel):
    question: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    answer: str
    session_id: str

# Define a lifespan function for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create a persistent connection and set up the chat history table.
    app.state.sync_connection = psycopg.connect(DATABASE_URL)
    table_name = "langchain_chat_history"
    PostgresChatMessageHistory.create_tables(app.state.sync_connection, table_name)
    yield
    # Shutdown: Close the connection
    app.state.sync_connection.close()


app = FastAPI(title="Legal Advisor Chatbot", lifespan=lifespan)


def get_session_history(session_id: str) -> PostgresChatMessageHistory:
    table_name = "langchain_chat_history"
    return PostgresChatMessageHistory(table_name, session_id, sync_connection=app.state.sync_connection)


def get_history_from_config(config):
    if isinstance(config, dict):
        session_id = config.get("configurable", {}).get("session_id", "default_session")
    else:
        session_id = config
    return get_session_history(session_id)

# Define the prompt template with a system message.
prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(
        "You are a helpful, professional legal advisor. You only answer questions strictly related to legal matters. "
        "If a user asks about anything outside the scope of legal topics, kindly respond that you are only able to "
        "assist with legal inquiries. Always provide accurate and ethical information within legal boundaries."
    ),
    HumanMessagePromptTemplate.from_template("{input}")
])

# Compose the chain and wrap it with RunnableWithMessageHistory.
chat_model = ChatOpenAI(temperature=0.5)
chain = prompt | chat_model

runnable = RunnableWithMessageHistory(
    chain,
    get_session_history=get_history_from_config
)

# API Endpoints
@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    session_id = request.session_id or "default_session"
    user_question = request.question

    try:
        response = runnable.invoke(
            {"input": user_question},
            config={"configurable": {"session_id": session_id}}
        )

        if isinstance(response, dict) and "output" in response:
            ai_response = response["output"]
        else:
            ai_response = response

        if hasattr(ai_response, "content"):
            ai_response = ai_response.content

        # Save messages to your SQLAlchemy audit log
        db_session = SessionLocal()
        db_session.add_all([
            Message(session_id=session_id, role="user", content=user_question),
            Message(session_id=session_id, role="assistant", content=ai_response)
        ])
        db_session.commit()
        db_session.close()

        return ChatResponse(answer=ai_response, session_id=session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/chat-history", response_model=List[str])
def get_chat_history_endpoint(session_id: str):
    db_session = SessionLocal()
    try:
        rows = db_session.query(Message).filter(Message.session_id == session_id).order_by(Message.id.asc()).all()
        return [f"{row.role}: {row.content}" for row in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db_session.close()
