# Legal Advisor Chatbot 🧑‍⚖️🤖

A conversational legal advisor chatbot that uses OpenAI's LLMs to provide accurate and ethical legal information.  
It uses **FastAPI** as the backend, **Streamlit** as the frontend, **PostgreSQL** to store chat history, and **LangChain** for prompt templates and conversation memory.

---

## ✅ Features

- 🔍 **Legal-focused AI assistant** – only answers legal questions
- 💬 **Chat history memory** – supports session-based follow-ups
- 🧠 **LangChain integration** – templates and memory management
- 🗃 **PostgreSQL** – stores all messages for audit and review
- 🚀 **Dockerized stack** – run everything with one command
- ⚡ **Streamlit UI** – lightweight chat interface

---

## 🗂 Project Structure

```
legal-advisor-chatbot/
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
└── README.md                  # You're reading it
```

---

## ⚙️ Local Setup (with Docker)

This is the **recommended** way to run the project.

### 1. Install dependencies

- [Docker Desktop](https://www.docker.com/products/docker-desktop)
- (Optional) [Git](https://git-scm.com/)

### 2. Clone the repository

```bash
git clone https://github.com/yourusername/legal-advisor-chatbot.git
cd legal-advisor-chatbot
```

### 3. Create your `.env` file

```bash
cp .env.example .env
```

Edit `.env` and fill in your real OpenAI API key.

### 4. Start all services

```bash
docker-compose up --build
```

- **Backend API**: http://localhost:8000  
- **Streamlit UI**: http://localhost:8501  
- **PostgreSQL**: exposed internally as `db:5432`

---

## 🧪 Local Setup (Without Docker)

Useful for debugging or development if you don't want Docker.

### Backend (FastAPI)

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend (Streamlit)

In another terminal:

```bash
cd frontend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Make sure your `.env` file exists and is loaded in both.

---

## 🔐 Environment Variables

The `.env` file must include the following:

| Variable            | Description                               |
|---------------------|-------------------------------------------|
| `OPENAI_API_KEY`    | Your OpenAI API Key                       |
| `POSTGRES_USER`     | Username for PostgreSQL                   |
| `POSTGRES_PASSWORD` | Password for PostgreSQL                   |
| `POSTGRES_DB`       | PostgreSQL database name                  |
| `FASTAPI_URL`       | Backend URL for the Streamlit frontend    |

Example values are included in `.env.example`.

---

## 🧠 LangChain Prompt

The chatbot uses this system prompt to control behavior:

> You are a helpful, professional legal advisor. You only answer questions strictly related to legal matters. If a user asks about anything outside the scope of legal topics, kindly respond that you are only able to assist with legal inquiries.

It ensures the assistant stays on topic and avoids misuse.

---

## 🧪 API Reference

FastAPI Swagger UI is available at:  
[http://localhost:8000/docs](http://localhost:8000/docs)

### `POST /chat`

- Request: `{ "question": "Can I sue for breach of contract?", "session_id": "abc123" }`
- Response: `{ "answer": "...", "session_id": "abc123" }`

### `GET /chat-history?session_id=abc123`

Returns an array of messages for a session.

---

## 🐞 Troubleshooting

- Streamlit shows connection error → check if backend is running
- Missing `.env` values → copy from `.env.example`
- Docker issue → run `docker-compose down -v` to reset containers and volumes

---

## 📋 Commit Messages

Follow this format:
- `Add Streamlit chat interface`
- `Implement LangChain memory and prompt logic`
- `Connect PostgreSQL and save chat history`
- `Configure Docker Compose with three services`

---

## 🧾 License

MIT – free for personal and commercial use.

---

## ✨ Author

Made with ❤️ by [Your Name] using Python, FastAPI, LangChain, and Streamlit.