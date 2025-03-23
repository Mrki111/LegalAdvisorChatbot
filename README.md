# Legal Advisor Chatbot 🧑‍⚖️🤖

A conversational legal advisor chatbot built using OpenAI's LLMs to provide accurate and ethical legal information.

- **Backend**: FastAPI (with LangChain for prompt & memory)
- **Frontend**: Streamlit (lightweight UI)
- **Database**: PostgreSQL (stores all messages for audit and review)
- **Orchestration**: Docker Compose (optional, recommended)

---

## Table of Contents

1. [Overview & Architecture](#overview--architecture)  
2. [Approach to the Legal Advisor Context](#approach-to-the-legal-advisor-context)  
3. [Challenges & Solutions](#challenges--solutions)  
4. [Project Structure](#project-structure)  
5. [Setup & Usage](#setup--usage)  
   - [Using Docker (Recommended)](#1-using-docker-recommended)  
   - [Without Docker](#2-without-docker)  
6. [Running the Backend](#running-the-backend)  
7. [Running the Frontend](#running-the-frontend)  
8. [Environment Variables](#environment-variables)  
9. [LangChain Prompt & Memory](#langchain-prompt--memory)  
10. [API Reference](#api-reference)  
11. [License](#license)  
12. [Author](#author)

---

## Overview & Architecture

### High-Level Flow

1. The user interacts with a **Streamlit** frontend (chat interface).
2. Each query is sent to the **FastAPI** backend.
3. The backend uses **LangChain** to:
   - Format the prompt with a **legal advisor** system message.
   - Maintain **conversation memory** so the chatbot can reference previous messages in the session.
4. All messages (user & bot) are stored in **PostgreSQL** for auditing and legal compliance.
5. The backend responds to Streamlit with the chatbot’s answer.
6. The frontend displays the answer in the chat UI.

### Components

- **Frontend (Streamlit)**  
  Renders a chat interface, sends user queries to FastAPI, and displays responses.  

- **Backend (FastAPI + LangChain)**  
  - API endpoints for sending/receiving chat messages.  
  - Uses LangChain’s memory to handle session-based contexts.  
  - Persists chat logs to PostgreSQL.  

- **Database (PostgreSQL)**  
  Stores user messages and bot responses.  

- **Docker Compose**  
  Optionally runs all three components (frontend, backend, database) in separate containers, orchestrated via a single command.

---

## Approach to the Legal Advisor Context

1. **System Prompt**: A carefully crafted system message is used to instruct the model to respond only to legal inquiries and to politely decline any non-legal questions.
2. **Role-based Messages**: OpenAI’s chat format allows the chatbot to differentiate messages from the user, system, and the assistant. This is used to maintain a consistent, “professional legal advisor” tone.
3. **LangChain**:  
   - **Prompt Templates**: A strict template is defined to keep the chatbot within legal subjects.  
   - **Memory**: Conversation snippets are stored to ensure continuity; if the user references a previous question or context, the chatbot can recall that information accurately.

---

## Challenges & Solutions

1. **Maintaining Context**  
   - **Challenge**: Without a memory mechanism, the chatbot would forget prior user questions.  
   - **Solution**: LangChain’s conversation memory is used. All user and AI responses are kept in a short buffer so the chatbot sees recent dialogue.

2. **Storing Chat History Securely**  
   - **Challenge**: Chat logs must be stored but might contain sensitive data.  
   - **Solution**: Messages are stored in PostgreSQL with basic authentication.

3. **Deployment Complexity**  
   - **Challenge**: Coordinating backend, frontend, and database can be difficult.  
   - **Solution**: Docker Compose simplifies the setup and allows all components to run with a single command.

4. **Connection Management**  
   - **Challenge**: Creating a new psycopg connection for every call to `get_session_history` can work in a demo environment, but leads to performance issues under load.  
   - **Solution**: FastAPI's [lifespan](https://fastapi.tiangolo.com/advanced/events/#lifespan-function) function is used to create a persistent PostgreSQL connection at app startup, stored in `app.state.sync_connection`. This connection is reused in every chat session.

5. **Table Creation**  
   - **Challenge**: Creating the chat history table on every request wastes resources and could lead to race conditions.  
   - **Solution**: The required table schema is created once during the application's startup using `PostgresChatMessageHistory.create_tables()` inside the `lifespan` function. This ensures efficient resource usage and avoids redundant calls.
---

## Project Structure

```
LegalAdvisorChatbot/
├── backend/
│   ├── main.py                # FastAPI + LangChain logic
│   ├── Dockerfile             # Backend container
│   ├── requirements.txt       # Backend Python dependencies
├── frontend/
│   ├── app.py                 # Streamlit UI
│   ├── Dockerfile             # Frontend container
│   ├── requirements.txt       # Frontend Python dependencies
├── docker-compose.yml         # Orchestrates backend, frontend, db
├── .env.example               # Template for secrets/config
└── README.md                  # Documentation (this file)
```

---

## Setup & Usage

### 1) Using Docker (Recommended)

1. **Install Docker**  
   - [Docker Desktop](https://www.docker.com/products/docker-desktop)

2. **Clone the repository**:
   ```bash
   git clone https://github.com/Mrki111/LegalAdvisorChatbot.git
   cd LegalAdvisorChatbot
   ```

3. **Create `.env` from the example**:
   ```bash
   cp .env.example .env
   ```
   - Add to your `.env` file:
   ```
    OPENAI_API_KEY=Actual **OpenAI API key**  
    Database credentials for PostgreSQL: 
      - POSTGRES_USER=postgres        
      - POSTGRES_PASSWORD=postgres    
      - POSTGRES_DB=legal_advisor_db
      - POSTGRES_HOST=db
    FASTAPI_URL=http://backend:8000
   
4. **Run Docker Compose**:
   ```bash
   docker-compose up --build
   ```
   - Backend: [http://localhost:8000](http://localhost:8000)  
   - Frontend: [http://localhost:8501](http://localhost:8501)  
   - PostgreSQL: internally at `db:5432` (make sure the port is not being used by other applications)
---

### 2) Without Docker

#### A) Prerequisites

- Python 3.10+ (Do not use python 3.13!) 
- PostgreSQL installed locally or hosted  
- Git (optional)

#### B) Set up PostgreSQL
#### **Install PostgreSQL**

1. Download PostgreSQL installer from: [https://www.enterprisedb.com/downloads/postgres-postgresql-downloads](https://www.enterprisedb.com/downloads/postgres-postgresql-downloads)
2. Run the installer and follow the prompts:
   - Choose a password for the `postgres` superuser (you'll need it later)
   - Leave default port `5432`
   - Install optional components like pgAdmin if desired

#### Create a database

After installation, you can use **pgAdmin** (GUI) or **psql** (CLI).

##### Using `psql` (command line):
Use postgres superuser
```bash
psql -U postgres
```

Then inside the prompt:

```sql
CREATE DATABASE legal_advisor_db;
```
To exit:

```sql
\q
```
**Clone the repository**:
   ```bash
   git clone https://github.com/Mrki111/LegalAdvisorChatbot.git
   cd LegalAdvisorChatbot
   ```

#### C) Create `.env` file
```bash
cp .env.example .env
```
Add database credenitals:

```bash
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password # password for the postgres superuser
POSTGRES_DB=legal_advisor_db
POSTGRES_HOST=localhost
```
Add the FastAPI url:
```bash
FASTAPI_URL=http://localhost:8000
```
Add your OPENAI_API_KEY:
```bash
OPENAI_API_KEY=you_api_key_here
```






---

## Running the Backend

```bash
cd backend
python -m venv venv # or py -3.12 -m venv venv   
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
Test at [http://localhost:8000/docs](http://localhost:8000/docs)

---

## Running the Frontend

```bash
cd frontend
python -m venv venv # or py -3.12 -m venv venv   
source venv/bin/activate # or venv\Scripts\activate on Windows
pip install -r requirements.txt
streamlit run app.py
```

Visit [http://localhost:8501](http://localhost:8501) in your browser.

---

## Environment Variables

| Variable             | Description                                                  |
|----------------------|--------------------------------------------------------------|
| `OPENAI_API_KEY`     | OpenAI API Key                                               |
| `POSTGRES_USER`      | PostgreSQL username                                          |
| `POSTGRES_PASSWORD`  | PostgreSQL password                                          |
| `POSTGRES_DB`        | PostgreSQL database name                                     |
| `POSTGRES_HOST`      | PostgreSQL host                                              |
| `FASTAPI_URL`        | URL of the backend (e.g., `http://localhost:8000`)          |

---

## LangChain Prompt & Memory

Default system prompt:

> "You are a helpful, professional legal advisor. You only answer questions strictly related to legal matters. If a user asks about anything outside the scope of legal topics, politely respond that you are only able to assist with legal inquiries."

- Keeps responses on-topic.  
- Memory allows for recall of recent messages and more natural dialogue.

---

## API Reference

Auto-generated Swagger/OpenAPI docs: [http://localhost:8000/docs](http://localhost:8000/docs)

### `POST /chat`
```json
{
  "question": "Can I sue for breach of contract?",
  "session_id": "abc123"
}
```
**Response:**
```json
{
  "answer": "...",
  "session_id": "abc123"
}
```

### `GET /chat-history?session_id=abc123`
Returns all messages for a session. Useful for auditing or debugging.

---

## Author

Made by Lazar Mrkic using:
- Python, FastAPI, and LangChain for the backend  
- Streamlit for the frontend  
- PostgreSQL for data persistence  



