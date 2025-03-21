import traceback
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

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

def get_history_from_config(config):
    if isinstance(config, dict):
        session_id = config.get("configurable", {}).get("session_id", "default_session")
    else:
        session_id = config
    return get_session_history(session_id)


# Define the Prompt Template with a System Message --------------------------------------------------------------------

prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(
        "You are a helpful legal advisor. You provide accurate and ethical legal advice. Only answer questions related \
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


        return ChatResponse(answer=ai_response, session_id=session_id)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

