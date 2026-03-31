# Capstone System Report: Multilingual RAG Museum Chatbot (repository notes)

> **Note:** The **signed PDF** submitted for grading is the authoritative version (APA formatting, ≥25 references, supervisor signature). This Markdown file is a **technical appendix** aligned with the **deployed codebase** and **defense panel feedback** (April 2025).

## 1. System overview

The **Rwanda Museum Interactive Guide** uses **Retrieval-Augmented Generation (RAG)** to answer visitor questions in **English, French, and Kinyarwanda**, grounded in **curated museum text files** and optional **Google Gemini** generation.

### 1.1 Architecture (as implemented in this repo)

1. **Presentation layer:** React (Vite) PWA — language selection, chat UI, EULA, QR deep links (`museumId`, `lang`).
2. **Application + ML layer:** **Python/Flask** (`app.py`) — HTTP API, ChromaDB retrieval, curated **`CORE_FACTS`**, Gemini REST calls, relevance / out-of-scope handling, fallbacks.

A separate **Node/Express** tree under `backend/` and optional **`ml-service/`** exist as prototypes; **production** described in the main **README** uses **`app.py`**.

---

## 2. RAG pipeline (summary)

- **Corpus:** `knowledge_base/*.txt` (one file per museum).
- **Vector store:** **ChromaDB** with **DefaultEmbeddingFunction** (ONNX embeddings in the deployed path; no separate sentence-transformers server required on Railway for that configuration).
- **Retrieval:** Similarity search over indexed chunks; responses can be scoped by museum.
- **Generation:** Prompts require answers to use retrieved context and the visitor’s language.
- **Curated shortcuts:** Keyword rules return **hand-written** `CORE_FACTS` strings (hours, location, etc.) without calling the LLM.

**Design trade-offs** (for fuller treatment see the PDF): RAG vs fine-tuning; managed LLM API vs on-premise models; Chroma vs other vector databases — all involve cost, latency, and maintainability.

---

## 3. Evaluation — scope and limitations (panel feedback)

- **Sample size:** Any pilot figures in early drafts were based on a **limited query set** and must **not** be generalized to all museum visitors or all institutions without a larger, pre-registered protocol (N, inclusion criteria, blind scoring).
- **Intent routing:** The repository includes `scripts/evaluation/evaluate_intent.py` and a multilingual CSV for **curated-route** agreement only. That is **not** the same as end-to-end **factual accuracy** of every generative answer.
- **Hallucination:** RAG, prompts, and out-of-scope behaviour **reduce** unsupported answers; they do **not** prove **100%** elimination of hallucination in all conditions.
- **Engagement / dwell time:** Any before/after engagement multiples require **defined measurement** (instrument, baseline, N); avoid stating large multipliers without that evidence in the report.

**Qualitative RAG checks** (example style — details in PDF):

| Test idea | Purpose |
|-----------|---------|
| Contradiction / false-premise question | Observe whether the system stays grounded or refuses when context is missing |
| In-scope cultural query | Check retrieval + answer alignment with KB text |
| Multilingual same intent | Check language consistency |

---

## 4. Latency (indicative)

| Mode | Order of magnitude (environment-dependent) |
|------|-----------------------------------------------|
| Gemini path | ~1–5 s depending on model, cold start, and network |
| Chunk-only fallback | Faster; depends on Chroma and payload size |

---

## 5. Conclusion (brief)

The system demonstrates a **practical RAG deployment** for multilingual museum interpretation with clear **limitations** on data scale and evaluation generalisability. **Future work:** larger annotated evaluation sets, ablation studies (chunk size, top-k, embedding choice), and optional on-device or open-weight LLMs for sovereignty and offline use.

---

*Supervisor: Thadee Gatera — see signed PDF for formal approval.*
