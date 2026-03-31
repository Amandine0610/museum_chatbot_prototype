import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from src.rag.engine import RAGEngine

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize RAG Engine
print("Initializing RAG Engine...")
rag_engine = RAGEngine()
print("RAG Engine initialized successfully!")

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'timestamp': __import__('datetime').datetime.now().isoformat()
    })

@app.route('/api/query', methods=['POST'])
def query():
    """Process user query and return AI response"""
    try:
        data = request.get_json()
        
        message = data.get('message', '')
        language = data.get('language', 'en')
        museum_id = data.get('museum_id', 'ingabo')
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Process query through RAG engine
        result = rag_engine.query(
            message=message,
            language=language,
            museum_id=museum_id
        )
        
        return jsonify(result)
    
    except Exception as e:
        print(f"Error processing query: {str(e)}")
        return jsonify({
            'error': 'Failed to process query',
            'message': str(e)
        }), 500

@app.route('/api/embeddings/status', methods=['GET'])
def embeddings_status():
    """Check if embeddings are ready"""
    return jsonify({
        'is_ready': rag_engine.is_ready,
        'collection_count': rag_engine.get_collection_count()
    })

@app.route('/api/reset', methods=['POST'])
def reset():
    """Reset the RAG engine (rebuild embeddings)"""
    try:
        rag_engine.reset()
        return jsonify({'status': 'reset complete'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    print(f"""
╔═══════════════════════════════════════════════════════════════╗
║     Rwanda Museums Chatbot - ML Service                       ║
║     Running on port {port}                                       ║
╚═══════════════════════════════════════════════════════════════╝
    """)
    
    app.run(host='0.0.0.0', port=port, debug=debug)