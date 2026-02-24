# 🏛️ Rwanda Museum Interactive Guide — Multilingual AI Chatbot

> **Capstone Project** | BSc. Software Engineering | Amandine Irakoze | Supervisor: Thadee Gatera

A culturally contextualised, machine-learning–driven chatbot utilising **Retrieval-Augmented Generation (RAG)** to provide interactive, multilingual cultural storytelling in **Kinyarwanda, English, and French** for Rwandan museums.

🔗 **Repository:** https://github.com/Amandine0610/museum_chatbot_prototype  

---

## 📸 Application Screens

| Language Selection | Artefact Detail | Chat Interface |
|---|---|---|
| Select from English / Français / Kinyarwanda | Browse artefacts with full descriptions | Ask questions in any language |

---

## 🏗️ System Architecture

```
┌─────────────────┐     HTTP      ┌─────────────────┐     HTTP     ┌──────────────────┐
│   Frontend      │ ──/api/chat──▶│   Backend       │ ──/query──▶  │   ML Service     │
│  React + Vite   │               │  Node / Express │              │  Python / Flask  │
│  Port 5173      │               │  Port 3000      │              │  Port 5000       │
└─────────────────┘               └─────────────────┘              └──────────────────┘
                                                                           │
                                                                    LangChain RAG
                                                                    ChromaDB + LLM
```

**Three-Tier Stack:**
- **Frontend:** ReactJS + Vite (Responsive mobile-first UI, phone-frame design)
- **Backend:** Node.js + Express (API Gateway / Proxy)
- **ML Service:** Python + LangChain + ChromaDB (RAG Pipeline)

---

## ⚙️ Prerequisites

| Tool | Version | Purpose |
|---|---|---|
| Node.js | v18+ | Frontend & Backend |
| Python | v3.9+ | ML Service |
| Git | any | Version control |

---

## 🚀 Installation & Running (Step-by-Step)

You need **3 terminal windows** open simultaneously.

### Step 1 — Clone the Repository
```bash
git clone https://github.com/Amandine0610/museum_chatbot_prototype.git
cd museum_chatbot_prototype
```

### Step 2 — ML Service (Terminal 1)
```bash
cd ml-service

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# (Optional) Add your OpenAI API key for live RAG responses
# Create a file called .env with: OPENAI_API_KEY=sk-...
# Without a key the app runs in Demo Mode

# Start the ML service
python app.py
```
✅ You should see: `Running on http://127.0.0.1:5000`

### Step 3 — Backend (Terminal 2)
```bash
cd backend

npm install

# Start the backend
npm start
```
✅ You should see: `Backend Server running on port 3000`

### Step 4 — Frontend (Terminal 3)
```bash
cd frontend

npm install

npm run dev
```
✅ You should see: `Local: http://localhost:5173/`

### Step 5 — Open the App
Open your browser and go to: **http://localhost:5173**

---

## 🧪 Running Tests

The ML service has a full test suite covering unit tests and API integration tests:

```bash
cd ml-service

# Activate the virtual environment first (see Step 2)
venv\Scripts\activate   # Windows
source venv/bin/activate  # Mac/Linux

# Run all tests
python test_rag_pipeline.py
```

**Test Coverage:**
| Test Class | Tests | What's Covered |
|---|---|---|
| `TestMockRAGPipeline` | 8 tests | RAG logic, multilingual queries (EN/FR/RW), response time |
| `TestFlaskAPI` | 5 tests | `/health` and `/query` endpoints, error handling, 400 responses |

---

## 🌍 Multilingual Support

The system supports three languages end-to-end:

| Language | UI Labels | Artefact Descriptions | Chat |
|---|---|---|---|
| 🇬🇧 English | ✅ | ✅ | ✅ |
| 🇫🇷 Français | ✅ | ✅ | ✅ |
| 🇷🇼 Kinyarwanda | ✅ | ✅ | ✅ |

---

## 🤖 AI / RAG Pipeline

The ML service uses a **Retrieval-Augmented Generation** pipeline:

1. **Ingestion:** Museum knowledge base (`museum_data.txt`) is loaded and split into chunks
2. **Embedding:** Text chunks are embedded using OpenAI embeddings and stored in ChromaDB
3. **Retrieval:** User queries retrieve the top-3 most relevant chunks semantically
4. **Generation:** A GPT-3.5-turbo LLM generates a culturally contextualised answer

> **Demo Mode:** If no `OPENAI_API_KEY` is set, the service runs in demo mode and returns informative placeholder responses. This allows the full UI to be demonstrated without an API key.

---

## 📁 Project Structure

```
museum_chatbot_prototype/
├── frontend/               # React + Vite UI
│   ├── src/
│   │   ├── components/
│   │   │   ├── LanguageSelector.jsx
│   │   │   └── ArtifactDetail.jsx
│   │   ├── translations.js      # EN / FR / RW strings
│   │   ├── App.jsx
│   │   └── main.jsx
│   └── public/artefacts/        # Artefact images go here
├── backend/                # Node.js Express API Gateway
│   └── server.js
├── ml-service/             # Python Flask RAG Service
│   ├── app.py
│   ├── rag_pipeline.py
│   ├── museum_data.txt         # Museum knowledge base
│   ├── requirements.txt
│   └── test_rag_pipeline.py    # Test suite
└── README.md
```

---

## 📊 Performance & Evaluation

| Metric | Result |
|---|---|
| API Response Time (Mock Mode) | < 100ms |
| API Response Time (Live RAG) | ~1.2s |
| Languages Supported | 3 (EN, FR, RW) |
| Artefacts in Knowledge Base | 2 (expandable) |
| Test Pass Rate | 13/13 (100%) |

---

## 🚢 Deployment Plan

| Component | Platform | Notes |
|---|---|---|
| Frontend | Vercel / Netlify | Auto-deploy from `main` branch |
| Backend | Render (Node.js) | Free tier, auto-sleep after inactivity |
| ML Service | Render (Python) | Requires `OPENAI_API_KEY` env var |

**Environment Variables needed on deployment:**
- `OPENAI_API_KEY` — for the ML Service
- `ML_SERVICE_URL` — Backend needs the deployed ML service URL

---

## 🔑 Key Technologies

`ReactJS` · `Vite` · `Python` · `Flask` · `LangChain` · `ChromaDB` · `OpenAI GPT-3.5` · `Node.js` · `Express` · `RAG` · `Kinyarwanda NLP`