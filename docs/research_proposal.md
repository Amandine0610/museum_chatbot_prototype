# Ethical AI Integration in African Tourism: A Multilingual ML-driven Chatbot for Enhancing Visitor Engagement in Rwandan Museums

**BSc. in Software Engineering**  
**Amandine Irakoze**  
**Capstone Project**  
**Supervisor: Thadee Gatera**  
**23/01/2026**

---

## 1. Introduction
Museums play a vital role in sustaining a nation's cultural heritage and promoting tourism. In Rwanda, the tourism sector contributes significantly to the GDP (estimated at 9.8% for 2024). However, many museums still rely on traditional interpretation methods like static notices and human guides, leading to an "interpretation gap." Language barriers further limit accessibility, as most information is in English or French, excluding Kinyarwanda speakers.

## 2. Problem Statement
There is a technological gap in Rwandan museums where culture is stored but remains largely inaccessible. Existing digital solutions often lack nuances in low-resource languages (LRL) like Kinyarwanda, a phenomenon known as "language data flaring." Additionally, visitors often remain passive observers rather than active participants in the cultural story.

## 3. Project Objectives
### Main Objective
Design and develop a culturally contextualized, machine-learning-driven chatbot utilizing **Retrieval-Augmented Generation (RAG)** to offer interactive and multilingual (Kinyarwanda, English, French) storytelling for Rwandan museums.

### Specific Objectives
1.  Analyze current literature on NLP and LRL (2020-2025).
2.  Develop a three-tier software architecture (Frontend, Backend API, and ML Service).
3.  Evaluate performance using Visitor Experience (VX) and technical metrics (F1-score).

## 4. System Architecture
The system follows a three-tier RAG pipeline:
-   **Presentation Layer**: ReactJS/TailwindCSS web interface for visitor interaction.
-   **Application Layer**: Node.js/Express API for request handling and integration.
-   **ML & Knowledge Layer**: Python-based RAG service using LangChain, OpenAI (with local fallback), and a verified KAREN/RCHA knowledge base.

## 5. Significance
This project enhances visitor engagement, increases accessibility for local and foreign tourists, and solves real cultural issues in Rwanda through modern software engineering and machine learning.

---
*Verified Implementation Status: COMPLETED*
- [x] Three-tier architecture implemented.
- [x] RAG pipeline with local fallback functional.
- [x] Multilingual support logic integrated.
- [x] Enriched with RCHA historical data.
