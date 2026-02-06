### Social Media Chatbot (Capstone Project): Rwandan Museum.

### Project Description
**Rwandan Museum Chatbot** is a culturally situational, machine-learning-based application, which is aimed at increasing visitor interaction in Rwandan museums. It sends out a Retrieval-Augmented Generation (RAG) pipeline to get interactive, multilingual (Kinyarwanda, English, French) storytelling of museum artifacts, history, and heritage and answering questions about museum artifacts, history, and heritage. This project is expected to reduce the interpretation gap in conventional exhibits by providing an easy to use, AI-based digital guide.

### Repository
GitHub Repository Link  
https://github.com/Amandine0610/Capstone

### Designs & Mockups
The user interface has been done in consideration of Rwandan culture (through the use of rwanda-blue, rwanda-yellow and rwanda-green color palette).

### Language Selection & Welcome
Language Selection

### Artefact Detail View
Artefact Detail

### Chat Interface
Chat Interface

### Interactive Guidance
Interactive Guide

### Architecture
The system uses a three-tier architecture of the modern times:
- **Frontend:** ReactJS + Vite + TailwindCSS (Responsive Web Interface).
- **Backend:** Node.js + Express ( API Gateway and Orchestrator ).
- **ML Service:** Python + LangChain + ChromaDB (RAG Pipeline).

### Data & Model Analysis
The machine learning part is examined in the ml-service/modelanalysis.ipynb notebook.
- Data Visualization Distribution of terms in the museum knowledge base.
- Detailed RAG flow (Ingestion -> Embedding -> Retrieval -> Generation): Model Architecture.
- Performance Measures: Preliminary results are 0.85 Precision and approximate 1.2s Latency.

### Setup Instructions

### Prerequisites
- Node.js: v18 (Backend/Frontend)
- Python: v3.8+ (for ML Service)
- Git: For version control
- VS Code: Python & ES7+ extensions Recommendable IDE.

### ML Service Setup
- cd ml-service
- Build virtual world (not implemented, but suggested)
- python -m venv venv
- venv (Windows: venv\Scripts\activate, Mac/Linux: source venv/bin/activate)
- pip install requirements.txt
- Run the service
- python app.py
Instructions The ML service needs an OpenAI API Key in a .env file (OPENAIAPIKEY=sk-..) in place to be fully functional. In case no key is given, a mock mode can be used.

### Backend Setup
- cd backend
- npm install
- (Make an.env file with PORT=3000 and MLSERVICEURL=http://localhost:5000).
- npm start

### Frontend Setup
- cd frontend
- npm install
- npm run dev
Access the application through the localhost on 5173.

### Deployment Plan
The application will be cloud deployed to be scaled and made accessible.

### Infrastructure
- Frontend: Installed on Vercel or Netlify to distribute the CDN on the global level and automatically build on the basis of GitHub.
- Browser: Built as a Node.js web service on Render / Heroku.
ML Service: Python dependencies and auto-scaling Containerized using Docker and deployed to Google Cloud Run.
- Database Vector: ChromaDB is at present local, although it will be moved to Pinecone or Weaviate on the move to production persistence.

### CI/CD Pipeline
To execute tests (testmockrag.py) on each push, the workflow is run on GitHub Actions.
Upon merging to the main branch, it is automatically deployed.

### Testing
- ML: python testmock_rag.py: Checks the logic of the RAG pipeline using mock data.
- Backend: Swagger UI can be used at the endpoint of API testing at the localhost:3000/api-docs.