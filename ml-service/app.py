from flask import Flask, request, jsonify
from rag_pipeline import query_rag
import os

app = Flask(__name__)

@app.route('/query', methods=['POST'])
def query():
    data = request.json
    user_query = data.get('query')
    language = data.get('language', 'en')
    
    if not user_query:
        return jsonify({"error": "No query provided"}), 400
    
    try:
        # In a real scenario, we might want to catch specific RAG errors
        # Check if vector DB exists, if not, maybe return a specific message
        if not os.path.exists("./chroma_db"):
             return jsonify({
                 "result": "System initializing... Please ingest documents first.",
                 "source_documents": []
             })

        response = query_rag(user_query, language)
        # response is currently just a string from query_rag return value
        
        return jsonify({
            "response": response,
            "source": "ml-service"
        })
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "service": "ML Service"})

if __name__ == '__main__':
    app.run(port=5000, debug=True)
