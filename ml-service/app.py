from flask import Flask, request, jsonify
from flask_cors import CORS
from rag_pipeline import initialize_rag, get_answer
import os

app = Flask(__name__)
CORS(app)

print("Starting Rwandan Museum ML Service...")
initialize_rag()

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "service": "Museum-RAG-Engine"})

@app.route('/query', methods=['POST'])
def query():
    data = request.get_json()
    if not data or not data.get('query'):
        return jsonify({"error": "No query provided"}), 400

    answer = get_answer(data['query'])
    return jsonify({
        "response": answer,
        "language": data.get('language', 'en')
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
