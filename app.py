"""
Rwanda Museum Chatbot - RAG-based chatbot using Chroma DB + Gemini LLM
Version: 4.3 (Language Enforcement + Relevance Guard)
Supports: English, French, Kinyarwanda for ALL Museums
"""

import os
import json
import random
import string
import re
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Instance Configuration
INSTANCE_ID = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
KNOWLEDGE_BASE_DIR = os.path.join(os.path.dirname(__file__), 'knowledge_base')
CHROMA_PERSIST_DIR = os.path.join(os.path.dirname(__file__), 'chroma_db')
MODEL_NAME = 'sentence-transformers/all-MiniLM-L6-v2'

# Environment Setup
try:
    from dotenv import load_dotenv
    _base = os.path.dirname(os.path.abspath(__file__))
    _ml_env = os.path.join(_base, 'ml-service', '.env')
    _root_env = os.path.join(_base, '.env')
    if os.path.exists(_ml_env):
        load_dotenv(_ml_env)
    if os.path.exists(_root_env):
        load_dotenv(_root_env, override=False)  # root fills gaps; ml-service wins if both set
    if not os.path.exists(_ml_env) and not os.path.exists(_root_env):
        load_dotenv()
except ImportError:
    pass

# LLM Config — uses Gemini REST API directly (no SDK version dependency)
import requests as _requests
import time as _time

_GEMINI_API_KEY = None
_GEMINI_ACTIVE_MODEL = None
# Try flash-lite first (higher free-tier quota), then standard models
_GEMINI_MODELS = [
    'gemini-2.0-flash-lite',
    'gemini-2.0-flash',
    'gemini-1.5-flash-8b',
    'gemini-1.5-flash',
    'gemini-1.5-pro',
]
_GEMINI_RATE_LIMITED_UNTIL = 0  # epoch seconds; skip all calls until this passes

def call_gemini(prompt):
    """Call Gemini via REST API. Returns response text or None on failure."""
    global _GEMINI_API_KEY, _GEMINI_ACTIVE_MODEL, _GEMINI_RATE_LIMITED_UNTIL
    if _GEMINI_API_KEY is None:
        _GEMINI_API_KEY = os.environ.get('GOOGLE_API_KEY') or os.environ.get('GEMINI_API_KEY', '')
    if not _GEMINI_API_KEY:
        print(f"[{INSTANCE_ID}] Gemini API key missing")
        return None
    # Back-off: if we recently hit a rate limit, skip LLM entirely
    if _time.time() < _GEMINI_RATE_LIMITED_UNTIL:
        remaining = int(_GEMINI_RATE_LIMITED_UNTIL - _time.time())
        print(f"[{INSTANCE_ID}] Gemini back-off active ({remaining}s remaining), using fallback")
        return None

    models = ([_GEMINI_ACTIVE_MODEL] if _GEMINI_ACTIVE_MODEL else []) + _GEMINI_MODELS
    seen = set()
    for model in models:
        if not model or model in seen:
            continue
        seen.add(model)
        try:
            url = (f"https://generativelanguage.googleapis.com/v1beta/models/"
                   f"{model}:generateContent?key={_GEMINI_API_KEY}")
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.55, "maxOutputTokens": 512, "topP": 0.9}
            }
            resp = _requests.post(url, json=payload, timeout=35)
            if resp.status_code == 200:
                data = resp.json()
                candidates = data.get("candidates", [])
                if not candidates:
                    print(f"[{INSTANCE_ID}] Gemini {model} returned no candidates")
                    continue
                text = candidates[0]["content"]["parts"][0]["text"]
                if _GEMINI_ACTIVE_MODEL != model:
                    print(f"[{INSTANCE_ID}] Gemini active model: {model}")
                    _GEMINI_ACTIVE_MODEL = model
                return text.strip()
            elif resp.status_code == 429:
                print(f"[{INSTANCE_ID}] Gemini rate limit hit on {model}, entering 90s back-off")
                _GEMINI_RATE_LIMITED_UNTIL = _time.time() + 90
                return None
            elif resp.status_code in (404, 400):
                print(f"[{INSTANCE_ID}] Model {model} unavailable ({resp.status_code}), trying next...")
            else:
                print(f"[{INSTANCE_ID}] Gemini {model} error {resp.status_code}: {resp.text[:120]}")
        except Exception as e:
            print(f"[{INSTANCE_ID}] Gemini {model} exception: {e}")
    return None

# Museum Mappings
MUSEUM_NAMES = {
    "1": {"en": "King's Palace Museum", "fr": "Musée du Palais Royal", "rw": "Ingoro y'Abami i Nyanza"},
    "2": {"en": "Ethnographic Museum", "fr": "Musée Ethnographique", "rw": "Inzu ndangamurage i Huye"},
    "3": {"en": "Museum Ingabo", "fr": "Musée Ingabo", "rw": "Inzu ndangamurage Ingabo"},
    "4": {"en": "Campaign Against Genocide Museum", "fr": "Musée de la Campagne contre le Génocide", "rw": "Inzu ndangamurage yo guhagarika Jenoside"},
    "5": {"en": "Kandt House Museum", "fr": "Musée de la Maison Kandt", "rw": "Inzu ndangamurage ya Richard Kandt"},
    "6": {"en": "Environment Museum", "fr": "Musée de l'Environnement", "rw": "Inzu ndangamurage y'Ibidukikije"},
    "7": {"en": "Kigali Genocide Memorial", "fr": "Mémorial du Génocide de Kigali", "rw": "Urwibutso rwa Jenoside rwa Kigali"},
    "8": {"en": "Rwanda Art Museum", "fr": "Musée d'Art du Rwanda", "rw": "Inzu ndangamurage y'Ubuhanzi bw'u Rwanda"}
}

MUSEUM_MAPPING = {
    "1": "king's_palace_museum.txt",
    "2": "ethnographic_museum.txt",
    "3": "museum_ingabo.txt",
    "4": "campaign_against_genocide_museum.txt",
    "5": "kandt_house_museum.txt",
    "6": "environment_museum.txt",
    "7": "kigali_genocide_memorial.txt",
    "8": "rwanda_art_museum.txt"
}

