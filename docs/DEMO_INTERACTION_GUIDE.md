# 📜 My Capstone Demo: Interaction & Testing Log
**Developer**: Amandine Irakoze

In my final demonstration, I use these specific questions to verify the depth and accuracy of my RAG-powered chatbot. These tests confirm that the system correctly retrieves information from the five main museum archives.

---

## 1. Museum Ingabo (Kigali Testing)
I verified the system's ability to handle contemporary cultural art questions:
- **English**: "What is the meaning behind the 'Inzira y'Inzitane' exhibition?"
- **Kinyarwanda**: "Vuga amateka y'imurikagurisha rya Inzira y'Inzitane n'umuhanzi King Ngabo."
- **French**: "Qui est l'artiste derrière le Musée Ingabo et quelle est sa vision?"
- **Advanced**: "How does the 'Blind Drum Walk' work?"

## 2. Ethnographic Museum (Huye Testing)
I tested the system on pre-colonial governance and traditional craftsmanship:
- **English**: "Tell me about the importance of the Karinga drum."
- **Kinyarwanda**: "Karinga yari ifite akahe kamaro mu bwami bw'u Rwanda?"
- **French**: "Qui étaient les Abiru et quel était leur rôle?"
- **Advanced**: "Explain the meaning of the Agaseke (Peace Basket) patterns."

## 3. King's Palace Museum (Nyanza Testing)
I validated the retrieval of royal history and sacred traditions:
- **English**: "Why are the Inyambo cattle called 'royal poets'?"
- **Kinyarwanda**: "Inka z'Inyambo zatozwaga gute mu birori by'ibwami?"
- **French**: "Quelle est l'importance du trône 'Intebe y’Umwami'?"
- **Advanced**: "What was the 'Urugo' of King Mutara III Rudahigwa like?"

## 4. Campaign Against Genocide Museum (CAG Testing)
I ensured accuracy for historical liberation facts:
- **English**: "What was the role of the 12.7mm Machine Gun in stopping the Genocide?"
- **Kinyarwanda**: "Imashini ya 12.7mm yakoreshejwe gute ku nyubako ya CND?"
- **French**: "Racontez-moi l'histoire du 3ème bataillon pendant le siège du Parlement."

## 5. National History Museum & Art Museum
I confirmed identity and origin details:
- **Richard Kandt**: "Comment Kigali est-elle devenue la capitale à l'époque de Richard Kandt?"
- **Imigongo Art**: "Who originated the Imigongo art form?"

---

## 💡 Technical Proofs Shown in Demo:
1. **Multilingualism**: I show the bot switching languages seamlessly by re-entering the site with different language parameters.
2. **QR Deep Linking**: I demonstrate scanning a QR code (using `?id=3`) which automatically filters the AI's "brain" to the specific museum.
3. **Hallucination Protection**: I ask a non-museum question (e.g., "Who won the World Cup?") to prove that my **Extractive QA logic** restricts the bot's answers to verified museum archives only.
