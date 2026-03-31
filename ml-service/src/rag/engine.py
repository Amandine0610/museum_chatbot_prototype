import os
import json
from datetime import datetime
from typing import Optional, List, Dict, Any

# LangChain imports
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document

# Try to import LLM providers
try:
    import google.generativeai as genai
    GOOGLE_AI_AVAILABLE = True
except ImportError:
    GOOGLE_AI_AVAILABLE = False

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

class RAGEngine:
    """Retrieval-Augmented Generation Engine for the museum chatbot"""
    
    def __init__(self):
        self.is_ready = False
        self.vectorstores: Dict[str, Chroma] = {}
        self.embeddings = None
        self.text_splitter = None
        
        # Fallback responses for each language
        self.fallback_responses = {
            'en': {
                'greeting': "Welcome! I'm your cultural guide. Feel free to ask about our exhibits, artifacts, or Rwandan history.",
                'out_of_scope': "That's an interesting question, but I'm specifically designed to help with our museum's collections and Rwandan cultural heritage. Please ask me about our exhibits or history!",
                'error': "I apologize, but I'm having trouble providing an answer right now. Please try again."
            },
            'fr': {
                'greeting': "Bienvenue ! Je suis votre guide culturel. N'hésitez pas à poser des questions sur nos expositions, artefacts ou histoire rwandaise.",
                'out_of_scope': "C'est une question intéressante, mais je suis spécifiquement conçu pour aider avec les collections de notre musée et le patrimoine culturel rwandais. Veuillez me poser des questions sur nos expositions ou notre histoire !",
                'error': "Je m'excuse, mais j'ai du mal à fournir une réponse en ce moment. Veuillez réessayer."
            },
            'rw': {
                'greeting': "Murakaza neza! Ndi umuhuza w'umuco. Wibazire ibijyanye n'ibitekerezo, ibikoresho, cyangwa ibitekerezo y'u Rwanda.",
                'out_of_scope': "Ni ikibazo gikwiye, ariko nashinzwe mugushimira ibikoresho by'ishyingiro n'ibiganiro by'umuco w'u Rwanda. Ntubaze ibijyanye n'ibitekerezo!",
                'error': "N Navarre, noneho ngaha igisubizo. Ongera ugerageze."
            }
        }
        
        self._initialize()
    
    def _initialize(self):
        """Initialize the RAG components"""
        print("Initializing RAG Engine components...")
        
        # Initialize embeddings model
        try:
            self.embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={'device': 'cpu'}
            )
            print("✓ Embeddings model loaded")
        except Exception as e:
            print(f"✗ Failed to load embeddings: {e}")
            return
        
        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            separators=["\n\n", "\n", " ", ""]
        )
        print("✓ Text splitter initialized")
        
        # Load knowledge base for each museum
        self._load_knowledge_bases()
        
        self.is_ready = True
        print("RAG Engine initialization complete!")
    
    def _load_knowledge_bases(self):
        """Load knowledge bases for each museum"""
        data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        
        # Check if data directory exists
        if not os.path.exists(data_dir):
            print(f"Warning: Data directory not found at {data_dir}")
            print("Creating sample data...")
            self._create_sample_data()
            return
        
        # Supported museums
        museums = ['ingabo', 'ethnographic', 'kings_palace', 'genocide_memorial']
        
        for museum_id in museums:
            museum_data_dir = os.path.join(data_dir, museum_id)
            if os.path.exists(museum_data_dir):
                self._load_museum_kb(museum_id, museum_data_dir)
            else:
                print(f"No data found for museum: {museum_id}")
    
    def _load_museum_kb(self, museum_id: str, data_dir: str):
        """Load knowledge base for a specific museum"""
        try:
            # Load documents from all files in the directory
            documents = []
            
            for filename in os.listdir(data_dir):
                if filename.endswith(('.txt', '.md', '.pdf')):
                    filepath = os.path.join(data_dir, filename)
                    try:
                        if filename.endswith('.txt') or filename.endswith('.md'):
                            with open(filepath, 'r', encoding='utf-8') as f:
                                text = f.read()
                                doc = Document(
                                    page_content=text,
                                    metadata={
                                        'source': filename,
                                        'museum': museum_id
                                    }
                                )
                                documents.append(doc)
                    except Exception as e:
                        print(f"Error loading {filename}: {e}")
            
            if documents:
                # Split documents
                chunks = self.text_splitter.split_documents(documents)
                
                # Create vector store
                persist_dir = os.path.join(os.path.dirname(__file__), '..', 'vectorstores', museum_id)
                os.makedirs(persist_dir, exist_ok=True)
                
                vectorstore = Chroma.from_documents(
                    documents=chunks,
                    embedding=self.embeddings,
                    persist_directory=persist_dir
                )
                
                self.vectorstores[museum_id] = vectorstore
                print(f"✓ Loaded knowledge base for {museum_id} ({len(chunks)} chunks)")
            else:
                print(f"No documents found for {museum_id}")
                
        except Exception as e:
            print(f"Error loading KB for {museum_id}: {e}")
    
    def _create_sample_data(self):
        """Create sample knowledge base data"""
        data_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'ingabo')
        os.makedirs(data_dir, exist_ok=True)
        
        # Sample content about Museum Ingabo
        sample_content = """
        Museum Ingabo - Overview
        
        Museum Ingabo, located in Rwanda, is a cultural institution dedicated to preserving 
        and showcasing the rich heritage of Rwanda. The museum houses various collections 
        that tell the story of Rwandan history and culture.
        
        Inzira y'Inzitane
        
        One of the most significant exhibitions at Museum Ingabo is "Inzira y'Inzitane" 
        (The Path of Resilience), which symbolizes the 30-year journey of survival and 
        resilience of the Rwandan people. This exhibition documents the history, struggles, 
        and triumphs of Rwanda.
        
        King Ngabo
        
        Museum Ingabo was founded by King Ngabo, a cultural visionary who recognized 
        the importance of preserving Rwandan heritage for future generations. His vision 
        continues to inspire the museum's mission to educate and inspire visitors.
        
        Rwandan Culture
        
        The museum features exhibits on traditional Rwandan culture including:
        - Traditional Intore dance and music
        - Handicrafts and pottery
        - Traditional housing (Rugogi)
        - Agricultural practices
        - Social customs and traditions
        
        The museum serves as an educational resource for both local and international 
        visitors seeking to understand Rwandan cultural heritage.
        """
        
        with open(os.path.join(data_dir, 'about.txt'), 'w', encoding='utf-8') as f:
            f.write(sample_content)
        
        # Reload with new data
        self._load_knowledge_bases()
    
    def query(self, message: str, language: str = 'en', museum_id: str = 'ingabo') -> Dict[str, Any]:
        """Process a user query and return a response"""
        
        # Check if this is a greeting
        greeting_keywords = {
            'en': ['hello', 'hi', 'hey', 'welcome'],
            'fr': ['bonjour', 'salut', 'bonsoir', 'bienvenue'],
            'rw': ['murakaza', 'hello', 'hi']
        }
        
        msg_lower = message.lower()
        if any(kw in msg_lower for kw in greeting_keywords.get(language, [])):
            return {
                'response': self.fallback_responses.get(language, self.fallback_responses['en'])['greeting'],
                'sources': [],
                'detected_language': language
            }
        
        # Get vector store for the museum
        vectorstore = self.vectorstores.get(museum_id)
        
        if not vectorstore:
            # Return fallback response
            return {
                'response': self._get_llm_response(message, language, museum_id),
                'sources': [],
                'detected_language': language
            }
        
        try:
            # Perform similarity search
            docs = vectorstore.similarity_search(message, k=3)
            
            if not docs:
                return {
                    'response': self.fallback_responses.get(language, self.fallback_responses['en'])['out_of_scope'],
                    'sources': [],
                    'detected_language': language
                }
            
            # Get context from retrieved documents
            context = "\n\n".join([doc.page_content for doc in docs])
            sources = [doc.metadata.get('source', 'unknown') for doc in docs]
            
            # Generate response using LLM
            response = self._generate_response(
                message=message,
                context=context,
                language=language,
                museum_id=museum_id
            )
            
            return {
                'response': response,
                'sources': list(set(sources)),
                'detected_language': language
            }
            
        except Exception as e:
            print(f"Error in query: {e}")
            return {
                'response': self._get_llm_response(message, language, museum_id),
                'sources': [],
                'detected_language': language,
                'error': str(e)
            }
    
    def _generate_response(self, message: str, context: str, language: str, museum_id: str) -> str:
        """Generate a response using available LLM"""
        
        # Try Google Gemini first
        if GOOGLE_AI_AVAILABLE and os.getenv('GOOGLE_API_KEY'):
            try:
                genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
                model = genai.GenerativeModel('gemini-2.0-flash')
                
                prompt = self._build_prompt(message, context, language)
                response = model.generate_content(prompt)
                return response.text
            except Exception as e:
                print(f"Google AI error: {e}")
        
        # Try OpenAI as fallback
        if OPENAI_AVAILABLE and os.getenv('OPENAI_API_KEY'):
            try:
                client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
                
                prompt = self._build_prompt(message, context, language)
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.choices[0].message.content
            except Exception as e:
                print(f"OpenAI error: {e}")
        
        # Fallback to rule-based response
        return self._get_llm_response(message, language, museum_id)
    
    def _build_prompt(self, message: str, context: str, language: str) -> str:
        """Build the prompt for the LLM"""
        
        lang_instruction = {
            'en': 'Respond in English.',
            'fr': 'Répondez en français.',
            'rw': 'Respond in Kinyarwanda using proper cultural terminology.'
        }
        
        prompt = f"""You are a cultural guide at a Rwandan museum. 
Your role is to provide accurate, culturally sensitive information about Rwandan heritage.

Context from museum archives:
{context}

Question: {message}

{lang_instruction.get(language, lang_instruction['en'])}

Guidelines:
- Only use information from the provided context
- If the context doesn't contain relevant information, say so
- Be respectful and culturally sensitive
- Keep responses informative but concise

Answer:"""
        
        return prompt
    
    def _get_llm_response(self, message: str, language: str, museum_id: str) -> str:
        """Get a fallback response when no LLM is available"""
        
        # Simple keyword-based responses
        responses = {
            'en': {
                'king': 'King Ngabo was a cultural visionary who founded Museum Ingabo to preserve Rwandan heritage.',
                'history': 'Our museum showcases the rich history and culture of Rwanda through various exhibits.',
                'exhibit': 'We have several exhibits including Inzira y\'Inzitane which symbolizes our 30-year journey of resilience.',
                'default': self.fallback_responses['en']['out_of_scope']
            },
            'fr': {
                'roi': 'Le roi Ngabo était un visionnaire culturel qui a fondé le Musée Ingabo pour préserver le patrimoine rwandais.',
                'histoire': 'Notre musée présente la riche histoire et culture du Rwanda à travers diverses expositions.',
                'exposition': 'Nous avons plusieurs expositions dont Inzira y\'Inzitane qui symbolise notre parcours de résilience de 30 ans.',
                'default': self.fallback_responses['fr']['out_of_scope']
            },
            'rw': {
                'king': 'Umwami Ngabo yari umushumba w\'umuco wavuze ko igushingiro ry\'Ingabo rigomba kubika ibitekerezo by\'u Rwanda.',
                'history': 'Ishyingiro ryacu rifitanye ibiganiro byinshi ku butumwa bw\'u Rwanda n\'umuco.',
                'exhibit': 'Ifitanye ibitekerezo byinshi harimo Inzira y\'Inzitane ikurikirana ibitekerezo by\'imyaka 30.',
                'default': self.fallback_responses['rw']['out_of_scope']
            }
        }
        
        msg_lower = message.lower()
        lang_responses = responses.get(language, responses['en'])
        
        if 'king' in msg_lower or 'ngabo' in msg_lower:
            return lang_responses['king']
        elif 'history' in msg_lower or 'ibitekerezo' in msg_lower:
            return lang_responses['history']
        elif 'exhibit' in msg_lower or 'ibitekerezo' in msg_lower:
            return lang_responses['exhibit']
        else:
            return lang_responses['default']
    
    def get_collection_count(self) -> int:
        """Get total number of collections loaded"""
        return len(self.vectorstores)
    
    def reset(self):
        """Reset the RAG engine"""
        self.vectorstores = {}
        self._initialize()
