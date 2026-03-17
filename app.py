"""
Rwanda Museum Chatbot - RAG-based chatbot using Chroma DB + Gemini LLM
Version: 3.7 (Instant Boot - Render High Priority)
Supports: English, French, Kinyarwanda for ALL Museums
"""

import os
import json
import random
import string
import re
from flask import Flask, request, jsonify
from flask_cors import CORS
# HEAVY IMPORTS MOVED TO LAZY LOADERS BELOW

app = Flask(__name__)
CORS(app)

# Instance Configuration
INSTANCE_ID = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
KNOWLEDGE_BASE_DIR = os.path.join(os.path.dirname(__file__), 'knowledge_base')
CHROMA_PERSIST_DIR = os.path.join(os.path.dirname(__file__), 'chroma_db')
MODEL_NAME = 'sentence-transformers/all-MiniLM-L6-v2'

# Environment Setup
try:
    from dotenv import load_dotenv
    ml_env = os.path.join(os.path.dirname(__file__), 'ml-service', '.env')
    if os.path.exists(ml_env): load_dotenv(ml_env)
    else: load_dotenv()
except ImportError: pass

# LLM Config (Lazy Configured)
gemini_model = None

def get_gemini():
    global gemini_model
    if gemini_model is None:
        import google.generativeai as genai
        api_key = os.environ.get('GOOGLE_API_KEY') or os.environ.get('GEMINI_API_KEY', '')
        if api_key:
            genai.configure(api_key=api_key)
            gemini_model = genai.GenerativeModel('gemini-2.0-flash')
            print(f"[{INSTANCE_ID}] Gemini Brain Loaded")
        else:
            print(f"[{INSTANCE_ID}] Gemini API Key Missing")
    return gemini_model

# Museum Mappings
MUSEUM_NAMES = {
    "1": {"en": "King's Palace Museum", "fr": "Musée du Palais Royal", "rw": "Ingoro y'Abami i Nyanza"},
    "2": {"en": "Ethnographic Museum", "fr": "Musée Ethnographique", "rw": "Inzu ndangamurage i Huye"},
    "3": {"en": "Museum Ingabo", "fr": "Musée Ingabo", "rw": "Inzu ndangamurage Ingabo"}
}

MUSEUM_MAPPING = { "1": "king's_palace_museum.txt", "2": "ethnographic_museum.txt", "3": "museum_ingabo.txt" }

