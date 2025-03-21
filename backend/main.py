import os
import traceback
from datetime import datetime

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

# SQLAlchemy imports
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base

# LangChain imports
from langchain_openai import ChatOpenAI
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate
)

from dotenv import load_dotenv
load_dotenv()


# Environment and DB Setup --------------------------------------------------------------------------------------------

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("Missing OPENAI_API_KEY!")

POSTGRES_USER = os.environ.get("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "postgres")
POSTGRES_DB = os.environ.get("POSTGRES_DB", "legal_advisor_db")
DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@db:5432/{POSTGRES_DB}"

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

# FastAPI Setup -------------------------------------------------------------------------------------------------------
app = FastAPI(title="Legal Advisor Chatbot")

class ChatRequest(BaseModel):
    question: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    answer: str
    session_id: str


# In-Memory Chat History Store ----------------------------------------------------------------------------------------

session_store = {}

def get_session_history(session_id: str) -> InMemoryChatMessageHistory:
    if session_id not in session_store:
        session_store[session_id] = InMemoryChatMessageHistory()
    return session_store[session_id]


# Helper to Retrieve Session History ----------------------------------------------------------------------------------

def get_history_from_config(config):
    # If config is a dict, extract session_id from it.
    if isinstance(config, dict):
        session_id = config.get("configurable", {}).get("session_id", "default_session")
    else:
        session_id = config
    return get_session_history(session_id)


# Define the Prompt Template with a System Message --------------------------------------------------------------------

prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(
        "You are a helpful legal advisor. Provide accurate and ethical legal advice. Only answer questions related \
        to legal matters."
    ),
    HumanMessagePromptTemplate.from_template("{input}")
])


# Compose the Chain and Wrap with RunnableWithMessageHistory ----------------------------------------------------------

chat_model = ChatOpenAI(temperature=0.5)
chain = prompt | chat_model

runnable = RunnableWithMessageHistory(
    chain,
    get_session_history=get_history_from_config
)


# API Endpoints -------------------------------------------------------------------------------------------------------

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

        db_session = SessionLocal()
        db_session.add_all([
            Message(session_id=session_id, role="user", content=user_question),
            Message(session_id=session_id, role="assistant", content=ai_response)
        ])
        db_session.commit()
        db_session.close()

        return ChatResponse(answer=ai_response, session_id=session_id)
    except Exception as e:
        traceback.print_exc()
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
