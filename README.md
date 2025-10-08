# AI-Powered Personalized Quiz Generator

A **modular, RAG-based AI quiz system** built with FastAPI that:

* Generates **personalized quizzes** using LLMs (Ollama / LLaMA 3.2).
* Stores answers in a **vector database** (ChromaDB) for intelligent feedback.
* Provides **adaptive, personalized feedback** based on user responses and quiz context.
* Tracks **full quiz history** per user.
* Supports **JWT authentication** and Swagger/OpenAPI docs.

---

## 🔹 Features

| Feature                         | Description                                                              |
| ------------------------------- | ------------------------------------------------------------------------ |
| Personalized Quiz Generation    | Generates quizzes based on user profile (age, hobbies, education, etc.)  |
| Answer Embedding & Vector Store | Stores answers in ChromaDB for similarity searches and adaptive feedback |
| Feedback Engine                 | Provides personalized feedback and follow-up suggestions using LLMs      |
| History Tracking                | Tracks past quizzes, responses, and feedback per user                    |
| JWT Authentication              | Secures endpoints and user data                                          |
| Swagger/OpenAPI                 | Interactive API docs at `/docs`                                          |
| Modular Architecture            | Easy to extend with microservices in future                              |

---

##  Tech Stack

| Layer               | Technology                              |
| ------------------- | --------------------------------------- |
| API Backend         | FastAPI                                 |
| LLM Integration     | Ollama / LLaMA 3.2                      |
| Vector Store        | ChromaDB (or FAISS, Qdrant, Weaviate)   |
| Embedding Model     | SentenceTransformers |
| SQL Database        | PostgreSQL        |
| Auth                | JWT via `fastapi-jwt-auth`              |
| Docs                | Swagger/OpenAPI                         |

---

##  Project Structure

```
quizgen-backend/
│
├── app/
│   ├── main.py
│   ├── api/
│   │   ├── auth/
│   │   ├── quiz/
│   │   ├── feedback/
│   │   └── history/
│   ├── core/
│   ├── db/
│   │   ├── base.py
│   │   ├── models/
│   │   └── repositories/
│   ├── services/
│   └── vectorDB/
├── requirements.txt or pyproject.toml
├── Dockerfile
├── .env
└── alembic/
```

---

## Setup Instructions

### 1️ Clone Repository

```bash
https://github.com/shubham3451/AI-Quiz-Generator.git
cd AI-Quiz-Generator
```

### 2️ Create Virtual Environment if using pip

```bash
python -m venv .venv
```

**Activate it:**

* **Windows (PowerShell):**

```powershell
.venv\Scripts\Activate.ps1
```

* **Mac/Linux:**

```bash
source .venv/bin/activate
```

---

### 3️ Install Dependencies

If using **uv package manager**:

```bash
uv install
```

If using **pip**:

```bash
pip install -r requirements.txt
```

---

### 4️ Configure Environment Variables

Create a `.env` file in the root:

```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/dbname
JWT_SECRET=jwt_secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
LLM_BASE_URL=http://localhost:11434/api/generate
MODEL=LLAMA

```

* `DATABASE_URL` – your database (PostgreSQL).
* `JWT_SECRET` – secret key for signing JWTs.
* `LLM_URL` – URL of your LLM server (Ollama/LLaMA).

---

### 5️ Run Alembic Migrations

```bash
uv run alembic upgrade head
```

---

### 6️⃣ Start the FastAPI Server

```bash
uv run uvicorn app.main:app --reload
```

* Default URL: `http://127.0.0.1:8000`
* Swagger docs: `http://127.0.0.1:8000/docs`

---

### 7️ Start LLM Server

* Make sure your **LLaMA/Ollama model** is running on `LLM_URL`.
* Example:

```bash
ollama serve --model llama3
```

---

## 🔑 Usage

### Register a User

```http
POST /auth/register
{
  "email": "user@example.com",
  "password": "secret123"
}
```
![Register User Screenshot](images/register.jpg)

### Login to get JWT

```http
POST /auth/login
{
  "email": "user@example.com",
  "password": "secret123"
}
```
![Login and get JWT User Screenshot](images/login.jpg)

### Generate a Quiz

```http
POST /generate-quiz
Headers: Authorization: Bearer <JWT>
{
  "name": "firstname lastname",
  "age": 30,
  "gender": "Male",
  "education": "Bachelor's in Computer Science",
  "city": "New Delhi",
  "hobbies": [
    "reading",
    "gaming",
    "cycling"
  ],
  "bio": "A software engineer who loves hiking and coffee."
}
```
![generate quiz](images/quizgenerate.jpg)
![generate quiz](images/quizgenerate2.jpg)
### Submit Quiz Responses

```http
POST /submit-responses
Headers: Authorization: Bearer <JWT>
{
  "quiz_id": "string",
  "responses": [
    {
      "question_id": "string",
      "answer_text": "string",
    }
  ]
}
```
![submit responses Screenshot](images/submitresponses.jpg)
![submit responses Screenshot](images/submitresponses2.jpg)

### Get Feedback

```http
GET /feedback?quiz_id=<quiz_id>&topic=Python
Headers: Authorization: Bearer <JWT>
```
![feedback Screenshot](images/feedback.jpg)
---

##  Notes

* Vector DB must be initialized and writable.
* LLM server must be running to generate quizzes and feedback.
* JWT is required for all protected endpoints.

---