# CORE FACTS (High Reliability facts with French & English Parity)
CORE_FACTS = {
    "1": { # King's Palace
        "rw": {
            "history": "Ingoro y'Abami i Nyanza igaragaza amateka y'ubwami bw'u Rwanda n'uburyo bwayoborwaga kugeza mu ntangiriro z'imyaka ya 1960. Irimo inzu y'ibyatsi yubatse mu buryo bwa gakondo n'inzu ya Art Deco y'umwami Mutara III Rudahigwa (yubatse mu 1931).",
            "hours": "7:00 AM - 6:00 PM (Kuwa Kabiri - ku Cyumweru). Kuwa Mbere irafunze.",
            "location": "Akarere ka Nyanza, mu Ntara y'Amajyepfo, ku birometero 88 uvuye i Kigali.",
            "inyambo": "Iyi ngoro irimo inka z'umwami (Inyambo) zirangwa n'amahembe maremare cyane kandi zerekana uburanga n'umuco gakondo.",
            "rudahigwa": "Umwami Mutara III Rudahigwa (1911–1959) yari umwami w'u Rwanda wateje imbere igihugu kandi akubaka ingoro ya kijyambere iherereye hano i Nyanza mu 1931."
        },
        "fr": {
            "history": "Le Musée du Palais Royal à Nyanza offre un aperçu du système monarchique rwandais, avec une réplique du palais traditionnel et le palais moderne du Roi Mutara III Rudahigwa.",
            "hours": "07h00 - 18h00 (Mardi au Dimanche). Fermé le Lundi.",
            "location": "District de Nyanza, Province du Sud, à 88 km de Kigali.",
            "inyambo": "Le musée abrite les vaches royales Inyambo, célèbres pour leurs cornes majestueuses.",
            "rudahigwa": "Le Roi Mutara III Rudahigwa (1911-1959) était un souverain réformateur qui a construit ce palais moderne en 1931."
        },
        "en": {
            "history": "The King's Palace in Nyanza showcases Rwanda's monarchical history through a traditional palace replica and the modern residence of King Mutara III Rudahigwa.",
            "hours": "7:00 AM - 6:00 PM (Tuesday to Sunday). Closed on Mondays.",
            "location": "Nyanza District, Southern Province, about 88 km from Kigali.",
            "inyambo": "Known for their majestic long horns, the royal Inyambo cattle are a living cultural symbol found here.",
            "rudahigwa": "King Mutara III Rudahigwa (1911–1959) was a visionary terminal leader who built the modern Art Deco palace in Nyanza."
        }
    },
    "2": { # Ethnographic
        "rw": {
            "history": "Inzu Ndangamurage y'i Huye ni imwe mu nzu zikomeye muri Afurika zirimo ibikoresho n'amateka by'umuco.",
            "hours": "9:00 AM - 6:00 PM (Kuwa Kabiri - ku Cyumweru).",
            "location": "Akarere ka Huye, mu Ntara y'Amajyepfo, ku birometero 130 uvuye i Kigali.",
            "highlights": "Ifite ibice birindwi birimo imyubakire, ubugeni bwa gakondo nko kuboha amaseke, n'ingoma z'ingabe."
        },
        "fr": {
            "history": "Le Musée Ethnographique de Huye est l'un des plus riches d'Afrique, retraçant l'histoire du Rwanda à travers sept galeries thématiques.",
            "hours": "09h00 - 18h00 (Mardi au Dimanche).",
            "location": "District de Huye, Province du Sud, à 130 km de Kigali.",
            "highlights": "Les galeries présentent l'architecture traditionnelle, l'artisanat (Agaseke), et une collection unique de tambours royaux."
        },
        "en": {
            "history": "The Ethnographic Museum in Huye houses a world-class collection depicting Rwandan culture and history across seven galleries.",
            "hours": "9:00 AM - 6:00 PM (Tuesday to Sunday).",
            "location": "Huye District, Southern Province, about 130 km from Kigali.",
            "highlights": "Highlights include traditional architectural models, Agaseke baskets, and royal ceremonial drums."
        }
    },
    "3": { # Museum Ingabo
        "rw": {
            "history": "Ingoro Ingabo ni inzu ndangamurage y'abigenga y'ubugeni iherereye i Rebero mu Mujyi wa Kigali.",
            "hours": "9:00 AM - 6:00 PM (ku Cyumweru kugeza kuwa Gatanu). Kuwa Gatandatu irafunze.",
            "location": "Rebero Hill (Kigali Cultural Village), KK 553 st, Kigali.",
            "founder": "Yashinzwe na King Ngabo, umuhanzi n'umushanditsi w'ikerekezo washatse kwerekana amateka n'icyerekezo binyuze mu bugeni.",
            "inzira": "Imurikagurisha rya 'Inzira y'Inzitane' rigaragaza urugendo rw'u Rwanda rwo kwiyubaka mu myaka 30 ishize binyuze mu buhanzi n'ibitekerezo."
        },
        "fr": {
            "history": "Le Musée Ingabo est le premier musée privé du Rwanda, fondé par l'artiste King Ngabo à Rebero, Kigali, en 2023.",
            "hours": "09h00 - 18h00 (Dimanche au Vendredi). Fermé le Samedi.",
            "location": "Colline de Rebero (Kigali Cultural Village), KK 553 st, Kigali.",
            "founder": "Le musée a été fondé par l'artiste King Ngabo, un entrepreneur culturel rwandais dédié à la narration africaine à travers l'art.",
            "inzira": "L'exposition 'Inzira y'Inzitane' est une installation immersive qui raconte les 30 ans de résilience et de reconstruction du Rwanda (1994-2024)."
        },
        "en": {
            "history": "Museum Ingabo is Rwanda's first private museum, focused on storytelling and contemporary African art.",
            "hours": "9:00 AM - 6:00 PM (Sunday to Friday). Closed on Saturdays.",
            "location": "Rebero Hill (Kigali Cultural Village), KK 553 st, Kigali.",
            "founder": "Founded by the visionary artist King Ngabo to celebrate Rwandan heritage through creative expression.",
            "inzira": "The 'Inzira y'Inzitane' (Path of Resilience) exhibition showcases Rwanda's journey of reconstruction over the last 30 years."
        }
    }
}