# CORE FACTS (Comprehensive — covers 90% of visitor questions in EN/FR/RW without needing Gemini)
CORE_FACTS = {
    "1": { # King's Palace Museum
        "rw": {
            "history":    "Ingoro y'Abami i Nyanza igaragaza amateka y'ubwami bw'u Rwanda n'uburyo bwayoborwaga kugeza mu ntangiriro z'imyaka ya 1960. Irimo inzu y'ibyatsi yubatse mu buryo bwa gakondo n'inzu ya Art Deco y'umwami Mutara III Rudahigwa (yubatse mu 1931).",
            "hours":      "Ingoro ifunguwe kuva saa moya (7:00 AM) kugeza saa kumi n'ibiri (6:00 PM), kuva Kuwa Kabiri kugeza ku Cyumweru. Kuwa Mbere irafunze.",
            "location":   "Ingoro iherereye mu Akarere ka Nyanza, mu Ntara y'Amajyepfo, ku birometero 88 uvuye i Kigali.",
            "admission":  "Kwinjira birishwa. Umunyamahanga arishyura hafi ya USD 15, naho Umunyarwanda arishyura munsi yaho. Igiciro kirimo uruzinduko rw'umurongoreza.",
            "exhibits":   "Ibikomeye mu ngoro ni ingoro y'ibyatsi y'imigani (ingoro ya mbere y'umwami), ingoro ya Art Deco yubatse mu 1931, inka z'umwami (Inyambo) zirangwa n'amahembe maremare, n'ibikoresho by'ubwami nk'ingoma, inzige n'ibindi.",
            "transport":  "Ingoro iherereye mu Nyanza. Ushobora kuza n'imodoka ya gutumbagiza (moto) cyangwa taxi uvuye i Kigali. Nta bwinjiriro bushoboka n'inzira yo gutumbagiza bwite.",
            "inyambo":    "Inka z'umwami (Inyambo) zirangwa n'amahembe maremare cyane kandi zerekana uburanga n'umuco gakondo w'u Rwanda.",
            "rudahigwa":  "Umwami Mutara III Rudahigwa yavutse mu 1911 kandi yapfuye ku ya 25 Nyakanga 1959. Yabaye umwami w'u Rwanda kuva mu 1931 kugeza 1959 — imyaka 28 y'ubwami. Yakomeje imbere igihugu kandi yubatse ingoro ya kijyambere ya Art Deco iherereye hano i Nyanza mu 1931, igihe awugaruriwe n'Ababirigi.",
        },
        "fr": {
            "history":    "Le Musée du Palais Royal à Nyanza offre un aperçu fascinant du système monarchique rwandais, avec une réplique du palais traditionnel en chaume et le palais Art Déco du Roi Mutara III Rudahigwa (construit en 1931).",
            "hours":      "07h00 – 18h00 (Mardi au Dimanche). Fermé le Lundi.",
            "location":   "District de Nyanza, Province du Sud, à 88 km de Kigali.",
            "admission":  "L'entrée est payante et inclut une visite guidée. Tarif étranger : environ 15 USD. Des tarifs réduits sont disponibles pour les résidents rwandais.",
            "exhibits":   "Les expositions majeures comprennent : la réplique du palais traditionnel en chaume, le palais Art Déco de 1931, les vaches royales Inyambo aux cornes majestueuses, et les insignes royaux (tambours, boucliers, objets cérémoniels).",
            "transport":  "Depuis Kigali, des bus réguliers desservent Nyanza (environ 2h). Des taxis et motos sont disponibles localement. La route est goudronnée et accessible.",
            "inyambo":    "Le musée abrite les vaches royales Inyambo, célèbres pour leurs cornes majestueuses et leur dressage exceptionnel. Elles symbolisent la royauté rwandaise.",
            "rudahigwa":  "Le Roi Mutara III Rudahigwa est né en 1911 et est décédé le 25 juillet 1959. Il a régné sur le Rwanda de 1931 à 1959 — soit 28 ans de règne. Souverain réformateur et visionnaire, il a construit le palais Art Déco en 1931 lors de son intronisation imposée par les autorités coloniales belges.",
        },
        "en": {
            "history":    "The King's Palace Museum in Nyanza showcases Rwanda's rich monarchical history, featuring a traditional thatched palace replica and the modern Art Deco residence of King Mutara III Rudahigwa, built in 1931.",
            "hours":      "7:00 AM – 6:00 PM (Tuesday to Sunday). Closed on Mondays.",
            "location":   "Nyanza District, Southern Province, about 88 km south of Kigali.",
            "admission":  "Entry is paid and includes a guided tour. Foreign visitors pay approximately USD $15; Rwandan residents pay less. The guided tour is highly recommended.",
            "exhibits":   "Key exhibits: the traditional thatched palace (replica of the royal residence), the 1931 Art Deco palace, the famous Inyambo royal cattle with extraordinary long horns, and royal regalia including drums, shields, and ceremonial items.",
            "transport":  "From Kigali, take a bus to Nyanza (about 2 hours). Taxis and moto-taxis are available. The road is paved and in good condition.",
            "inyambo":    "The royal Inyambo cattle are the museum's living highlight — their extraordinary long horns and graceful demeanor make them a unique cultural symbol of Rwandan royalty.",
            "rudahigwa":  "King Mutara III Rudahigwa was born in 1911 and died on 25 July 1959. He reigned as King of Rwanda from 1931 to 1959 — 28 years on the throne. He was installed by Belgian colonial authorities after his father Yuhi V Musinga was deposed. A visionary ruler, he built the Art Deco palace here in 1931 and worked to modernise Rwanda while preserving its cultural heritage.",
        }
    },
    "2": { # Ethnographic Museum
        "rw": {
            "history":    "Inzu Ndangamurage y'i Huye ni imwe mu nzu zikomeye muri Afurika zirimo ibikoresho n'amateka by'umuco. Ifite imyitozo n'ibikoresho by'umuco w'u Rwanda mu bihe bitandukanye.",
            "hours":      "9:00 AM – 6:00 PM (Kuwa Kabiri - ku Cyumweru). Kuwa Mbere irafunze.",
            "location":   "Akarere ka Huye, mu Ntara y'Amajyepfo, ku birometero 130 uvuye i Kigali.",
            "admission":  "Kwinjira birishwa. Amafaranga ni make kandi bafite amafaranga agenwa k'amashuri. Uruzinduko rw'umurongoreza ruracyagenwa.",
            "exhibits":   "Inzu ndangamurage ifite ibice birindwi birimo: imyubakire ya kera, ingoma z'ubwami, ubukorikori bwa gakondo (Agaseke), imyenda y'umuco, intwaro za kera, n'ibikoresho by'umuziki.",
            "highlights": "Ibikomeye ni ingoma z'ubwami, amaseke (Agaseke), imyubakire y'uturere n'imibanire n'ibidukikije.",
            "transport":  "Huye iri ku birometero 130 uvuye i Kigali. Hari amabus ajyanye na Butare/Huye buri gihe. Taxi n'imodoka z'abigenga nabyo bishoboka.",
        },
        "fr": {
            "history":    "Le Musée Ethnographique de Huye est l'un des musées les plus riches d'Afrique, retraçant l'histoire du Rwanda à travers sept galeries thématiques et des milliers d'objets culturels.",
            "hours":      "09h00 – 18h00 (Mardi au Dimanche). Fermé le Lundi.",
            "location":   "District de Huye, Province du Sud, à 130 km de Kigali.",
            "admission":  "Entrée payante (tarif modéré). Des tarifs réduits sont disponibles pour les groupes scolaires. Visite guidée disponible.",
            "exhibits":   "Les sept galeries couvrent : l'architecture traditionnelle, les tambours royaux, la poterie et le tissage (Agaseke), les costumes traditionnels, les armes, les instruments de musique, et l'artisanat rwandais.",
            "highlights": "Les galeries présentent l'architecture traditionnelle, l'artisanat (Agaseke), et une collection unique de tambours royaux.",
            "transport":  "Depuis Kigali, des bus réguliers desservent Huye/Butare (environ 2h30). Taxis disponibles.",
        },
        "en": {
            "history":    "The Ethnographic Museum in Huye is one of Africa's largest and most significant museums, housing thousands of objects depicting Rwandan culture, history, and traditions across seven themed galleries.",
            "hours":      "9:00 AM – 6:00 PM (Tuesday to Sunday). Closed on Mondays.",
            "location":   "Huye District (formerly Butare), Southern Province, about 130 km from Kigali.",
            "admission":  "Entry is paid with a modest fee. Group and school rates are available. Guided tours are available and recommended.",
            "exhibits":   "Seven galleries cover: traditional architecture models, royal ceremonial drums (ingoma), Agaseke basket weaving, pottery, traditional costumes, weapons and tools, and traditional musical instruments.",
            "highlights": "Highlights include traditional architectural models, Agaseke baskets, and royal ceremonial drums.",
            "transport":  "From Kigali, regular buses run to Huye/Butare (about 2.5 hours). Taxis also available. The museum is in the town center.",
        }
    },
    "3": { # Museum Ingabo
        "rw": {
            "history":    "Ingoro Ingabo ni inzu ndangamurage ya mbere y'abigenga mu Rwanda. Iherereye ku musozi wa Rebero mu Mujyi wa Kigali, yashinzwe mu 2023 na King Ngabo kugira ngo yerekane amateka n'umuco binyuze mu buhanzi.",
            "hours":      "9:00 AM – 6:00 PM (ku Cyumweru kugeza kuwa Gatanu). Kuwa Gatandatu irafunze.",
            "location":   "Ku musozi wa Rebero (Kigali Cultural Village), KK 553 st, Kigali.",
            "admission":  "Kwinjira birishwa. Inzu ndangamurage kandi itanga inyigisho z'ubuhanzi n'ibikorwa by'ubumuntu. Reba urutonde rw'ibikorwa kuri website yabo.",
            "exhibits":   "Imurikagurisha rikomeye ni 'Inzira y'Inzitane' (Inzira y'Ubutwari) rigaragaza urugendo rw'u Rwanda rwo kwiyubaka mu myaka 30 (1994–2024) binyuze mu buhanzi n'amashusho. Kandi haritwa ubuhanzi bw'umuhanzi w'u Rwanda n'Afurika.",
            "founder":    "Ingoro Ingabo yashinzwe na King Ngabo, umuhanzi n'umushanditsi w'ikerekezo w'umunyarwanda washatse kwerekana amateka n'icyerekezo cy'u Rwanda binyuze mu buhanzi.",
            "inzira":     "Imurikagurisha rya 'Inzira y'Inzitane' rigaragaza urugendo rw'u Rwanda rwo kwiyubaka mu myaka 30 ishize binyuze mu buhanzi n'ibitekerezo. Ni imurikagurisha rirasira cyane.",
            "kamwe":      "Imurikagurisha 'KAMWE' ('A Hundred Days of Death') ni imurikagurisha rirasira rijyanye no kwibuka iminsi 100 ya Jenoside yakorewe Abatutsi mu 1994. Ryerekana uburyo ubugeni bushobora gutanga isomo, kwibuka no gutunganya ibikomere by'umuryango wose. Mu murikagurisha harimo ibihangano n'ibikoresho bigaragaza agahinda, ukwibuka inzirakarengane, no gukomeza kwigira ku mateka kugira ngo bitazongera. Si inzu ndangamurage y'intambara ya RPA ku CND — aho ni ahantu h'ubuhanzi na kamere y'urwibutso muri Ingoro Ingabo i Rebero.",
            "different_wounds": "Imurikagurisha 'DIFFERENT, SAME WOUNDS' (2025, riguma kugeza ku ya 29 Mata 2026) ry'umuhanzi King Ngabo rijyanye n'ubwiyunge mu bwoko: twita ku bitandukanye by'uruhu, ubwoko, n'umuco, ariko tureba uburyo dukoresha ibikomere twese dukoresha. Insanganyamatsiko: ubumwe mu bwoko, inzitwazo z'isi yose, no gukira hamwe.",
            "transport":  "Ingoro iherereye i Rebero, Kigali. Ushobora gufata imodoka ya gutumbagiza (moto) cyangwa taxi uvuye mu gace ka Kigali.",
        },
        "fr": {
            "history":    "Le Musée Ingabo est le premier musée privé du Rwanda, fondé en 2023 par l'artiste King Ngabo sur la Colline de Rebero à Kigali, dédié à la narration africaine contemporaine à travers l'art.",
            "hours":      "09h00 – 18h00 (Dimanche au Vendredi). Fermé le Samedi.",
            "location":   "Colline de Rebero (Kigali Cultural Village), KK 553 st, Kigali.",
            "admission":  "Entrée payante. Le musée propose également des ateliers artistiques et des événements culturels réguliers. Consultez leur site web pour le programme.",
            "exhibits":   "L'exposition phare 'Inzira y'Inzitane' (Chemin de la Résilience) documente les 30 ans de reconstruction du Rwanda (1994–2024) à travers des installations artistiques immersives, peintures et multimédia.",
            "founder":    "Le musée a été fondé par l'artiste King Ngabo, entrepreneur culturel rwandais engagé dans la promotion de l'art africain contemporain et de la narration visuelle.",
            "inzira":     "L'exposition 'Inzira y'Inzitane' est une installation artistique immersive qui retrace 30 ans de résilience et de reconstruction du Rwanda (1994-2024). C'est l'exposition principale du musée.",
            "kamwe":      "KAMWE (« Cent jours de mort ») est une exposition immersive au Musée Ingabo qui porte sur les cent jours du génocide contre les Tutsi en 1994. Elle utilise l'art pour explorer la mémoire collective, le deuil, la survie et l'importance de se souvenir. Les visiteurs découvrent des installations qui honorent les victimes et invitent à la réflexion. Ce n'est pas le musée militaire de la campagne de libération au Parlement — c'est un espace artistique et mémoriel au village culturel de Rebero.",
            "different_wounds": "« Different, Same Wounds » (2025, jusqu'au 29 avril 2026) par King Ngabo explore l'unité au-delà des différences visibles (couleur de peau, race, culture) et les blessures partagées de l'humanité : diversité, guérison collective et lien entre les peuples.",
            "transport":  "Le musée est sur la Colline de Rebero à Kigali. Accessible en moto-taxi ou en taxi depuis le centre-ville.",
        },
        "en": {
            "history":    "Museum Ingabo is Rwanda's first private museum, founded in 2023 by artist King Ngabo on Rebero Hill in Kigali. It focuses on storytelling, contemporary African art, and Rwanda's cultural journey.",
            "hours":      "9:00 AM – 6:00 PM (Sunday to Friday). Closed on Saturdays.",
            "location":   "Rebero Hill (Kigali Cultural Village), KK 553 st, Kigali.",
            "admission":  "Entry is paid. The museum also hosts regular art workshops and cultural events. Check their social media for the current schedule.",
            "exhibits":   "The signature exhibition is 'Inzira y'Inzitane' (Path of Resilience), an immersive installation documenting Rwanda's 30-year reconstruction journey (1994–2024) through art, paintings, and multimedia. The museum also features contemporary Rwandan and African artists.",
            "founder":    "Founded by visionary Rwandan artist King Ngabo, the museum was created to celebrate Rwandan heritage and tell the story of Africa's resilience through creative expression.",
            "inzira":     "The 'Inzira y'Inzitane' (Path of Resilience) exhibition is the museum's centerpiece — an immersive art journey showing Rwanda's 30-year transformation from tragedy to triumph, told through powerful visual storytelling.",
            "kamwe":      "KAMWE ('A Hundred Days of Death') is an installation exhibition at Museum Ingabo that reflects on the hundred days of the 1994 Genocide against the Tutsi. Through art and installations it explores collective memory, trauma, survival, remembrance, and education toward never again. Visitors see works that honour victims and invite quiet reflection. Note: this is not the Campaign Against Genocide Museum at Parliament — Ingabo is a private art museum at Rebero, Kigali Cultural Village.",
            "different_wounds": "'Different, Same Wounds' (2025, running through 29 April 2026) by King Ngabo asks us to look past visible differences like skin colour and culture to our shared humanity and shared wounds — themes of unity in diversity, healing, and global connection.",
            "transport":  "Located on Rebero Hill, Kigali. Take a moto-taxi or taxi from anywhere in Kigali city center.",
        }
    },
    "4": { # Campaign Against Genocide Museum
        "rw": {
            "history":    "Inzu ndangamurage yo guhagarika Jenoside iri mu nyubako y'Inteko Ishinga Amategeko (CND) i Kigali. Igaragaza urugamba rw'iminsi 100 rwa RPA rwagamijwe guhagarika Jenoside yakorewe Abatutsi mu 1994.",
            "hours":      "8:00 AM – 5:00 PM (Kuwa Mbere kugeza Kuwa Gatanu). Irafunzwe ku Cyumweru n'iminsi mikuru.",
            "location":   "Inyubako y'Inteko Ishinga Amategeko (CND), Kigali (mu gace ka kigali). Iherereye hafi ya hoteli nyinshi z'i Kigali.",
            "admission":  "Kwinjira ni ubuntu (birishwa na zero). Uruzinduko rw'umurongoreza ruragaragara kandi rurasabwa kugira ngo usobanukirwe neza amateka.",
            "exhibits":   "Inzu ndangamurage irimo: ibikoresho by'intambara bya RPA (imodoka z'intambara, intwaro), amafoto y'urugamba rw'iminsi 100, imurikagurisha ry'igitero cy'i CND (ingabo 600 z'RPA), n'amateka y'intwari nk'Jenerali Paul Kagame.",
            "cnd":        "Mu 1994, ingabo 600 z'RPA zari zifunze mu nyubako ya CND. Jenoside itangiye, RPA yatangiye urugamba rwo guhagarika Jenoside, ikora ku CND, maze ikiza abazunguye n'Abatutsi bagahunga.",
            "transport":  "Inzu ndangamurage iherereye mu gace ka kigali, hafi ya hoteli nyinshi z'umurwa mukuru. Ushobora kuyigera n'amaguru, taxi cyangwa imodoka ya gutumbagiza.",
        },
        "fr": {
            "history":    "Le Musée de la Campagne contre le Génocide (CAG), situé dans l'ancien bâtiment du CND (actuel Parlement), retrace la campagne militaire de 100 jours de l'APR pour mettre fin au génocide de 1994.",
            "hours":      "08h00 – 17h00 (Lundi au Vendredi). Fermé le week-end et les jours fériés.",
            "location":   "Bâtiment du Parlement (ancien CND), centre-ville de Kigali, à proximité des grands hôtels.",
            "admission":  "L'entrée est GRATUITE. Des visites guidées sont disponibles et vivement recommandées pour le contexte historique complet.",
            "exhibits":   "Les expositions comprennent : équipements militaires de l'APR (véhicules blindés, armes), archives photographiques de la campagne de 100 jours, l'exposition du siège du CND, et les profils des commandants dont le Général Paul Kagame.",
            "cnd":        "En 1994, 600 soldats de l'APR étaient assiégés au CND. Quand le génocide a commencé, l'APR a lancé une campagne de libération depuis le nord, secourant les assiégés et les civils tutsi en 100 jours.",
            "transport":  "Situé au cœur de Kigali, à distance de marche des grands hôtels. Accessible en taxi, moto-taxi ou à pied.",
        },
        "en": {
            "history":    "The Campaign Against Genocide Museum is located in the Parliament Building (former CND) in Kigali. It documents the 100-day RPA military campaign that ended the 1994 Genocide against the Tutsi.",
            "hours":      "8:00 AM – 5:00 PM (Monday to Friday). Closed weekends and public holidays.",
            "location":   "Parliament Building (former CND), Kigali City Center, near major hotels.",
            "admission":  "Admission is FREE. Guided tours are available and highly recommended for full historical context.",
            "exhibits":   "Key exhibits include military equipment used by the RPA (armored vehicles, weapons, communication gear), photographic archives of the 100-day campaign, the CND Battle Exhibit, a timeline of the liberation, and profiles of commanders including General Paul Kagame.",
            "cnd":        "In 1994, 600 RPA soldiers were besieged at the CND. When the genocide began, the RPA launched a liberation campaign from the north, rescuing those at the CND and ending the genocide in 100 days.",
            "transport":  "Located in the heart of Kigali city center, walking distance from major hotels. Accessible by taxi, moto-taxi, or on foot.",
        }
    },
    "5": { # Kandt House Museum
        "rw": {
            "history":    "Inzu y'Ingando ya Kandt ni inzu ndangamurage iri mu nzu yahoze ari iy'Umudage Richard Kandt, uwashinze umujyi wa Kigali mu 1907. Irimo amateka kamere y'u Rwanda n'igihe cy'ubwami bw'Abadage.",
            "hours":      "9:00 AM – 5:00 PM (Kuwa Kabiri - ku Cyumweru). Kuwa Mbere irafunze.",
            "location":   "Nyarugenge, Kigali (hafi ya kigo cy'umujyi).",
            "admission":  "Kwinjira birishwa (amafaranga make). Ni inzu imwe mu nzu za kera cyane i Kigali (yubatse mu 1908).",
            "exhibits":   "Inzu ndangamurage irimo ibintu bya Richard Kandt bwite, amakusanyo y'amateka kamere (inyamaswa n'inyoni zifatirwa), mapu n'amafoto y'igihe cy'ubukoloni, ibiremwa by'ibitaka, n'amateka y'ishingwa rya Kigali mu 1907.",
            "kandt":      "Richard Kandt yari muganga w'Ubudage wahamagawe kuba Umuyobozi wa mbere w'u Rwanda mu ngoma ya Abadage. Yashinze Kigali nk'umurwa mukuru w'u Rwanda mu 1907.",
            "transport":  "Inzu ndangamurage iherereye i Nyarugenge, Kigali. Ushobora kuyigera uturutse mu gace k'umujyi nawe.",
        },
        "fr": {
            "history":    "La Maison Kandt, ancienne demeure du Dr. Richard Kandt, retrace la fondation de Kigali en 1907 et explore l'histoire naturelle du Rwanda pendant l'ère coloniale allemande.",
            "hours":      "09h00 – 17h00 (Mardi au Dimanche). Fermé le Lundi.",
            "location":   "Nyarugenge, Kigali (centre-ville historique).",
            "admission":  "Entrée payante (tarif modéré). L'un des bâtiments les plus anciens de Kigali (construit en 1908).",
            "exhibits":   "Les expositions comprennent : les effets personnels de Richard Kandt, une collection d'histoire naturelle (animaux et oiseaux préservés), des cartes et photographies de l'époque coloniale, des spécimens géologiques, et l'histoire de la fondation de Kigali.",
            "kandt":      "Richard Kandt (1867–1918) était un médecin et explorateur allemand qui a fondé Kigali comme capitale administrative du Rwanda en 1907 et fut le premier Résident allemand du Rwanda.",
            "transport":  "Situé à Nyarugenge, quartier historique de Kigali. Accessible à pied depuis le centre-ville ou en moto-taxi.",
        },
        "en": {
            "history":    "The Kandt House Museum is the former home of Dr. Richard Kandt, the German physician who founded Kigali in 1907. It is one of the oldest buildings in Kigali and explores Rwanda's natural history and colonial era.",
            "hours":      "9:00 AM – 5:00 PM (Tuesday to Sunday). Closed on Mondays.",
            "location":   "Nyarugenge, Kigali city center (historic quarter).",
            "admission":  "Entry is paid (modest fee). The building itself is one of the oldest in Kigali, built in 1908.",
            "exhibits":   "Displays include Richard Kandt's personal belongings, natural history collections (preserved animals and birds from colonial Rwanda), colonial-era maps and photographs, geological specimens, and the story of Kigali's founding in 1907.",
            "kandt":      "Dr. Richard Kandt (1867–1918) was a German physician and explorer who became the first Resident of Rwanda under German rule. He chose the hill of Kigali as Rwanda's administrative capital in 1907.",
            "transport":  "Located in Nyarugenge, central Kigali. Easily reachable by moto-taxi or on foot from the city center.",
        }
    },
    "6": { # Environment Museum
        "rw": {
            "history":    "Inzu ndangamurage y'Ibidukikije i Karongi ni iyo yonyine muri Afurika igamijwe gusohora ibijyanye n'ibidukikije n'amateka kamere y'u Rwanda. Iherereye hafi y'ikiyaga cya Kivu.",
            "hours":      "9:00 AM – 5:00 PM (Kuwa Kabiri - ku Cyumweru). Kuwa Mbere irafunze.",
            "location":   "Akarere ka Karongi (Kibuye), Intara y'Uburengerazuba, ku birometero 90 uvuye i Kigali hafi y'ikiyaga cya Kivu.",
            "admission":  "Kwinjira birishwa (amafaranga make). Inzu ndangamurage iherereye ahantu heza hafi y'ikiyaga cya Kivu, bigatuma ushobora guhubuka no kureba ikiyaga.",
            "exhibits":   "Ibikomeye ni: irima ry'imbuto z'imbuto z'akaravumu (indwara z'ibibazo 100+ z'imitsi), imurikagurisha ry'ibinyabuzima (ingagi, inyoni, n'ibiti by'inzaratsi), amateka y'ibirunga bya Virunga, n'amakuru y'inzuzi z'Umuganura (Nile).",
            "highlights": "Ifite irima ry'imbuto z'imbuto z'akaravumu hejuru y'inzu, imurikagurisha ry'ibinyabuzima bidasanzwe byo mu Rwanda harimo ingagi z'intare, n'amakuru y'ikiyaga cya Kivu.",
            "gorilla":    "U Rwanda rutuye hafi kimwe cya kabiri cy'itunga ry'ingagi z'intare (mountain gorillas) zose ku isi. Inzu ndangamurage igaragaza ibikorwa byo kurinda ingagi n'ibindi binyabuzima bidasanzwe.",
            "transport":  "Karongi iri ku birometero 90 uvuye i Kigali (inzira ya Muhanga). Hari amabus yo gutumbagiza. Urugendo rurumvikana neza kuko inzira ni nziza kandi uranga neza.",
        },
        "fr": {
            "history":    "Le Musée de l'Environnement de Karongi est le seul musée entièrement dédié à l'environnement naturel sur le continent africain. Il est situé près du Lac Kivu.",
            "hours":      "09h00 – 17h00 (Mardi au Dimanche). Fermé le Lundi.",
            "location":   "District de Karongi (Kibuye), Province de l'Ouest, à 90 km de Kigali sur les rives du Lac Kivu.",
            "admission":  "Entrée payante (tarif modéré). Le cadre au bord du Lac Kivu en fait une visite agréable à combiner avec une excursion sur le lac.",
            "exhibits":   "Galeries principales : Géologie (Rift Albertin, volcans Virunga), Biodiversité (gorilles de montagne, singes dorés, 700+ espèces d'oiseaux), Jardin d'herbes médicinales sur le toit (100+ espèces), et Galerie des eaux (Lac Kivu, source du Nil).",
            "highlights": "Le musée comprend un jardin d'herbes médicinales indigènes sur le toit (100+ espèces) et une galerie biodiversité présentant les gorilles de montagne et les forêts rwandaises.",
            "gorilla":    "Le Rwanda abrite environ la moitié de la population mondiale des gorilles de montagne. Le musée documente les efforts de conservation menés par le Rwanda pour protéger ces animaux emblématiques.",
            "transport":  "Depuis Kigali, route de Muhanga jusqu'à Karongi (90 km, environ 2h). Des bus réguliers sont disponibles. La route est bien entretenue avec de beaux panoramas.",
        },
        "en": {
            "history":    "The Environment Museum in Karongi is Africa's only museum entirely dedicated to the natural environment. It sits near the shores of Lake Kivu and explores Rwanda's extraordinary biodiversity, geology, and conservation story.",
            "hours":      "9:00 AM – 5:00 PM (Tuesday to Sunday). Closed on Mondays.",
            "location":   "Karongi District (Kibuye), Western Province, about 90 km from Kigali on the shores of Lake Kivu.",
            "admission":  "Entry is paid (modest fee). Combine with a visit to Lake Kivu for a full day out.",
            "exhibits":   "Main galleries: Geology Gallery (Albertine Rift, Virunga volcanoes), Biodiversity Gallery (mountain gorillas, golden monkeys, 700+ bird species), rooftop indigenous Herbal Garden (100+ medicinal plant species), and the Water & Lakes Gallery (Lake Kivu, Nile source).",
            "highlights": "Highlights include the rooftop indigenous herbal garden, mountain gorilla conservation displays, geological rock and mineral collections, and exhibits on Rwanda's role as a source of the Nile River.",
            "gorilla":    "Rwanda is home to roughly half the world's mountain gorilla population. The museum documents Rwanda's world-class conservation efforts to protect these critically endangered animals.",
            "transport":  "From Kigali, take the Muhanga road to Karongi (90 km, about 2 hours). Regular buses run this route. Beautiful scenic drive.",
        }
    },
    "7": { # Kigali Genocide Memorial
        "rw": {
            "history":    "Urwibutso rwa Jenoside rwa Kigali ruherereye ku musozi wa Gisozi i Kigali. Ni ahantu ho gutuza abarenga 250,000 b'inzirakarengane baguye mu Jenoside yakorewe Abatutsi mu 1994. Kandi ni ahantu h'inyigisho n'ubuvugizi.",
            "hours":      "8:00 AM – 5:00 PM (buri munsi, harimo iminsi mikuru).",
            "location":   "Gisozi, Kigali (KN 3 Rd). Kwinjira ni ubuntu.",
            "admission":  "Kwinjira ni ubuntu (birishwa na zero). Basaba abasura kwubaha ahantu h'urubuho. Uruzinduko rw'umurongoreza ruragaragara.",
            "exhibits":   "Urwibutso rufite ibice bikuru bitatu: imibiri y'inzirakarengane igumijwe hanze (abarenga 250,000), imusée irimo amafoto, ubugabo n'inzira z'amateka y'itsembabwoko, n'agace k'urwibutso k'abana baguye muri jenoside.",
            "kwibuka":    "Buri mwaka ku wa 7 Mata, u Rwanda rwibuka inzirakarengane za Jenoside mu birori by'igihugu bya Kwibuka biganywa ku rwibutso rwa Gisozi.",
            "children":   "Urwibutso rw'abana ni agace k'urwibutso kakoreshwa inzira z'amashusho n'amakuru yerekana ibyago byabayeho ku bana mu gihe cya Jenoside. Ni agace gafata umutima cyane.",
            "transport":  "Urwibutso ruherereye i Gisozi, Kigali. Ushobora kugera aho uturutse mu gace kose ka Kigali n'imodoka ya gutumbagiza (moto) cyangwa taxi.",
        },
        "fr": {
            "history":    "Le Mémorial du Génocide de Kigali à Gisozi est le lieu de sépulture de plus de 250 000 victimes du génocide contre les Tutsi de 1994. C'est aussi un centre éducatif dédié à la mémoire et à la prévention des génocides.",
            "hours":      "08h00 – 17h00 (tous les jours, y compris les jours fériés).",
            "location":   "Gisozi Hill, Kigali (KN 3 Rd). Entrée gratuite.",
            "admission":  "L'entrée est GRATUITE. Le mémorial demande respect et silence de tous les visiteurs. Visites guidées disponibles.",
            "exhibits":   "Le mémorial comprend trois sections principales : les jardins funéraires extérieurs (lieu de repos de 250 000+ victimes), les galeries d'exposition intérieures (photos, témoignages, chronologie du génocide), et le Mémorial des Enfants.",
            "kwibuka":    "Chaque année le 7 avril, le Rwanda commémore les victimes du génocide lors des cérémonies nationales de Kwibuka à Gisozi. Ces cérémonies sont diffusées dans le monde entier.",
            "children":   "Le Mémorial des Enfants est une section dédiée aux victimes enfants, utilisant des photographies et témoignages pour documenter leur vie et leur mort pendant le génocide. C'est la section la plus émouvante.",
            "transport":  "Situé à Gisozi, Kigali. Accessible en taxi, moto-taxi ou bus depuis tout Kigali.",
        },
        "en": {
            "history":    "The Kigali Genocide Memorial at Gisozi is the burial site for over 250,000 victims of the 1994 Genocide against the Tutsi. It is both a sacred place of remembrance and an important educational center.",
            "hours":      "8:00 AM – 5:00 PM (open every day including public holidays).",
            "location":   "Gisozi Hill, Kigali (KN 3 Rd). Free admission.",
            "admission":  "Admission is FREE. The memorial requests respectful and quiet behavior. Guided tours are available.",
            "exhibits":   "The memorial has three main areas: outdoor burial gardens (resting place for 250,000+ victims), indoor exhibition galleries (photos, survivor testimonies, genocide history and international context), and the Children's Memorial section.",
            "kwibuka":    "Every April 7th, Rwanda holds national Kwibuka (remembrance) ceremonies here. The memorial educates visitors about the genocide's causes, events, and the global importance of 'Never Again'.",
            "children":   "The Children's Memorial is one of the most moving sections — it uses photographs and detailed accounts to honor individual child victims, giving them names, faces, and remembered stories.",
            "transport":  "Located at Gisozi, accessible from anywhere in Kigali by moto-taxi or taxi. About 3 km from the city center.",
        }
    },
    "8": { # Rwanda Art Museum
        "rw": {
            "history":    "Inzu ndangamurage y'Ubuhanzi bw'u Rwanda iri mu nzu yahoze ari kwa Perezida i Kanombe, Kigali. Ni inzu yahoze iri iya Perezida Juvénal Habyarimana. Irimo amakusanyo y'ubuhanzi bw'umwimerere harimo Imigongo.",
            "hours":      "9:00 AM – 5:00 PM (Kuwa Kabiri - ku Cyumweru). Kuwa Mbere irafunze.",
            "location":   "Kanombe, Kigali (hafi y'ikibuga cy'indege cy'i Kigali).",
            "admission":  "Kwinjira birishwa. Inzu ndangamurage ifite duka ry'ubuhanzi aho ushobora kugura Imigongo n'ibikoresho by'ubugeni bw'umwimerere.",
            "exhibits":   "Ibikomeye ni: amakusanyo y'Imigongo (ubuhanzi gakondo bw'u Rwanda), ubuhanzi bw'ubu bw'inyandiko n'ibisusuruko by'abanyarwanda, ibiraro by'imodoka za Perezida, n'ibiraro by'abafotografi bagaragaza u Rwanda rushya.",
            "imigongo":   "Imigongo ni ubuhanzi gakondo bw'u Rwanda bwatangijwe na Umutware Kakira wo muri Gisaka. Bukoresheje imizigo y'inka bukora imishinga y'imigani. Zigizago mu Imigongo zisobanura 'abagore babiri bafatanye intoki'.",
            "kakira":     "Umutware Kakira wo muri Gisaka ni we watangije ubuhanzi bwa Imigongo. Yatangiye gutura imishinga y'imigani ku nzu z'inzu y'ubwami, ubuhanzi bwasakaye mu Rwanda hose.",
            "transport":  "Inzu ndangamurage iherereye i Kanombe, hafi y'ikibuga cy'indege. Ushobora kuza na taxi cyangwa imodoka ya gutumbagiza uvuye mu gace kose ka Kigali.",
        },
        "fr": {
            "history":    "Le Musée d'Art du Rwanda est installé dans l'ancien Palais Présidentiel à Kanombe, résidence du Président Juvénal Habyarimana. Il célèbre l'art contemporain rwandais et les traditions artistiques ancestrales.",
            "hours":      "09h00 – 17h00 (Mardi au Dimanche). Fermé le Lundi.",
            "location":   "Kanombe, Kigali (à côté de l'Aéroport International de Kigali).",
            "admission":  "Entrée payante. Le musée dispose d'une boutique vendant de l'art Imigongo authentique et d'autres artisanats rwandais.",
            "exhibits":   "Les expositions majeures : la plus grande collection d'Imigongo du Rwanda, peintures et sculptures contemporaines rwandaises, galerie des voitures présidentielles, et expositions temporaires d'artistes émergents.",
            "imigongo":   "L'Imigongo est un art traditionnel unique rwandais, originaire du Prince Kakira de Gisaka. Il utilise de la bouse de vache séchée et des pigments naturels pour créer des motifs géométriques. Le zigzag symbolise 'deux femmes se tenant la main'.",
            "kakira":     "Le Prince Kakira de Gisaka est le fondateur de l'art Imigongo. Il a découvert la technique d'utiliser la bouse de vache pour créer des motifs géométriques, qui s'est ensuite répandue dans tout le Rwanda.",
            "transport":  "Situé à Kanombe, près de l'aéroport international. Accessible en taxi ou moto-taxi depuis tout Kigali.",
        },
        "en": {
            "history":    "The Rwanda Art Museum is housed in the former Presidential Palace at Kanombe — the former residence of President Juvénal Habyarimana. It celebrates contemporary Rwandan art and the country's rich artistic traditions.",
            "hours":      "9:00 AM – 5:00 PM (Tuesday to Sunday). Closed on Mondays.",
            "location":   "Kanombe, Kigali (near Kigali International Airport).",
            "admission":  "Entry is paid. The museum shop sells authentic Imigongo artworks and traditional Rwandan crafts — a great place to take home a unique souvenir.",
            "exhibits":   "Key exhibits: Rwanda's finest Imigongo collection, contemporary Rwandan paintings and sculptures, the presidential car gallery (vehicles used by former presidents), and rotating exhibitions by emerging Rwandan artists.",
            "imigongo":   "Imigongo is Rwanda's iconic traditional art form, originating with Prince Kakira of Gisaka. Made from dried cow dung with natural pigments, it features bold geometric patterns. The zigzag pattern represents 'two women holding hands' — a symbol of unity.",
            "kakira":     "Prince Kakira of Gisaka originated the Imigongo art form using dried cow dung to create geometric decorative patterns on palace walls. This tradition spread across Rwanda and is now one of the country's most celebrated cultural exports.",
            "transport":  "Located at Kanombe, near Kigali International Airport. Take any taxi or moto-taxi from Kigali city center.",
        }
    }
}

