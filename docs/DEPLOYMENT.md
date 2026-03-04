# 🚀 Deployment & Installation Guide

To deploy and run the **Universal Museum Guide** in any environment.

## 1. Prerequisites
- **Node.js**: v18 or higher (Frontend/Backend)
- **Python**: v3.9 or higher (ML Service)
- **Git**: For repository cloning

## 2. Environment Setup
Creating an `.env` file in the `ml-service` folder:
```env
OPENAI_API_KEY=your_key_here  
```

## 3. Step-by-Step Installation

### A. ML Service 
```bash
cd ml-service
python -m venv venv
source venv/bin/activate  
pip install -r requirements.txt
python app.py  # Runs on port 5050
```

### B. Backend 
```bash
cd backend
npm install
node server.js  # Runs on port 5000
```

### C. Frontend 
```bash
cd frontend
npm install
npm run dev     # Runs on port 5173
```

## 4. Testing the Deployment
Open your browser to:
- `https://museum-chatbott.onrender.com` (Language Selection)
- `https://museum-chatbott.onrender.com/?id=3` (Direct Museum Ingabo access)

## 5. Cloud Deployment Guide

To make the app accessible globally, follow these professional deployment steps:

### A. Frontend (Vercel - Recommended)
1. Push the code to GitHub.
2. Connect the repo to [Vercel](https://vercel.com).
3. **Build Settings**:
   - Build Command: `npm run build`
   - Output Directory: `dist`
   - Root Directory: `frontend`
4. **Environment Variables**: Add `VITE_API_URL` pointing to your deployed Backend URL.

### B. ML Service (Render / Railway)
Since this contains the RAG engine and ChromaDB, use **Render** or **Railway**:
1. Connect the `ml-service` subfolder.
2. **Environment Variables**: Add `OPENAI_API_KEY`.
3. **Build Command**: `pip install -r requirements.txt`
4. **Start Command**: `python app.py` or use the provided `Dockerfile`.

### C. Backend (Render / Railway)
1. Connect the `backend` subfolder.
2. **Environment Variables**: 
   - `ML_SERVICE_URL`: Set this to `https://museum-chatbot-ml-1.onrender.com`
3. **Start Command**: `node server.js`

---

## 🏗️ Docker Deployment (For ML Service)
For maximum reliability, we have provided a `Dockerfile` in the `ml-service` directory. This ensures that the HuggingFace models and ChromaDB are installed identically in the cloud as they are on your local machine.

```bash
cd ml-service
docker build -t museum-chatbot-ml .
docker run -p 5005:5005 museum-chatbot-ml
```

---
> [!IMPORTANT]
> **Performance Tip**: When deploying to the cloud, ensure the ML Service has at least 512MB of RAM to handle the `sentence-transformers` embedding engine during startup.
