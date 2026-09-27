# Atlas — AI Learning Researcher & Practice Engine

Atlas is an agentic, AI-powered learning and practice platform built with **LangGraph**, **Gemini LLM**, **FAISS vector search**, and **RAG (Retrieval-Augmented Generation)**. It empowers learners to ask conceptual questions, explore PDF documents, take grounded practice quizzes, and receive performance diagnostics.

---

## 🌟 Key Features

### 1. 📖 Interactive Learn Mode (Grounded RAG Chat)
- Chat with Atlas using either the **built-in Knowledge Base (`ML_Textbook.pdf`)** or **user-uploaded PDF documents**.
- Contextual retrieval using FAISS vector search and MiniLM embeddings ensures accurate, grounded answers with citations.

### 2. ⚡ Practice Engine (Adaptive Evaluation)
- **MCQ Mode (5 Questions)**: Generates 5 multiple choice questions grounded in the selected PDF context, featuring selectable option cards (A, B, C, D).
- **Typed Answer Mode (2 Questions)**: Generates 2 deep conceptual questions for typed responses.
- **Dynamic Performance Diagnostic**:
  - **Score**: Integer score from **0 to 10 points** calculated dynamically per answer.
  - **Strengths (Concepts Mastered)**: Identifies specific concepts answered correctly.
  - **Weaknesses (Concepts to Review)**: Highlights concepts requiring revision.
  - **Recommended Focus Topic**: Recommends the next study topic.

### 3. 📄 Document Management
- Upload custom PDF study materials directly from the Documents tab.
- Instant RAG indexing and clean document deletion with real-time FAISS index synchronization.

### 4. 📊 Study Dashboard
- Tracks questions asked, study sessions completed, uploaded documents, and learning history cleanly initialized per user account.

---

## 🏗️ System Architecture

Atlas operates on a multi-agent state graph built with **LangGraph**:

```mermaid
graph TD
    User([User Request]) --> Supervisor[Supervisor Agent]
    Supervisor -->|General / Conceptual| Tutor[Tutor Agent]
    Supervisor -->|PDF Query / Document RAG| Researcher[Researcher Agent (FAISS RAG)]
    Supervisor -->|Quiz Request / Practice Mode| Evaluator[Evaluator Agent]
    Evaluator -->|Submit Answers| Memory[Memory Node]
    Researcher --> Response([Output Response])
    Tutor --> Response
    Evaluator --> Response
    Memory --> Response
```

- **Supervisor Agent**: Intelligently routes queries to the appropriate specialized node.
- **Tutor Agent**: Teaches foundational and advanced concepts.
- **Researcher Agent**: Performs PDF text extraction, chunking, MiniLM vector embedding, and FAISS RAG search.
- **Evaluator Agent**: Generates grounded quizzes in JSON format and evaluates student answers strictly against accuracy standards.
- **Memory**: Persists user study results into memory.

---

## 📁 Directory Structure

```text
atlas/
├── server.py                   # Python HTTP & REST API server
├── backend/
│   ├── agents/
│   │   ├── graph.py            # LangGraph multi-agent orchestration workflow
│   │   ├── supervisor.py       # Intent router agent
│   │   ├── tutor.py            # Concept tutor agent
│   │   ├── researcher.py       # FAISS RAG & PDF vector search agent
│   │   ├── evaluator.py        # Quiz generator & answer evaluation agent
│   │   └── memory.py           # User learning memory storage
│   ├── knowledge_base/
│   │   └── ML_Textbook.pdf     # Built-in knowledge base
│   ├── user_documents/         # User uploaded PDFs directory
│   └── memory/
│       └── user_accounts.json  # User profiles & question history database
└── frontend/
    ├── index.html              # Single Page Application UI structure
    ├── style.css               # Modern dark-mode styling system
    └── app.js                 # Dynamic UI logic, chat handler, practice engine
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- Gemini API Key (`GEMINI_API_KEY` or `ATLAS_API_KEY`)

### Installation & Execution

1. **Activate Virtual Environment**:
   ```bash
   source venv/bin/activate
   ```

2. **Set Environment Variable**:
   ```bash
   export ATLAS_API_KEY="your-gemini-api-key"
   ```

3. **Start Server**:
   ```bash
   python server.py
   ```

4. **Access Web Application**:
   Open browser at `http://localhost:8000`.

---

## 📡 API Endpoints

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `POST /api/login` | `POST` | Authenticates user and loads user account data |
| `GET /api/stats` | `GET` | Fetches study sessions, document counts, and topics learned |
| `GET /api/documents` | `GET` | Returns list of user uploaded PDF documents |
| `POST /api/upload` | `POST` | Uploads PDF document and syncs RAG index |
| `POST /api/documents/delete` | `POST` | Deletes PDF file and updates RAG index |
| `POST /api/chat` | `POST` | Processes chat queries or practice quiz requests via Atlas agents |
| `GET /api/user/history` | `GET` | Returns user question history |
