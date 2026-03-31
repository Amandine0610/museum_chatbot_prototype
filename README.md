# Rwanda Museum Interactive Guide — Multilingual RAG Chatbot

**Capstone Project** | BSc. Software Engineering | Amandine Irakoze | Supervisor: Thadee Gatera

This repository implements a **Retrieval-Augmented Generation (RAG)** system: a **Flask** backend embeds and indexes curated museum text in **ChromaDB**, retrieves relevant chunks for each visitor question, and optionally calls **Google Gemini** to generate answers **grounded in those chunks**. A **React (Vite)** web app is the visitor-facing interface (language selection, chat, EULA, QR entry). **The machine-learning core is the retrieval + generation pipeline in `app.py`**, not the UI alone.

**Live app:** [https://rwanda-museums-chatbot.vercel.app/](https://rwanda-museums-chatbot.vercel.app/)

**Repository:** [https://github.com/Amandine0610/Rwanda_museums_chatbot](https://github.com/Amandine0610/Rwanda_museums_chatbot)

---

## 1. ML / RAG pipeline (backend)

| Stage | What happens |
|--------|----------------|
| **Corpus** | Eight plain-text files in `knowledge_base/` (one per museum), edited from official-style descriptions. |
| **Indexing** | On first use (or empty collection), chunks are embedded with Chroma’s **DefaultEmbeddingFunction** (ONNX; no separate PyTorch sentence-transformers server required in production). |
| **Storage** | **ChromaDB** persistent store under `chroma_db/` (local; excluded from git — rebuilt on deploy or copied from backup). |
| **Retrieval** | Query embedding + similarity search; results can be **museum-scoped** (`museumId`). Distance used for **relevance / out-of-scope** behaviour. |
| **Generation** | **Gemini** (REST) receives retrieved passages + strict language and “use only context” style instructions. |
| **Curated layer** | **`CORE_FACTS` in `app.py`**: keyword-triggered, **hand-written** answers in EN/FR/RW for frequent intents (hours, location, fees, etc.) — no LLM call for those paths. |
| **Fallback** | If Gemini is unavailable or rate-limited, **sentence extraction from retrieved chunks** (`smart_fallback`) still returns text from the archive. |

The web app only sends `query`, `language`, and `museumId` to `/api/chat`; all steps above run on the server.

---

## 2. Design choices and alternatives (summary for the report)

| Decision | Rationale (short) | Alternatives not used here |
|----------|-------------------|-----------------------------|
| **RAG vs fine-tuning** | Museum text changes; RAG updates by editing files and re-indexing without retraining a large model. | Full fine-tune on a small corpus risks overfitting and stale weights. |
| **ChromaDB + default embeddings** | Simple Python integration, persistent store, ONNX embeddings suitable for Railway resource limits. | Pinecone/Weaviate (managed), or self-hosted Qdrant; heavier embedding models (e.g. larger ST models) need more RAM/CPU. |
| **Gemini (API)** | Strong multilingual generation; free tier usable for prototyping; single HTTP API from Flask. | OpenAI API, Anthropic, or **local** LLMs (Ollama, Llama) — add ops cost or hosting complexity. |
| **Curated `CORE_FACTS`** | Stable answers for high-traffic intents; reduces reliance on the LLM for simple facts. | Pure LLM-only — higher variance and cost. |

A fuller comparison and literature review belong in the **final PDF report** (see panel feedback below).

---

## 3. Data scope and limitations (evaluation / generalization)

- The knowledge base is **small** relative to national-scale or “all visitors” populations: eight museum-specific `.txt` files, not a massive crawl or official digitized archive dump.
- **Results must not be generalized** to all Rwandan museum visitors or all cultural institutions without a **larger, representative study** (more queries, blind scoring, external annotators, longitudinal use).
- **Hallucination:** RAG and prompts **reduce** unsupported answers; they do **not** prove **100%** hallucination elimination. The EULA states that answers are assistive and may be incomplete.
- **“Factual accuracy” percentages** in early documentation should be read as **pilot / limited-sample** evaluations tied to a defined protocol in the **capstone report**, not as population-level statistics. This README does **not** repeat headline percentages; see the **signed final PDF** for revised wording after panel feedback.

---

## 4. Reproducible evaluation in this repo

**Intent / routing check** (curated keyword paths, not full answer correctness):

```bash
# From repository root, after pip install -r requirements.txt
python scripts/evaluation/evaluate_intent.py
```

Uses `scripts/evaluation/intent_test_set.csv` (multilingual rows) and `get_core_fact_route_key` in `app.py`. Optional: `pip install scikit-learn` for a printed classification report.

**What this does *not* measure:** end-to-end factual correctness of every Gemini answer, user engagement, or “hallucination rate” at scale — those require a separate protocol (golden Q&A set, human judges, larger N).

---

## 5. Supported museums

| ID | Museum |
|---:|---|
| 1 | King's Palace Museum (Nyanza) |
| 2 | Ethnographic Museum (Huye) |
| 3 | Museum Ingabo (Kigali) |
| 4 | Campaign Against Genocide Museum |
| 5 | Kandt House Museum |
| 6 | Environment Museum (Karongi) |
| 7 | Kigali Genocide Memorial |
| 8 | Rwanda Art Museum |

---

## 6. Architecture (high level)

```
Visitor (browser)
       |
       v
React/Vite (Vercel)  --POST /api/chat-->  Flask app (Railway): app.py
                                                |
                        +-----------------------+-----------------------+
                        |                       |                       |
                        v                       v                       v
                 ChromaDB retrieve      CORE_FACTS match?        Gemini REST
                 (museum-scoped)         (hours, location…)      (grounded prompt)
                        |                       |                       |
                        +-----------------------+-------+---------------+
                                                        v
                                                 JSON response text
```

---

## 7. Technology stack

| Layer | Technology |
|-------|------------|
| Frontend | React 18, Vite, TailwindCSS (light/dark), Axios |
| Backend | Python 3.11, Flask, Flask-CORS, Gunicorn |
| Vector store | ChromaDB, DefaultEmbeddingFunction (ONNX) |
| LLM | Google Gemini (REST; model list and fallbacks in `app.py`) |
| Hosting | Vercel (frontend), Railway (backend) |

---

## 8. Local installation and running

### Prerequisites

- **Python 3.11+**
- **Node.js 18+**
- A **Google AI (Gemini) API key** for full generative behaviour (optional for testing retrieval-only paths)

### 8.1 Clone

```bash
git clone https://github.com/Amandine0610/Rwanda_museums_chatbot.git
cd Rwanda_museums_chatbot
```

### 8.2 Backend

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate

pip install -r requirements.txt
```

**Environment variables** (pick one approach):

- **`ml-service/.env`** — `GOOGLE_API_KEY=...` (loaded first if present), or  
- **Project root `.env`** — same variable (also loaded; see `app.py`).

```bash
python app.py
```

Default Flask URL is typically **http://127.0.0.1:8000** (confirm in console). First run may **index** `knowledge_base/` into `chroma_db/` (can take several minutes).

### 8.3 Frontend

```bash
cd frontend
npm install
```

Create **`frontend/.env`** for local API calls (see `frontend/.env.example`):

```env
VITE_API_URL=http://127.0.0.1:8000
```

```bash
npm run dev
```

Open the printed URL (often **http://localhost:5173**). Ensure CORS allows your frontend origin (already relaxed for `/api/*` in `app.py` for development).

### 8.4 Admin QR page

Open `http://localhost:5173/?admin=qr` to print/test per-museum URLs.

### 8.5 Troubleshooting

| Issue | Check |
|-------|--------|
| `Gemini API key missing` | `GOOGLE_API_KEY` or `GEMINI_API_KEY` set on **Railway** or in local `.env`; redeploy after changing Railway vars. |
| Empty or slow first chat | Chroma indexing; disk space; Railway cold start. |
| CORS errors | Backend URL in `VITE_API_URL` must match Flask origin scheme/host. |

---

## 9. Environment variables

| Variable | Where | Purpose |
|----------|--------|---------|
| `GOOGLE_API_KEY` or `GEMINI_API_KEY` | Railway / local `.env` | Gemini API |
| `VITE_API_URL` | Vercel / `frontend/.env` | Public backend base URL (no trailing slash on path) |

Never commit real keys. `.env` files are gitignored.

---

## 10. Project structure

```
Rwanda_museums_chatbot/
├── app.py                      # Flask, RAG, Chroma, Gemini, CORE_FACTS, /api/chat
├── requirements.txt
├── Procfile                    # Railway / process entry
├── runtime.txt                 # Python version pin
├── railway.toml
├── knowledge_base/             # Museum .txt corpora (source for RAG)
├── chroma_db/                  # Local vector store (gitignored)
├── scripts/
│   └── evaluation/             # Intent routing CSV + evaluate_intent.py
├── frontend/                   # React visitor UI
│   ├── .env.example
│   ├── vite.config.js
│   └── src/
├── docs/                       # Capstone supporting docs (figures, notebooks)
├── ml-service/                 # Optional alternate RAG service (not required for main app.py path)
└── backend/                    # Legacy Node Express stub (not the deployed Flask API)
```

---

## 11. Features (accurate wording)

- **Multilingual UI** (EN / FR / RW) and **language-conditioned** prompts and `CORE_FACTS`.
- **RAG** with **museum-scoped** retrieval where configured.
- **Grounding and guards** to align answers with retrieved text and deflect clear off-topic input; **not** a proof of zero hallucination.
- **QR / `museumId`** deep links for per-museum context.
- **EULA** with localStorage consent; mentions third-party (Gemini) processing.
- **Dark mode** (persisted preference).

---

## 12. Response to defense panel feedback (for LMS comment + report)

Use this as a checklist when you write the **course “comment section”** and the **report revision**; align the **PDF** with APA (≥25 sources recommended by panel, formatting, references).

| Panel concern | How addressed |
|---------------|----------------|
| ML aspects under-emphasised vs web app | Report and this README foreground **RAG, Chroma, embeddings, Gemini, CORE_FACTS**, and the **pipeline in `app.py`**. |
| Repo still showed old headline metrics | **`docs/capstone_system_report.md`**, **`generate_charts.py`**, and **`generate_slides.py`** are aligned with cautious wording; edit chart constants to match your signed PDF if you regenerate figures. |
| Small data / no large-population claims | **Section 3** states limits; report should add explicit **generalizability** and **sample size** discussion. |
| Scant literature | Expand report references to **≥25** peer-reviewed and grey sources (RAG, museum tech, multilingual NLP, evaluation). **APA 7** in-text and reference list. |
| Limited evaluation / overstated metrics | Remove or **rephrase** headline percentages; tie any number to **N, protocol, and limits**; add **intent script** as reproducible artefact; plan **larger human-evaluated set** as future work. |
| “100% hallucination rejection” / engagement claims | **Dropped from README**; report should use **careful** language (reduction, not elimination; engagement only with **measured** definition). |
| Model / architecture justification | **Section 2** + expanded **report** subsection comparing **alternatives**. |
| Document formatting | **Final PDF:** title page **unnumbered**; **roman** preliminary pages vs **arabic** main body; **each chapter new page**; **student + supervisor signatures**; clear **diagrams** with captions. |
| Repo + README for moderators | This file + clone URL + install steps above. |

---

## 13. Future work (aligned with panel)

- Larger **annotated** Q&A set and **inter-rater** factual scoring.
- Ablation or comparison: **embedding model** / **chunk size** / **top-k** / optional **LLM** swap.
- More **literature-backed** evaluation metrics (e.g. faithfulness to context) with reported confidence intervals.
- Optional **local LLM** path for offline or data-sovereignty scenarios.

---

## 14. Academic integrity

This project was developed as a BSc. Software Engineering Capstone at **African Leadership University (ALU)**. The **authoritative narrative, citations, figures, and signed approval** are in the **submitted PDF**, not only in this README.

---

## 15. Final submission checklist (course upload)

Use this when submitting the **Mission Capstone — Final Submission** (PDF + LMS fields):

| Item | Action |
|------|--------|
| **PDF** | One file: signed report (student + supervisor), APA 7, panel feedback incorporated, repo link on references/title page as required. |
| **LMS comment** | Summarise panel feedback and how the PDF was revised (see §12 table for talking points). |
| **Repository** | Public: `https://github.com/Amandine0610/Rwanda_museums_chatbot` — moderators clone and follow **§8** (backend + frontend + env vars). |
| **Live demo** | `https://rwanda-museums-chatbot.vercel.app/` (optional to mention in PDF/README). |
| **Secrets** | Never commit `.env`; set `GOOGLE_API_KEY` on Railway for production API. |

**Git history note:** This repository may use a **single squashed commit** titled `updated` so all visible commit messages match that label; full development history is not preserved on `main`.

---

*Supervisor: Thadee Gatera — final report must bear student and supervisor signatures per course rubric.*
