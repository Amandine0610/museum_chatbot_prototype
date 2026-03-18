# Rwanda Museum Interactive Guide — Multilingual AI Chatbot

**Capstone Project** | BSc. Software Engineering | Amandine Irakoze | Supervisor: Thadee Gatera

A culturally contextualised, machine-learning-driven chatbot using **Retrieval-Augmented Generation (RAG)** to provide interactive, multilingual cultural storytelling in **Kinyarwanda, English, and French** for Rwandan museums.

---

## Live Application

**[https://rwanda-museums-chatbot.vercel.app/](https://rwanda-museums-chatbot.vercel.app/)**

Visitors scan a museum-specific QR code which opens the chatbot pre-loaded with that museum's knowledge base, serving as an interactive digital guide.

---

## Supported Museums

| ID | Museum |
|---|---|
| 1 | King's Palace Museum (Nyanza) |
| 2 | Ethnographic Museum (Huye) |
| 3 | Museum Ingabo (Kigali) |
| 4 | Campaign Against Genocide Museum |
| 5 | Kandt House Museum |
| 6 | Environment Museum (Karongi) |
| 7 | Kigali Genocide Memorial |
| 8 | Rwanda Art Museum |

---

## System Architecture

```
Visitor scans QR code
        |
        v
React/Vite PWA (Vercel)        <-- frontend/
        |  HTTPS POST /api/chat
        v
Python/Flask Backend (Railway) <-- app.py
        |
        +---> ChromaDB (vector store)
        |         |-- Semantic similarity search
        |         |-- 8 museum knowledge bases indexed
        |
        +---> Google Gemini REST API
                  |-- gemini-2.0-flash-lite (primary)
                  |-- Smart local fallback if quota exceeded
```

---

## Technology Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, Vite, TailwindCSS, Axios, Framer Motion |
| Backend | Python 3.11, Flask, Flask-CORS, Gunicorn |
| Vector Store | ChromaDB (ONNX-based DefaultEmbeddingFunction) |
| LLM | Google Gemini REST API (gemini-2.0-flash-lite) |
| Frontend Hosting | Vercel |
| Backend Hosting | Railway |

---

## Local Development Setup

### Prerequisites
- Python 3.11+
- Node.js 18+

### 1. Clone the repository
```bash
git clone https://github.com/Amandine0610/museum_chatbot_prototype.git
cd museum_chatbot_prototype
```

### 2. Backend (Python/Flask)
```bash
# From the project root
pip install -r requirements.txt

# Create ml-service/.env with your Google API key:
# GOOGLE_API_KEY=your_key_here

python app.py
# Backend runs on http://localhost:8000
```

### 3. Frontend (React/Vite)
```bash
cd frontend
npm install
npm run dev
# Frontend runs on http://localhost:5173
```

The Vite dev server proxies `/api` requests to `http://localhost:8000` automatically.

---

## Environment Variables

| Variable | Where | Description |
|---|---|---|
| `GOOGLE_API_KEY` | Backend (Railway / `.env`) | Google Gemini API key |
| `VITE_API_URL` | Frontend (Vercel) | Backend URL (e.g. `https://your-app.railway.app`) |

---

## Testing Results

### Functional Testing

| Museum | Query | Result |
|---|---|---|
| Ethnographic (Huye) | "What does the zigzag mean?" | "Two women holding hands" |
| King's Palace (Nyanza) | "Why are Inyambo special?" | Royal cattle with long horns |
| Museum Ingabo | "Explain Inzira y'Inzitane" | 30-year reconstruction journey |
| Campaign Museum | "What happened at CND in 1994?" | Siege and RPA rescue mission |
| Rwanda Art Museum | "Who originated Imigongo?" | Prince Kakira of Gisaka |

### RAG & Hallucination Suppression

| Metric | Result |
|---|---|
| Factual accuracy (valid queries) | 97.1% |
| Hallucination rejection (out-of-scope) | 100% |

### Multilingual Intent Recognition (F1-Score)

| Language | Precision | Recall | F1 |
|---|---|---|---|
| English | 0.93 | 0.91 | 0.92 |
| French | 0.91 | 0.88 | 0.89 |
| Kinyarwanda | 0.84 | 0.82 | 0.83 |

### System Response Latency

| Mode | Latency |
|---|---|
| Gemini generative (warm) | ~1750ms |
| Cold-start | ~4600ms |
| Local RAG fallback (ChromaDB) | ~85ms |

---

## Project Structure

```
rwanda_museums_chatbot/
├── app.py                  # Flask backend — RAG pipeline, Gemini API, ChromaDB
├── requirements.txt        # Python dependencies
├── Procfile                # Railway deployment process
├── runtime.txt             # Python version for Railway
├── knowledge_base/         # Museum knowledge base (.txt files, one per museum)
├── frontend/               # React/Vite PWA
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/
│   │   │   ├── ArtifactDetail.jsx   # Main chat interface
│   │   │   └── LanguageSelector.jsx # Multilingual onboarding
│   │   └── data/
│   │       └── museums.js           # Museum metadata
│   └── index.html
└── charts/                 # Generated result charts (report figures)
```

---

## Key Features

- **Multilingual**: Full support for Kinyarwanda, English, and French with language-specific system prompts
- **RAG-powered**: ChromaDB vector store with semantic similarity search, bounded to verified museum archives
- **Hallucination-resistant**: LLM responses strictly constrained to knowledge base context; graceful fallback when information is unavailable
- **QR code integration**: Each museum has a unique URL parameter (`?museumId=N&lang=en`) — scan a QR code to open the correct museum chatbot instantly
- **Progressive Web App**: Mobile-first design, installable on Android/iOS via "Add to Home Screen"
- **Smart fallback**: If Gemini API is rate-limited, the system falls back to direct ChromaDB passage retrieval (~85ms)

---

## Future Work

- Kinyarwanda Text-to-Speech (TTS) for oral storytelling tradition
- Augmented Reality (AR) overlays for artefact visualisation
- Offline edge deployment using Ollama + LLaMA-3 for museum-hosted servers
- Expanded Kinyarwanda NLP training corpus in partnership with Rwandan linguists

---

*This project was developed as a BSc. Software Engineering Capstone at African Leadership University (ALU).*
