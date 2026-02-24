from flask import Flask, request, jsonify
from flask_cors import CORS
# from rag_pipeline import initialize_rag, get_answer # Correct import later
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Mock RAG for initial testing if dependencies fail
def get_answer(query):
    return f"Simulated AI Response to: {query}"

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "ML-Service-Mock"})

@app.route('/query', methods=['POST'])
def query_chatbot():
    data = request.json
    user_query = data.get('query')
    language = data.get('language', 'English')
    
    if not user_query:
        return jsonify({"error": "No query provided"}), 400

    # Get answer from RAG pipeline
    answer = get_answer(user_query)
    
    return jsonify({
        "response": answer,
        "language": language
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
