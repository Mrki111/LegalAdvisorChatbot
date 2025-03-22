import uuid
import streamlit as st
import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Title for the chat application
st.title("Legal Advisor Chatbot")


# Initialize session state for messages if not already present
if "messages" not in st.session_state:
    st.session_state["messages"] = []


FASTAPI_URL = os.getenv("FASTAPI_URL")
session_id = str(uuid.uuid4())

# Send the user's question to the backend and return the AI response.
def send_question(question: str):

    endpoint = f"{FASTAPI_URL}/chat"
    payload = {"question": question, "session_id": session_id}
    try:
        response = requests.post(endpoint, json=payload)
        response.raise_for_status()
        data = response.json()
        return data.get("answer")
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None


# Chat interface layout
st.markdown("Ask a legal question")
question_input = st.text_input("Enter your question here:")
if st.button("Send"):
    if question_input.strip():

        st.session_state["messages"].append(("user", question_input))
        answer = send_question(question_input)
        if answer:
            st.session_state["messages"].append(("assistant", answer))



# Display the conversation history with simple styling
st.markdown("Conversation History")
for role, message in st.session_state["messages"]:
    if role == "user":

        st.markdown(
            f"<p style='text-align: right; color: blue; font-weight: bold;'>You: {message}</p>",
            unsafe_allow_html=True,
        )
    else:

        st.markdown(
            f"<p style='text-align: left; color: green; font-weight: bold;'>AI Advisor: {message}</p>",
            unsafe_allow_html=True,
        )