# Persona Wrappers (Conversational Framing)
PERSONA_WRAPPERS = {
    'rw': [
        "Nshingiye ku manyandiko dufite hano mu Ngoro: {text} Hari ikindi nkwifuriza kumenya?",
        "Nk'umurinzi w'aya mateka, dore icyo nakubwira: {text} Mbese ushaka kumenya n'ibindi?",
        "Urakoze ku kibazo cyawe. {text} Ndizera ko ibi bigufashije gusobanukirwa."
    ],
    'en': [
        "As your Digital Curator, here is what our archives say: {text} Does this help with your exploration?",
        "Excellent question. {text} Would you like to dive deeper into another part of our history?",
        "Based on the official records here at the museum: {text} Is there anything else I can assist you with?"
    ],
    'fr': [
        "En tant que Conservateur Numérique, voici ce que disent nos archives : {text} Souhaitez-vous d'autres précisions ?",
        "C'est une excellente question. {text} Puis-je vous aider pour une autre recherche ?",
        "D'après les documents officiels du musée : {text} Comment puis-je encore vous assister ?"
    ]
}

# Lazy-loaded globals
embedding_model = None
chroma_client = None
collection = None

def get_db():
    global embedding_model, chroma_client, collection
    if embedding_model is None:
        print(f"[{INSTANCE_ID}] Lazy-loading ML Engine & ChromaDB...")
        import chromadb
        from sentence_transformers import SentenceTransformer
        embedding_model = SentenceTransformer(MODEL_NAME)
        chroma_client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
        collection = chroma_client.get_or_create_collection(name="rwanda_museums_v3_7")
        if collection.count() == 0:
            initialize_vector_store()
    return embedding_model, collection

def clean_text(text):
    if not text: return ""
    text = re.sub(r'^#+\s*(\d+\.)?\s*', '', text, flags=re.MULTILINE)
    text = text.replace('**', '').replace('__', '').replace('*', '').replace('_', '')
    text = re.sub(r'^-{3,}$', '', text, flags=re.MULTILINE)
    return text.strip()