# Persona Wrappers (Conversational Framing)
PERSONA_WRAPPERS = {
    'rw': [
        "Nshingiye ku manyandiko dufite hano mu nzu ndangamurage: {text} Hari ikindi nkwifuriza kumenya?",
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
chroma_client = None
collection = None

def get_db():
    global chroma_client, collection
    if collection is None:
        print(f"[{INSTANCE_ID}] Lazy-loading ChromaDB...")
        import chromadb
        from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
        chroma_client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
        # Use ChromaDB's built-in ONNX-based embedding (no PyTorch dependency)
        ef = DefaultEmbeddingFunction()
        # New collection name forces fresh re-index with all 8 museums
        collection = chroma_client.get_or_create_collection(
            name="rwanda_museums_v4_2",
            embedding_function=ef
        )
        if collection.count() == 0:
            initialize_vector_store()
        print(f"[{INSTANCE_ID}] ChromaDB ready — {collection.count()} chunks indexed")
    return collection

def clean_text(text):
    if not text: return ""
    # Remove markdown headers
    text = re.sub(r'^#+\s*(\d+\.)?\s*', '', text, flags=re.MULTILINE)
    # Remove bold/italic markers
    text = text.replace('**', '').replace('__', '').replace('*', '')
    # Remove knowledge-base annotation tags like [RWANDA], [EN], [FR], [RW], [FRANÇAIS], [KINYARWANDA]
    text = re.sub(r'\[[A-Z\xC0-\xFF][A-Z\xC0-\xFFa-z\u00e0-\u00ff]{1,19}\]\s*', '', text)
    # Remove horizontal rules
    text = re.sub(r'^-{3,}$', '', text, flags=re.MULTILINE)
    # Convert leading "- " bullet points to clean sentences
    text = re.sub(r'^\s*-\s+', '', text, flags=re.MULTILINE)
    # Collapse multiple blank lines
    text = re.sub(r'\n{3,}', '\n\n', text)
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
    docs, metas, ids = load_knowledge_base()
    if docs:
        # ChromaDB handles embeddings internally via the collection's embedding function
        # Process in batches to avoid memory issues
        BATCH = 50
        for i in range(0, len(docs), BATCH):
            collection.add(
                documents=docs[i:i+BATCH],
                metadatas=metas[i:i+BATCH],
                ids=ids[i:i+BATCH]
            )
    print(f"[{INSTANCE_ID}] Database re-indexed: {collection.count()} chunks across 8 museums")

def apply_persona(text, lang):
    wrappers = PERSONA_WRAPPERS.get(lang, PERSONA_WRAPPERS['en'])
    return random.choice(wrappers).format(text=clean_text(text))

def resolve_core_fact(query, museum_id, language):
    """
    Returns (route_key, response_text) where route_key identifies which rule matched.
    Used for reproducible evaluation; get_core_fact returns only the text.
    route_key is None when no curated fact matches (LLM / RAG path).
    """
    m_id = str(museum_id)
    if m_id not in CORE_FACTS:
        return (None, None)
    lang_facts = CORE_FACTS[m_id].get(language, CORE_FACTS[m_id].get('en', {}))
    q_low = (query.lower().strip()
             .replace("\u2019", " ").replace("\u2018", " ").replace("'", " ")
             .replace("\u201c", " ").replace("\u201d", " "))

    if any(k in q_low for k in [
        "what do you call", "how do we call", "how do you call", "what is it called",
        "what is this called", "what is the name", "name in kinyarwanda",
        "name in french", "name in english", "kinyarwanda name", "french name",
        "english name", "translate the name", "nom en", "appelle", "s appelle",
        "comment appelle", "witwa iki", "izina ryayo", "izina ry", "izina muri",
        "izina mu", "bita iki", "bita gute", "ibitwa iki"
    ]):
        m_info = MUSEUM_NAMES.get(m_id, {})
        en_name = m_info.get('en', '')
        fr_name = m_info.get('fr', '')
        rw_name = m_info.get('rw', '')
        if language == 'rw':
            text = (f"Iyi nzu ndangamurage yitwa '{rw_name}' mu Kinyarwanda. "
                    f"Mu Cyongereza ni '{en_name}', kandi mu Gifaransa ni '{fr_name}'.")
        elif language == 'fr':
            text = (f"Ce musée s'appelle '{fr_name}' en français. "
                    f"En anglais : '{en_name}', et en kinyarwanda : '{rw_name}'.")
        else:
            text = (f"In English it is called '{en_name}'. "
                    f"In French: '{fr_name}', and in Kinyarwanda: '{rw_name}'.")
        return ("museum_name", text)

    if any(k in q_low for k in ["rudahigwa", "mutara"]):
        v = lang_facts.get("rudahigwa")
        return ("rudahigwa", v) if v else (None, None)
    if any(k in q_low for k in ["kakira", "prince kakira", "gisaka", "originate", "who created imigongo", "qui a cree", "iboneka he"]):
        v = lang_facts.get("kakira")
        return ("kakira", v) if v else (None, None)
    if any(k in q_low for k in ["kandt", "richard kandt", "colonial", "founded kigali", "fonde kigali", "yashinze kigali"]):
        v = lang_facts.get("kandt")
        return ("kandt", v) if v else (None, None)
    founder_sub = ["king ngabo", "founder", "fondateur", "createur", "qui a fonde", "who founded", "washinze", "who started", "qui a cree le musee"]
    if any(k in q_low for k in founder_sub) or re.search(r"\bngabo\b", q_low):
        v = lang_facts.get("founder")
        return ("founder", v) if v else (None, None)

    if any(k in q_low for k in ["inzira", "inzitane", "path of resilience", "resilience", "reconstruction", "parcours"]):
        v = lang_facts.get("inzira")
        return ("inzira", v) if v else (None, None)
    if m_id == "3":
        if any(k in q_low for k in [
            "kamwe", "camwe", "hundred days of death", "a hundred days of",
            "100 days of death", "exhibition kamwe", "kamwe exhibition", "the kamwe",
            "imurikagurisha kamwe", "about kamwe", "tell me about kamwe", "what is kamwe",
            "qu est ce que kamwe", "c est quoi kamwe",
        ]):
            val = lang_facts.get("kamwe")
            if val:
                return ("kamwe", val)
        if any(k in q_low for k in ["iminsi 100", "cent jours de", "100-day", "100 days", "cent jours"]):
            val = lang_facts.get("kamwe")
            if val:
                return ("kamwe", val)
        if any(k in q_low for k in [
            "different same wounds", "same wounds", "different, same", "unity in diversity",
            "avril 2026", "april 2026", "exhibition 3", "third exhibition",
        ]):
            val = lang_facts.get("different_wounds")
            if val:
                return ("different_wounds", val)
    if any(k in q_low for k in ["imigongo", "zigzag", "cow dung", "bouse de vache", "geometric", "geometrique", "cow art"]):
        v = lang_facts.get("imigongo")
        return ("imigongo", v) if v else (None, None)
    if any(k in q_low for k in ["inyambo", "inka z umwami", "royal cattle", "royal cow", "vache royale", "long horn", "ingumba"]):
        v = lang_facts.get("inyambo")
        return ("inyambo", v) if v else (None, None)
    if any(k in q_low for k in ["agaseke", "basket", "panier", "weaving", "tissage", "ingoma", "drums", "tambour"]):
        v = lang_facts.get("highlights") or lang_facts.get("exhibits")
        return ("exhibits_highlights", v) if v else (None, None)
    if any(k in q_low for k in ["gorilla", "gorille", "ingagi", "mountain gorilla", "golden monkey", "biodiversity", "biodiversite"]):
        v = lang_facts.get("gorilla") or lang_facts.get("highlights")
        return ("gorilla", v) if v else (None, None)
    if any(k in q_low for k in ["herbal", "herbe", "medicinal plant", "plante medicinale", "rooftop garden", "akaravumu"]):
        v = lang_facts.get("highlights") or lang_facts.get("exhibits")
        return ("exhibits_highlights", v) if v else (None, None)
    if any(k in q_low for k in ["children memorial", "memorial enfants", "urwibutso rw abana", "child victim"]):
        v = lang_facts.get("children")
        return ("children", v) if v else (None, None)

    if m_id == "4":
        if any(k in q_low for k in ["cnd", "siege", "rescue", "100 days", "100-day", "cent jours", "iminsi 100", "liberation campaign", "rpa campaign"]):
            v = lang_facts.get("cnd")
            if v:
                return ("cnd", v)
    if any(k in q_low for k in ["kwibuka", "commemor", "april 7", "7 april", "7 mata", "remembrance", "commemoration", "memorial day"]):
        v = lang_facts.get("kwibuka")
        if v:
            return ("kwibuka", v)

    if any(k in q_low for k in [
        "admission", "entrance fee", "entry fee", "ticket", "cost", "price",
        "how much", "free", "gratuit", "amafaranga", "kwinjira", "tarif",
        "billet", "payer", "n'amafaranga angahe", "birishwa angahe",
        "angahe", "ni angahe", "kwishyura", "amafaranga yo kwinjira",
        "ibiciro", "iyishyura", "bwite"
    ]):
        v = lang_facts.get("admission")
        return ("admission", v) if v else (None, None)

    if any(k in q_low for k in [
        "what to see", "what can i see", "exhibits", "collection", "gallery",
        "galleries", "display", "what is inside", "what does", "que voir",
        "exposition", "galerie", "ibiri mu ngoro", "ibiri mu nzu ndangamurage",
        "ibikomeye", "ibigaragazwa", "highlights", "ni iki", "nshobora kubona",
        "ibiriho", "biragaragazwa", "ibigori", "ibirori", "ibiterekwa",
        "ibibarizwa", "mu ngoro", "mu nzu ndangamurage"
    ]):
        v = lang_facts.get("exhibits") or lang_facts.get("highlights")
        return ("exhibits_general", v) if v else (None, None)

    if any(k in q_low for k in [
        "how to get", "directions", "transport", "bus", "taxi", "how do i reach",
        "how can i get", "comment arriver", "comment aller", "se rendre", "acces",
        "moyen de transport", "transport en commun", "gute", "uko nshobora kugera",
        "inzira yo kugera", "kugera aho", "nshobora kugera", "nkagera",
        "nzageuka", "nzagera", "nazagera", "ntoya", "nzajya", "nzajye",
        "kugenda", "ingendo", "imodoka", "moto", "bisi"
    ]):
        v = lang_facts.get("transport")
        return ("transport", v) if v else (None, None)

    if any(k in q_low for k in [
        "opening hours", "closing time", "open", "close", "horaires", "ouvert",
        "ferme", "when do you open", "what time", "igihe", "amasaha", "saa",
        "hafungurwa", "hafungwa", "heure", "heures d ouverture",
        "mfungurwa", "ifungurwa", "ifungwa", "ryari ifungurwa", "igihe cy",
        "amasaha yo", "saa zingahe", "ni ryari", "ryari", "mu saa",
        "bafungura", "bafunga", "bihe", "bitangira", "birangira"
    ]):
        v = lang_facts.get("hours")
        return ("hours", v) if v else (None, None)

    if any(k in q_low for k in [
        "where is", "where is it", "location", "address", "adresse", "situated", "situe",
        "how far", "distance", "aho iherereye", "mu karere",
        "ou se trouve", "ou est le musee", "localisation",
        "iherereye he", "iherereye", "iri he", "iri hehe",
        "aherereye", "uherereye", "icyambu", "akarere", "intara",
        "km uvuye", "birometero", "kilometero", "how do i get to",
        "si trouve", "se trouve"
    ]):
        v = lang_facts.get("location")
        return ("location", v) if v else (None, None)

    if any(k in q_low for k in [
        "history", "histoire", "amateka", "tell me about", "what is this",
        "overview", "about the museum", "describe", "who built", "when was",
        "background", "information", "info", "amakuru", "ubuzima bw",
        "ni iki", "niki", "bwira", "mbwira", "sobanura", "ni gute",
        "yacu", "yashingwa", "yabaye", "yashingwe", "inzu ndangamurage",
        "iyi nzu ndangamurage", "nzu ndangamurage iyi", "iki ni iki",
        "ingoro", "ingabo", "igenda bite", "ikora iki",
        "sobanurira", "mbwire", "ibyo uzi", "ukubwira"
    ]):
        v = lang_facts.get("history")
        return ("history", v) if v else (None, None)

    return (None, None)


def get_core_fact(query, museum_id, language):
    _, text = resolve_core_fact(query, museum_id, language)
    return text


def get_core_fact_route_key(query, museum_id, language):
    """Public hook for evaluation scripts: which curated branch matched, or 'unrouted'."""
    key, text = resolve_core_fact(query, museum_id, language)
    if key:
        return key
    return "unrouted"


def smart_fallback(query, context, language, museum_name):
    """
    Offline fallback used when Gemini is unavailable.
    Extracts the most relevant sentences from context chunks.
    For Kinyarwanda, we attempt a second Gemini call asking specifically for
    a Kinyarwanda translation so visitors don't receive a raw English answer.
    """
    no_info = {
        'en': (f"I'm sorry, I don't have specific details about that for {museum_name}. "
               f"Feel free to ask about our history, opening hours, admission, location, exhibits, or how to get here."),
        'fr': (f"Je suis désolé, je n'ai pas d'informations spécifiques sur ce sujet pour {museum_name}. "
               f"N'hésitez pas à demander l'histoire, les horaires, les droits d'entrée, l'emplacement, les expositions, ou comment s'y rendre."),
        'rw': (f"Mbabarira, nta makuru arambuye mfite kuri icyo kibazo muri {museum_name}. "
               f"Gerageza kubaza amateka, amasaha yo gufungurwa, kwinjira, aho iherereye, ibiri mu nzu ndangamurage, cyangwa uburyo bwo kugera aho.")
    }
    if not context:
        return no_info.get(language, no_info['en'])

    # Build a deduplicated pool of clean sentences from all retrieved chunks
    seen_sents = set()
    all_sentences = []
    for chunk in context:
        cleaned = clean_text(chunk)
        for sent in re.split(r'(?<=[.!?])\s+', cleaned):
            sent = sent.strip()
            # Normalise for dedup check (lowercase, collapse spaces)
            sent_key = re.sub(r'\s+', ' ', sent.lower())
            if len(sent) > 30 and not re.match(r'^[A-Z\s]+:$', sent) and sent_key not in seen_sents:
                seen_sents.add(sent_key)
                all_sentences.append(sent)

    if not all_sentences:
        return no_info.get(language, no_info['en'])

    # Score sentences by keyword overlap with the visitor's query
    stop_words = {'what', 'is', 'the', 'a', 'an', 'how', 'when', 'where', 'who', 'why',
                  'me', 'tell', 'i', 'can', 'do', 'de', 'le', 'la', 'les', 'du', 'en',
                  'un', 'une', 'this', 'that', 'are', 'was', 'were', 'and', 'or', 'of',
                  'ni', 'mu', 'ku', 'na', 'nta', 'ari', 'wa', 'ya', 'za', 'ba', 'bi', 'bu'}
    q_words = set(re.sub(r'[^\w\s]', '', query.lower()).split()) - stop_words

    def score(s):
        s_words = set(re.sub(r'[^\w\s]', '', s.lower()).split())
        return len(q_words & s_words)

    ranked = sorted(all_sentences, key=score, reverse=True)
    top = ranked[:2]
    core_info = ' '.join(top)

    # For Kinyarwanda: try a lightweight Gemini translation call so the visitor
    # does not receive raw English sentences wrapped in a Kinyarwanda frame.
    if language == 'rw':
        translate_prompt = (
            f"Hindura aya magambo mu Kinyarwanda gusa (ntukongere na kimwe, hindura gusa):\n\n{core_info}"
        )
        translated = call_gemini(translate_prompt)
        if translated:
            return f"Nk'uko bigaragazwa n'amakuru dufite muri {museum_name}: {clean_text(translated)}"
        # If translation also failed, return the Kinyarwanda no-info message
        return no_info['rw']

    frames = {
        'en': f"Based on our records at {museum_name}: {core_info}",
        'fr': f"D'après les archives du {museum_name} : {core_info}",
    }
    return frames.get(language, frames['en'])

def generate_response(query, context, language, museum_id, museum_name):
    # ── Greeting detection — a warm reply that is NOT the full welcome message ──
    q_strip = query.lower().strip().rstrip('!.,?')
    GREETINGS = {
        'en': {'hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening',
               'howdy', 'greetings', 'sup', 'good day'},
        'fr': {'bonjour', 'bonsoir', 'salut', 'coucou', 'bonne journée',
               'bonne matinée', 'bonne soirée', 'allô', 'allo'},
        'rw': {'muraho', 'mwaramutse', 'mwiriwe', 'bite', 'amakuru', 'bite se',
               'witwa', 'ndakuramutsa', 'salut', 'hello', 'hi'},
    }
    all_greetings = {g for gs in GREETINGS.values() for g in gs}
    if q_strip in all_greetings or q_strip in GREETINGS.get(language, set()):
        greeting_replies = {
            'en': (f"Hello! Welcome back. I'm your Digital Curator at {museum_name}. "
                   f"How can I help you today? You can ask me about our history, exhibits, "
                   f"opening hours, admission, or how to get here."),
            'fr': (f"Bonjour ! Heureux de vous retrouver au {museum_name}. "
                   f"Je suis votre Conservateur Numérique. Comment puis-je vous aider ? "
                   f"Vous pouvez me poser des questions sur l'histoire, les expositions, "
                   f"les horaires, les tarifs ou comment nous rejoindre."),
            'rw': (f"Muraho! Ndishimye kugutumirira muri {museum_name}. "
                   f"Ndi umurinzi w'amateka wawe. Nakubaza iki uyu munsi? "
                   f"Ushobora kubaza amateka, ibiri mu nzu ndangamurage, amasaha yo gufungurwa, "
                   f"kwinjira, cyangwa uburyo bwo kugera aho."),
        }
        return greeting_replies.get(language, greeting_replies['en'])

    # ── Yes / No / Affirmation / Negation handling ───────────────────────────
    YES_WORDS = {
        'en': {'yes', 'yeah', 'yep', 'yup', 'sure', 'ok', 'okay', 'alright',
               'of course', 'absolutely', 'please', 'go ahead', 'certainly'},
        'fr': {'oui', 'ouais', 'bien sûr', 'bien sur', 'certainement',
               'absolument', 'ok', 'okay', 'd accord', 'volontiers', 's il vous plaît'},
        'rw': {'yego', 'yego cyane', 'ni cyo', 'nibyo', 'mbese yego',
               'ok', 'okay', 'banza', 'ngaho'},
    }
    NO_WORDS = {
        'en': {'no', 'nope', 'nah', 'not really', 'never mind', 'nevermind',
               'no thanks', 'no thank you', 'stop', 'cancel', 'that is all',
               "that's all", 'nothing else', 'done'},
        'fr': {'non', 'nan', 'pas vraiment', 'laisse tomber', 'laissez tomber',
               'non merci', 'rien d autre', 'rien dautre', 'c est tout',
               'cest tout', 'arrêtez', 'arreter', 'annuler'},
        'rw': {'oya', 'oya ndabashimiye', 'oya murakoze', 'nta kintu', 'birahagije',
               'ndashimiye', 'urakoze', 'murakoze', 'nta kindi', 'birakwiye'},
    }
    all_yes = {w for ws in YES_WORDS.values() for w in ws}
    all_no  = {w for ws in NO_WORDS.values() for w in ws}

    if q_strip in all_yes or q_strip in YES_WORDS.get(language, set()):
        if context:
            return apply_persona(context[0], language)
        yes_prompts = {
            'en': (f"Of course! Here are some things you can explore at {museum_name}: "
                   f"the history and founding story, current exhibits, opening hours, "
                   f"admission fees, and directions. What would you like to know more about?"),
            'fr': (f"Bien sûr ! Voici ce que vous pouvez découvrir au {museum_name} : "
                   f"l'histoire et l'origine, les expositions, les horaires, "
                   f"les tarifs et comment y accéder. Que souhaitez-vous savoir ?"),
            'rw': (f"Yego, ndishimye kukufasha! Hari ibintu byinshi ushobora kumenya "
                   f"kuri {museum_name}: amateka yayo, ibiri mu nzu ndangamurage, amasaha yo gufungurwa, "
                   f"kwinjira no kugera aho. Ni iki ushaka kumenya?"),
        }
        return yes_prompts.get(language, yes_prompts['en'])

    if q_strip in all_no or q_strip in NO_WORDS.get(language, set()):
        no_replies = {
            'en': (f"No problem at all! Feel free to come back anytime you have a question "
                   f"about {museum_name}. Enjoy your visit!"),
            'fr': (f"Pas de problème ! N'hésitez pas à revenir quand vous aurez d'autres "
                   f"questions sur {museum_name}. Bonne visite !"),
            'rw': (f"Nta kibazo! Ushobora kugaruka igihe cyose ufite ikibazo "
                   f"kijyanye na {museum_name}. Ugende neza kandi unezerwe!"),
        }
        return no_replies.get(language, no_replies['en'])

    # ── "More" / "tell me more" filler — continue from context ──────────────
    MORE_WORDS = {
        'en': {'more', 'tell me more', 'continue', 'go on', 'elaborate',
               'and then', 'what else', 'keep going'},
        'fr': {'plus', 'encore', 'continuez', 'dites m en plus', 'dites moi plus',
               'et ensuite', 'quoi d autre', 'continuez s il vous plaît'},
        'rw': {'iyindi', 'mbwire ibindi', 'komeza', 'ukomeze', 'ibindi',
               'n ibindi', 'sobanura', 'nsobanurire'},
    }
    all_more = {w for ws in MORE_WORDS.values() for w in ws}
    if q_strip in all_more or q_strip in MORE_WORDS.get(language, set()):
        if context:
            return apply_persona(context[0], language)

    # Core Facts (Aggressive Priority)
    core_text = get_core_fact(query, museum_id, language)
    if core_text: return apply_persona(core_text, language)

    # Build a language-specific prompt — INSTRUCTIONS are written in the target language
    # so the model cannot default to English when the language is French or Kinyarwanda.
    context_text = "\n\n".join(clean_text(c) for c in context) if context else ""

    if language == 'rw':
        prompt = (
            f"Uri Umurinzi w'amateka muri {museum_name}. "
            f"SUBIZA MU KINYARWANDA GUSA — ntukoreshe na kimwe cy'Icyongereza cyangwa Igifaransa mu gisubizo cyawe.\n\n"
            f"AMAKURU Y'INZU NDANGAMURAGE:\n{context_text if context_text else '(Nta makuru arambuye ahari)'}\n\n"
            f"IKIBAZO CY'UMUSURA: {query}\n\n"
            f"AMABWIRIZA: Subiza mu magambo 2-4 gusa, wishingiye ku makuru yo hejuru. "
            f"Ntukoreshe markdown, akabariro, inyandiko z'ingaruka, cyangwa ibyiciro. "
            f"Niba amakuru adahari, bwira umusura neza no kumugisha ibibazo bijyanye n'inzu ndangamurage. "
            f"SUBIZA MU KINYARWANDA GUSA."
        )
    elif language == 'fr':
        prompt = (
            f"Vous êtes le Conservateur Numérique du {museum_name}. "
            f"RÉPONDEZ UNIQUEMENT EN FRANÇAIS — n'utilisez pas d'anglais ni de kinyarwanda dans votre réponse.\n\n"
            f"BASE DE CONNAISSANCES DU MUSÉE :\n{context_text if context_text else '(Aucun contexte disponible)'}\n\n"
            f"QUESTION DU VISITEUR : {query}\n\n"
            f"INSTRUCTIONS : Répondez en 2 à 4 phrases claires en utilisant uniquement les informations ci-dessus. "
            f"N'utilisez pas de markdown, de puces, d'astérisques ou de titres. "
            f"Si l'information n'est pas disponible, dites-le poliment et suggérez des sujets connexes. "
            f"RÉPONDEZ UNIQUEMENT EN FRANÇAIS."
        )
    else:  # English (default)
        prompt = (
            f"You are the Digital Curator for {museum_name}. Speak warmly and professionally. "
            f"RESPOND ONLY IN ENGLISH.\n\n"
            f"MUSEUM KNOWLEDGE BASE:\n{context_text if context_text else '(No archive context available)'}\n\n"
            f"VISITOR QUESTION: {query}\n\n"
            f"INSTRUCTIONS: Answer in 2-4 clear sentences using only the knowledge base above. "
            f"Do NOT use markdown, bullet points, asterisks, or headers. "
            f"If information is not available, politely say so and suggest related topics. "
            f"RESPOND ONLY IN ENGLISH."
        )

    ai_response = call_gemini(prompt)
    if ai_response:
        return clean_text(ai_response)

    # ── Intelligent fallback: extract clean sentences from context ──
    return smart_fallback(query, context, language, museum_name)

def detect_language(text):
    """
    Lightweight language detector based on unique character/word fingerprints.
    Returns 'rw', 'fr', or 'en'.  Used as a safety-net when the client sends
    the wrong language tag (e.g. language='en' but the visitor typed in Kinyarwanda).
    """
    t = text.lower()
    # Strong Kinyarwanda markers: common words / prefixes that never appear in EN/FR
    rw_markers = ['ndashaka', 'ni iki', 'ni nde', 'ni he', 'ni ryari', 'ni gute',
                  'urakoze', 'mwaramutse', 'mwiriwe', 'bite', 'amakuru', 'bite se',
                  'yego', 'oya', 'ibikomeye', 'ngaho', 'ubwoko', 'amasaha',
                  'kwinjira', 'amateka', 'igihe', 'aho iherereye', 'nshaka',
                  'umurinzi', 'ingoro', 'inzu', 'muraho', 'murakoze',
                  'ndabashimiye', 'ni angahe', 'birishwa', 'hafungurwa',
                  'hafungwa', 'ibiri mu ngoro', 'nshobora kugera']
    fr_markers = ['est-ce', "qu'est", 'comment', 'horaires', "qu'il", 'quoi',
                  "c'est", 'bonjour', 'bonsoir', 'salut', 'merci', 'pouvez',
                  'voulez', "j'aimerais", 'musée', 'exposition', 'entrée',
                  'tarif', 'billet', 'ouvert', 'fermé', 'ferme', 'gratuit']
    rw_score = sum(1 for m in rw_markers if m in t)
    fr_score  = sum(1 for m in fr_markers if m in t)
    if rw_score >= 1:
        return 'rw'
    if fr_score >= 1:
        return 'fr'
    return None  # Cannot determine — keep client-supplied language


# Distance threshold for relevance guard.
# ChromaDB's default ONNX embedding returns cosine distances (0 = identical, 2 = opposite).
# Values > 1.45 reliably indicate the query is unrelated to any museum content.
RELEVANCE_THRESHOLD = 1.45

# Topics the chatbot should firmly refuse regardless of context match
OUT_OF_SCOPE_PATTERNS = [
    r'\b(weather|forecast|temperature|rain|climate)\b',
    r'\b(recipe|cook|food|restaurant|hotel|flight|booking)\b',
    r'\b(politics|election|president|government|parliament)\b',
    r'\b(sport|football|basketball|soccer|olympic)\b',
    r'\b(write.*email|send.*email|draft.*letter|homework|essay)\b',
    r'\b(stock|invest|crypto|bitcoin|finance|money transfer)\b',
    r'\b(translate|traduction)\b',
]

def is_out_of_scope(query, best_distance, museum_id=None):
    """Return True if the query is clearly not about the museum."""
    q = query.lower()
    for pat in OUT_OF_SCOPE_PATTERNS:
        if re.search(pat, q):
            return True
    # Museum Ingabo: named exhibitions (KAMWE, Inzira, etc.) must not be blocked by weak embedding distance
    if museum_id == "3" and re.search(
        r'\b(kamwe|inzira|inzitane|rebero|cultural village|king ngabo|museum ingabo|musée ingabo|'
        r'ingabo|same wounds|different\s*,?\s*same|path of resilience|hundred days|100\s*days|'
        r'iminsi\s*100|cent jours|exhibit|exhibition|installation)\b',
        q, re.I
    ):
        return False
    # If ChromaDB found nothing even close, treat as out-of-scope
    if best_distance is not None and best_distance > RELEVANCE_THRESHOLD:
        return True
    return False


@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    msg = data.get('query') or data.get('message', '')
    lang = data.get('language', 'en')
    mid = str(data.get('museumId')) if data.get('museumId') and str(data.get('museumId')).lower() != 'none' else '1'

    # Safety-net: if the visitor's text looks like a different language, correct it
    detected = detect_language(msg)
    if detected and detected != lang:
        print(f"[{INSTANCE_ID}] Language override: client sent '{lang}', detected '{detected}'")
        lang = detected

    m_info = MUSEUM_NAMES.get(mid, MUSEUM_NAMES["1"])
    m_name = m_info.get(lang, m_info['en'])

    if msg == 'special:welcome':
        res = {
            'en': f"Welcome to {m_name}. I am your Digital Curator. How may I assist your exploration today?",
            'fr': f"Bienvenue au {m_name}. Je suis votre Conservateur Numérique. Comment puis-je vous aider ?",
            'rw': f"Murakaza neza muri {m_name}. Ndi umurinzi w'amateka aha. Nabafasha iki uyu munsi?"
        }
        return jsonify({'response': res.get(lang, res['en'])})

    # Retrieval via ChromaDB — include distances for relevance gating
    context = []
    best_distance = None
    try:
        coll = get_db()
        total = coll.count()
        safe_n = max(1, min(8, total)) if total > 0 else 0
        # Richer query text helps embeddings match short visitor questions (e.g. "kamwe")
        qtext = msg
        if mid == "3" and re.search(r'kamwe|kamo|hundred|100|cent jour|iminsi|exhibit|exhibition|death|genocide|memory', msg, re.I):
            qtext = f"{msg} KAMWE exhibition Museum Ingabo Rebero art installation memory genocide remembrance"
        if safe_n > 0:
            results = coll.query(
                query_texts=[qtext], n_results=safe_n,
                where={"museum_id": mid},
                include=["documents", "distances"]
            )
            context = results['documents'][0] if results['documents'] else []
            distances = results['distances'][0] if results.get('distances') else []
            if distances:
                best_distance = min(distances)
            # If the museum-specific filter returned nothing, broaden to all museums
            if not context:
                results = coll.query(
                    query_texts=[qtext], n_results=safe_n,
                    include=["documents", "distances"]
                )
                context = results['documents'][0] if results['documents'] else []
                distances = results['distances'][0] if results.get('distances') else []
                if distances:
                    best_distance = min(distances)
    except Exception as retrieval_err:
        print(f"[{INSTANCE_ID}] Retrieval error: {retrieval_err}")
        context = []

    # ── Out-of-scope guard ───────────────────────────────────────────────────
    if is_out_of_scope(msg, best_distance, mid):
        oos = {
            'en': (f"I'm your Digital Curator at {m_name} and I can only assist with museum-related "
                   f"topics such as our history, exhibits, opening hours, admission, and directions. "
                   f"How can I help you explore the museum today?"),
            'fr': (f"Je suis le Conservateur Numérique du {m_name} et je peux uniquement répondre "
                   f"aux questions liées au musée : histoire, expositions, horaires, tarifs et accès. "
                   f"Comment puis-je vous aider à explorer le musée ?"),
            'rw': (f"Ndi umurinzi w'amateka wa {m_name} kandi nshobora gusa gufasha mu bibazo "
                   f"bijyanye n'inzu ndangamurage nk'amateka yayo, ibiri muri yo, amasaha yo gufungurwa, "
                   f"kwinjira no kugera aho. Nagufasha iki uyu munsi?")
        }
        return jsonify({'response': oos.get(lang, oos['en']), 'instance': INSTANCE_ID, 'version': '4.3'})

    response = generate_response(msg, context, lang, mid, m_name)
    return jsonify({'response': response, 'instance': INSTANCE_ID, 'version': '4.3'})

@app.route('/api/status', methods=['GET'])
def status():
    count = collection.count() if collection else 0
    return jsonify({'status': 'online', 'version': '4.2', 'instance': INSTANCE_ID, 'indexed': count, 'museums': len(MUSEUM_NAMES)})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    print("\n" + "*"*60)
    print(f"  Rwanda Museum Chatbot v4.2 — {INSTANCE_ID}")
    print(f"  PORT: {port}  |  8 museums  |  CORS enabled")
    print(f"  NOTE: ChromaDB + Gemini load on first request (~15s)")
    print("*"*60 + "\n")
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)