def load_knowledge_base():
    documents, metadata, ids = [], [], []
    file_to_id = {v: k for k, v in MUSEUM_MAPPING.items()}
    for filename in os.listdir(KNOWLEDGE_BASE_DIR):
        if filename.endswith('.txt'):
            mid = file_to_id.get(filename, "unknown")
            filepath = os.path.join(KNOWLEDGE_BASE_DIR, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                sections = [s.strip() for s in content.split('\n\n') if len(s.strip()) > 20]
                for i, section in enumerate(sections):
                    documents.append(section)
                    metadata.append({"museum_id": mid, "source": filename})
                    ids.append(f"{filename}_{i}_{INSTANCE_ID}")
    return documents, metadata, ids

def initialize_vector_store():
    # This now assumes get_db has been called or uses current globals
    docs, metas, ids = load_knowledge_base()
    if docs:
        embeddings = embedding_model.encode(docs)
        collection.add(documents=docs, embeddings=embeddings.tolist(), metadatas=metas, ids=ids)
    print(f"[{INSTANCE_ID}] Database re-indexed: {collection.count()} items.")

def apply_persona(text, lang):
    wrappers = PERSONA_WRAPPERS.get(lang, PERSONA_WRAPPERS['en'])
    return random.choice(wrappers).format(text=clean_text(text))

def get_core_fact(query, museum_id, language):
    m_id = str(museum_id)
    if m_id not in CORE_FACTS: return None
    lang_facts = CORE_FACTS[m_id].get(language, CORE_FACTS[m_id].get('en', {}))
    q_low = query.lower().strip()
    
    # Priority Triggers with French keywords
    if any(k in q_low for k in ["rudahigwa", "mutara"]): return lang_facts.get("rudahigwa")
    if any(k in q_low for k in ["ngabo", "founder", "fondateur", "créateur", "createur", "qui est-ce"]): return lang_facts.get("founder")
    if any(k in q_low for k in ["inzira", "inzitane", "parcours", "résilience", "reconstruction"]): return lang_facts.get("inzira")
    if any(k in q_low for k in ["agaseke", "basket", "panier", "highlights", "drums", "tambour", "weapons", "armes"]): return lang_facts.get("highlights")
    if any(k in q_low for k in ["inyambo", "inka", "cattle", "vache", "cornes"]): return lang_facts.get("inyambo")
    if any(k in q_low for k in ["amasaha", "hours", "open", "time", "horaires", "ouvert", "quand"]): return lang_facts.get("hours")
    if any(k in q_low for k in ["aho iherereye", "location", "lieu", "where", "distance", "situé"]): return lang_facts.get("location")
    if any(k in q_low for k in ["amateka", "history", "histoire", "tell me about"]): return lang_facts.get("history")
    
    return None

def generate_response(query, context, language, museum_id, museum_name):
    # Core Facts (Aggressive Priority)
    core_text = get_core_fact(query, museum_id, language)
    if core_text: return apply_persona(core_text, language)

    # Filler Logic
    fillers = ['yes', 'yego', 'oui', 'more', 'iyindi', 'plus', 'tell me more', 'mbwire ibindi']
    if query.lower().strip() in fillers and context:
        return apply_persona(context[0], language)

    # AI Prompt
    system_prompts = {
        'en': f"You are the Digital Curator for {museum_name}. Speak professionally. RESPOND ONLY IN ENGLISH.",
        'fr': f"Vous êtes le Conservateur Numérique du {museum_name}. Parlez de manière professionnelle. RÉPONDEZ UNIQUEMENT EN FRANÇAIS.",
        'rw': f"Uri Umurinzi w'amateka muri {museum_name}. Vuga mu buryo bw'umwuga kandi wubashye. SUBIZA MU KINYARWANDA GUSA."
    }

    try:
        model = get_gemini()
        if not model: raise Exception("No Key")
        context_text = "\n".join(context)
        prompt = f"System: {system_prompts.get(language, system_prompts['en'])}\nContext: {context_text}\nUser Question: {query}\n\nAssistant Response (Conversational):"
        response = model.generate_content(prompt)
        return clean_text(response.text.strip())
    except Exception as e:
        print(f"[{INSTANCE_ID}] AI Error/Quota: {e}")
        if not context:
            no_info = {
                'en': f"I'm sorry, I don't have that specific detail for {museum_name} yet.",
                'rw': f"Mumbabarire, nta makuru arambuye mfite kuri ibyo muri {museum_name} uyu munsi.",
                'fr': f"Désolé, je n'ai pas cette information précise pour le {museum_name}."
            }
            return no_info.get(language, no_info['en'])
        
        # Best Paragraph Fallback (Translated if possible, otherwise context[0])
        para = context[0]
        for c in context:
            if len(c.strip()) > 40 and '###' not in c[:10]:
                para = c
                break
        return apply_persona(para, language)

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    msg = data.get('query') or data.get('message', '')
    lang = data.get('language', 'en')
    mid = str(data.get('museumId')) if data.get('museumId') and str(data.get('museumId')).lower() != 'none' else '1'
    
    m_info = MUSEUM_NAMES.get(mid, MUSEUM_NAMES["1"])
    m_name = m_info.get(lang, m_info['en'])
    
    if msg == 'special:welcome':
        res = {
            'en': f"Welcome to {m_name}. I am your Digital Curator. How may I assist your exploration today?",
            'fr': f"Bienvenue au {m_name}. Je suis votre Conservateur Numérique. Comment puis-je vous aider ?",
            'rw': f"Murakaza neza muri {m_name}. Ndi umurinzi w'amateka aha. Nabafasha iki uyu munsi?"
        }
        return jsonify({'response': res.get(lang, res['en'])})

    # Retrieval
    model, coll = get_db()
    query_embedding = model.encode([msg]).tolist()
    results = coll.query(query_embeddings=query_embedding, n_results=3, where={"museum_id": mid})
    context = results['documents'][0] if results['documents'] else []
    
    response = generate_response(msg, context, lang, mid, m_name)
    return jsonify({'response': response, 'instance': INSTANCE_ID, 'version': '3.7'})

@app.route('/api/status', methods=['GET'])
def status(): 
    count = collection.count() if collection else 0
    return jsonify({'status': 'online', 'version': '3.7', 'instance': INSTANCE_ID, 'indexed': count})

if __name__ == '__main__':
    # Local runs still pre-load for comfort
    get_db()
    get_gemini()
    port = int(os.environ.get('PORT', 5000))
    print("\n" + "*"*60)
    print(f"  !!! INSTANT BOOT: MUSEUM SERVER v3.7 !!!")
    print(f"  STATUS: RENDER READY & FAST AS LIGHT")
    print(f"  PORT: {port} | INSTANCE ID: {INSTANCE_ID}")
    print("*"*60 + "\n")
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)