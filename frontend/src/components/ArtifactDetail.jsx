import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import translations from '../translations';

const BROWN_DARK = '#5C3D1E';
const BROWN_GOLD = '#8B6914';
const CREAM_BG = '#F5F0EA';
const HEADER_BG = '#5C3D1E';

const LANG_LABELS = { en: 'English', fr: 'Français', rw: 'Kinyarwanda' };

// ---- Artefact Data (add image paths here when images are ready) ----
const ARTEFACTS = [
    {
        id: 1,
        title: { en: 'Royal Drum (Karinga)', fr: 'Tambour Royal (Karinga)', rw: 'Ingoma ya Karinga' },
        museum: { en: 'Ethnographic Museum – Huye', fr: 'Musée Ethnographique – Huye', rw: 'Inyubako y\'Umurage – Huye' },
        image: '/artefacts/ingoma.jpg',
        description: {
            en: `The Karinga is the supreme sacred royal drum of Rwanda, symbolizing the heart of the nation and its sovereignty. It was rarely beaten and served as the absolute emblem of royal authority. Inaugurated by King Ruganzu II Ndori in the 16th century, it was guarded by a secret council of ritualists known as the Abiru, who were the sole custodians of its sacred laws.`,
            fr: `Le Karinga est le tambour royal sacré suprême du Rwanda, symbolisant le cœur de la nation et sa souveraineté. Il n'était que rarement battu et servait d'emblème absolu de l'autorité royale.`,
            rw: `Karinga ni ingoma ntagatifu y'icyubahiro mu Rwanda, ihagarariye umutima w'igihugu n'ubusugire bwacyo. Ntabwo yakunze kuvuzwa kenshi, yari ikimenyetso ntakuka cy'ububasha bw'Umwami.`,
        },
        source: 'Ethnographic Museum Archives',
    },
    {
        id: 2,
        title: { en: 'Intebe y\'Umwami (Royal Throne)', fr: 'Trône Royal', rw: 'Intebe y\'Umwami' },
        museum: { en: "King's Palace Museum – Nyanza", fr: "Musée du Palais Royal – Nyanza", rw: "Inyubako ya Nyiri Ubutaka – Nyanza" },
        image: '/artefacts/intebe.jpg',
        description: {
            en: `The Intebe y'Umwami is the hand-carved wooden throne representing the MWAMI's absolute judicial and moral authority. From this seat, the King governed the land in deep consultation with the Biru protectors, ensuring justice was administered according to sacred codes. It bridges the transition between ancient royal architecture and modern statehood.`,
            fr: `L'Intebe y'Umwami est le trône en bois sculpté à la main représentant l'autorité judiciaire et morale absolue du MWAMI. Depuis ce siège, le Roi gouvernait le pays.`,
            rw: `Intebe y'Umwami ni intebe yakozwe mu giti n'intoke, ihagarariye ububasha ntakuka bw'Umwami mu bijyanye n'ubucamanza n'ubuyobozi bw'igihugu.`,
        },
        source: "King's Palace Museum Arhcives",
    },
    {
        id: 3,
        title: { en: "INZIRA Y'INZITANE Exhibition", fr: "Exposition INZIRA Y'INZITANE", rw: "Imurikagurisha INZIRA Y'INZITANE" },
        museum: { en: 'Museum Ingabo – Kigali', fr: 'Musée Ingabo – Kigali', rw: 'Inyubako y\'Umurage Ingabo – Kigali' },
        image: '/artefacts/ingabo.jpg',
        description: {
            en: `The "INZIRA Y'INZITANE" (The Labyrinthine Path) is a world-class exhibition founded by artist King NGABO. It uses 30 symbolic metal installations to narrate Rwanda's path from the tragedy of 1994 to its 2024 industrial and cultural renaissance. It celebrates the "labyrinth" of healing and the resilience of the Rwandan people.`,
            fr: `L'exposition "INZIRA Y'INZITANE" au Musée Ingabo raconte la tapisserie complexe et magnifique de l'histoire rwandaise à travers 30 installations symboliques.`,
            rw: `Imurikagurisha rya "INZIRA Y'INZITANE" rwashinzwe n'umuhanzi King NGABO, rikoresha ibihangano 30 by'icyuma mu kuvuga urugendo rw'u Rwanda rwo kuva mu mwijima rwerekeza mu mucyo n'uburumbuke.`,
        },
        source: 'Museum Ingabo Archives',
    },
    {
        id: 4,
        title: { en: "Inyambo (Royal Cattle)", fr: "Bovins Inyambo", rw: "Inyambo" },
        museum: { en: "King's Palace Museum – Nyanza", fr: "Musée du Palais Royal – Nyanza", rw: "Inyubako ya Nyiri Ubutaka – Nyanza" },
        image: '/artefacts/inyambo.jpg',
        description: {
            en: `The Inyambo are Rwanda's legendary royal cattle, known as "royal poets" for their graceful parade movements. Characterized by their majestic stature and extraordinarily long, lyre-shaped horns, they were bred specifically for royal ceremonies and remain a living symbol of the elegance of the ancient kingdom.`,
            fr: `Les Inyambo sont les légendaires bovins royaux du Rwanda, connus sous le nom de « poètes royaux » pour leurs mouvements de parade gracieux.`,
            rw: `Inyambo ni inka z'amateka n'icyubahiro mu Rwanda, zizwi nk'abasizi b'umwami kubera uburyo zegera n'amagambo igihe ziri mu birori.`,
        },
        source: 'RCHA Cultural Archives',
    },
    {
        id: 5,
        title: { en: "12.7mm Machine Gun", fr: "Mitrailleuse 12.7mm", rw: "Imashini y'Abasirikare 12.7mm" },
        museum: { en: "Campaign Against Genocide Museum", fr: "Musée de la Campagne contre le Génocide", rw: "Inyubako y'Umurage yo guhagarika Jenoside" },
        image: '/artefacts/gun.jpg',
        description: {
            en: `The 12.7mm Machine Gun is a pivotal artifact of the Campaign Against Genocide. Mounted on the roof of the Parliament building (then CND) during the 1994 siege, it was used by the RPA's 3rd Battalion to repel attacks, protecting thousands of civilians and securing the mission to rescue the nation.`,
            fr: `La mitrailleuse de 12,7 mm est un artefact essentiel de la campagne contre le génocide. Installée sur le toit du Parlement, elle a servi à repousser les attaques.`,
            rw: `Imashini y'abasirikare ya 12.7mm ni ikimenyetso gikomeye cy'amateka yo guhagarika Jenoside yakorewe Abatutsi. Yakoreshejwe ku gasongero k'inyubako y'inteko ishinga amategeko.`,
        },
        source: 'CAG Museum Archives',
    },
    {
        id: 6,
        title: { en: "Imigongo Art", fr: "Art Imigongo", rw: "Gukora Imigongo" },
        museum: { en: "Rwanda Art Museum – Kanombe", fr: "Musée d'Art du Rwanda – Kanombe", rw: "Inyubako y'Ubuhanzi – Kanombe" },
        image: '/artefacts/imigongo.jpg',
        description: {
            en: `Imigongo is a unique Rwandan art form dating back to the 18th century, originated by Prince Kakira of the Gisaka kingdom. It is made using cow dung mixed with natural pigments like volcanic ash and clay to create geometric, relief patterns. Traditionally used to decorate royal residences and ceremonial items, Imigongo represents Rwandan resilience and creativity, turning organic materials into intricate, high-status artistic expressions.`,
            fr: `L'Imigongo est une forme d'art rwandaise unique datant du XVIIIe siècle, créée par le prince Kakira du royaume de Gisaka. Il est fabriqué à partir de bouse de vache mélangée à des pigments naturels pour créer des motifs géométriques en relief.`,
            rw: `Imigongo ni uburyo bw'ubuhanzi bw'umwimerere bw'u Rwanda bukomoka mu kinyejana cya 18, buhangwa n'Igikomangoma Kakira mu bwami bwa Gisaka. Bikozwe mu mase y'inka n'ibindi bimenyetso by'umwimerere nk'amashyiga n'ibumba.`,
        },
        source: 'RCHA Art Archives',
    },
];

const ArtifactDetail = ({ language, setLanguage, onBack, initialArtifactId }) => {
    const t = translations[language] || translations.en;
    const [artefactIndex, setArtefactIndex] = useState(0);
    const [showChat, setShowChat] = useState(false);
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [imgError, setImgError] = useState({});
    const messagesEndRef = useRef(null);

    // Set initial artifact from URL param
    useEffect(() => {
        if (initialArtifactId) {
            const index = ARTEFACTS.findIndex(a => a.id === initialArtifactId);
            if (index !== -1) {
                setArtefactIndex(index);
                // When coming from a QR code, we want the chat open immediately
                setShowChat(true);
            }
        }
    }, [initialArtifactId]);

    const artefact = ARTEFACTS[artefactIndex];

    const nextLanguage = () => {
        const langs = Object.keys(LANG_LABELS);
        const idx = langs.indexOf(language);
        const next = langs[(idx + 1) % langs.length];
        setLanguage(next);
    };

    useEffect(() => {
        // Reset messages when museum changes so the visitor gets a fresh greeting
        setMessages([{
            role: 'bot',
            text: t.welcomeMsg(artefact.museum[language] || artefact.museum.en),
            time: new Date()
        }]);
    }, [language, artefactIndex, t, artefact.museum]);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages, showChat]);

    const sendMessage = async (e) => {
        e.preventDefault();
        if (!input.trim() || loading) return;
        const userText = input.trim();
        setInput('');
        setMessages(p => [...p, { role: 'user', text: userText, time: new Date() }]);
        setLoading(true);
        try {
            const apiUrl = import.meta.env.VITE_API_URL || '';
            const res = await axios.post(`${apiUrl}/api/chat`, { query: userText, language });

            // Clean up Markdown-like bullet points and bolding for raw text display
            let botResponse = res.data.response;
            botResponse = botResponse.replace(/\*\*/g, ''); // Remove bold markers

            setMessages(p => [...p, { role: 'bot', text: botResponse, time: new Date() }]);

            // INTELLIGENT IMAGE SWITCHING:
            // Check if the response mentions another artifact in our list
            const lowerRes = botResponse.toLowerCase();
            ARTEFACTS.forEach((item, index) => {
                const titleEN = (item.title.en || '').toLowerCase();
                const titleRW = (item.title.rw || '').toLowerCase();

                // If the bot mentions a specific known artifact, switch the main image!
                if (lowerRes.includes(titleEN) || lowerRes.includes(titleRW) || lowerRes.includes(item.id.toString())) {
                    if (index !== artefactIndex) {
                        setArtefactIndex(index);
                    }
                }
            });

        } catch (error) {
            const errorMsg = error.response
                ? `Error ${error.response.status}: ${JSON.stringify(error.response.data)}`
                : `Network Error: ${error.message}. Target: ${import.meta.env.VITE_API_URL || 'current domain'}`;

            setMessages(p => [...p, {
                role: 'bot',
                text: `${t.connectionError}\n\n[Diagnostic Info]: ${errorMsg}\n\nTip: Ensure VITE_API_URL is set in Render Environment and you have Redeployed.`,
                time: new Date()
            }]);
        } finally {
            setLoading(false);
        }
    };

    const fmt = (d) => d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const title = artefact.title[language] || artefact.title.en;
    const museum = artefact.museum[language] || artefact.museum.en;
    const desc = artefact.description[language] || artefact.description.en;

    const Header = () => (
        <header className="bg-museum-brown-dark px-4 py-3 flex items-center justify-between text-white z-20 shadow-md">
            <div className="flex items-center gap-3">
                <button onClick={onBack} className="flex items-center gap-1 text-sm font-medium hover:opacity-80 transition-opacity">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><polyline points="15 18 9 12 15 6"></polyline></svg>
                    {t.back}
                </button>
                <button
                    onClick={() => { setLanguage(null); onBack(); }}
                    className="flex items-center gap-1 text-sm font-medium hover:opacity-80 transition-opacity"
                >
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path><polyline points="9 22 9 12 15 12 15 22"></polyline></svg>
                    {t.home}
                </button>
            </div>
            <h2 className="text-[11px] font-bold uppercase tracking-wider opacity-90 truncate max-w-[120px]">{museum}</h2>
            <button
                onClick={nextLanguage}
                className="bg-white/15 px-3 py-1 rounded-full text-[11px] font-semibold border border-white/10 backdrop-blur-sm hover:bg-white/30 transition-all active:scale-95 flex items-center gap-1"
            >
                <span className="opacity-70 text-[9px] mr-1">🌐</span>
                {LANG_LABELS[language]}
            </button>
        </header>
    );

    return (
        <div className="phone-frame">
            <div className="phone-notch"></div>
            <div className="phone-screen flex flex-col">
                <Header />

                <main className="flex-1 overflow-y-auto no-scrollbar bg-museum-cream-light relative">
                    {/* Content Section */}
                    <article className="pb-24">
                        {/* Hero Image */}
                        <div className="h-64 relative overflow-hidden group">
                            {!imgError[artefact.id] && artefact.image ? (
                                <img
                                    src={artefact.image}
                                    alt={title}
                                    onError={() => setImgError(p => ({ ...p, [artefact.id]: true }))}
                                    className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105"
                                />
                            ) : (
                                <div className="w-full h-full bg-gradient-to-br from-museum-brown-dark to-museum-brown-medium flex items-center justify-center text-6xl">
                                    🥁
                                </div>
                            )}
                            <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent flex flex-col justify-end p-6">
                                <h1 className="text-white text-2xl font-bold leading-tight drop-shadow-lg">{title}</h1>
                            </div>
                        </div>

                        {/* Description Card */}
                        <div className="p-6">
                            <div className="premium-card !p-6">
                                <p className="text-museum-text-main text-[14px] leading-[1.8] text-justify mb-6 font-medium opacity-90">
                                    {desc}
                                </p>
                                <div className="pt-5 border-t border-museum-cream-dark flex flex-col gap-1">
                                    <p className="text-museum-brown-medium text-xs font-semibold italic">
                                        {t.source}: <span className="text-museum-brown-dark not-italic">{artefact.source}</span>
                                    </p>
                                    <p className="text-museum-brown-light text-[10px] font-medium opacity-60">
                                        Sample artefact image (RCHA archive)
                                    </p>
                                </div>
                            </div>

                            {/* Navigation Controls */}
                            <div className="flex gap-4 mt-8 px-2">
                                <button
                                    onClick={() => { setArtefactIndex(Math.max(0, artefactIndex - 1)); setShowChat(false); }}
                                    disabled={artefactIndex === 0}
                                    className={`flex-1 py-3.5 rounded-2xl font-semibold text-sm transition-all duration-300 border-2 ${artefactIndex === 0
                                        ? 'bg-transparent border-museum-cream-dark text-museum-brown-light/40 cursor-not-allowed'
                                        : 'bg-white border-museum-brown-medium text-museum-brown-medium hover:bg-museum-brown-medium/5'
                                        }`}
                                >
                                    {t.back}
                                </button>
                                <button
                                    onClick={() => { setArtefactIndex(Math.min(ARTEFACTS.length - 1, artefactIndex + 1)); setShowChat(false); }}
                                    disabled={artefactIndex === ARTEFACTS.length - 1}
                                    className={`flex-1 py-3.5 rounded-2xl font-semibold text-sm transition-all duration-300 shadow-md flex items-center justify-center gap-2 ${artefactIndex === ARTEFACTS.length - 1
                                        ? 'bg-museum-brown-light/50 text-white/50 cursor-not-allowed'
                                        : 'bg-museum-brown-medium text-white hover:bg-museum-brown-dark'
                                        }`}
                                >
                                    {t.next}
                                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"><polyline points="9 18 15 12 9 6"></polyline></svg>
                                </button>
                            </div>

                            {/* Dots Indicator */}
                            <div className="flex justify-center gap-2 mt-8">
                                {ARTEFACTS.map((_, i) => (
                                    <button
                                        key={i}
                                        onClick={() => { setArtefactIndex(i); setShowChat(false); }}
                                        className={`w-2 h-2 rounded-full transition-all duration-300 ${i === artefactIndex ? 'bg-museum-brown-medium w-4' : 'bg-museum-brown-light/30'}`}
                                    />
                                ))}
                            </div>
                        </div>
                    </article>

                    {/* Integrated Chat Button (Dynamic) */}
                    {!showChat && (
                        <div className="absolute bottom-6 left-0 right-0 flex justify-center z-30 px-6">
                            <button
                                onClick={() => setShowChat(true)}
                                className="bg-museum-brown-dark text-white rounded-full py-3.5 px-8 shadow-2xl flex items-center gap-3 font-semibold text-sm hover:scale-105 active:scale-95 transition-all duration-300 border border-white/10"
                            >
                                <span>{t.askQuestions}</span>
                                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>
                            </button>
                        </div>
                    )}

                    {/* Overlay for chat when open */}
                    <div className={`absolute inset-0 bg-black/20 backdrop-blur-[2px] z-40 transition-opacity duration-500 ${showChat ? 'opacity-100' : 'opacity-0 pointer-events-none'}`} onClick={() => setShowChat(false)} />

                    {/* Chat Drawer */}
                    <div className={`absolute bottom-0 left-0 right-0 bg-white rounded-t-[2.5rem] shadow-[0_-20px_50px_rgba(0,0,0,0.15)] z-50 flex flex-col transition-transform duration-500 ease-out h-[85%] border-t border-museum-cream-dark ${showChat ? 'translate-y-0' : 'translate-y-full'}`}>
                        <div className="p-6 pb-2 flex flex-col items-center">
                            <div className="w-12 h-1.5 bg-museum-cream-dark rounded-full mb-5 cursor-pointer hover:bg-museum-brown-light/30 transition-colors" onClick={() => setShowChat(false)} />
                            <h3 className="text-museum-brown-dark font-bold text-lg mb-1">{t.askAboutArtefact}</h3>
                            {messages.length <= 1 && (
                                <p className="text-museum-brown-medium text-xs font-medium opacity-60 italic text-center px-4">{t.chatPrompt}</p>
                            )}
                        </div>

                        {/* Messages Area */}
                        <div className="flex-1 overflow-y-auto px-6 py-4 flex flex-col gap-4 no-scrollbar">
                            {messages.map((msg, i) => (
                                <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                                    <div className={`p-4 rounded-3xl text-[14px] leading-[1.6] shadow-sm max-w-[90%] whitespace-pre-wrap ${msg.role === 'user'
                                        ? 'bg-museum-brown-medium text-white rounded-tr-none font-medium'
                                        : 'bg-museum-cream-light text-museum-brown-dark rounded-tl-none border border-museum-cream-dark'
                                        }`}>
                                        <p>{msg.text}</p>
                                        <p className={`text-[10px] mt-2 font-bold uppercase tracking-widest opacity-50 ${msg.role === 'user' ? 'text-white' : 'text-museum-brown-medium'}`}>
                                            {fmt(msg.time)}
                                        </p>
                                    </div>
                                </div>
                            ))}
                            {loading && (
                                <div className="flex justify-center p-2">
                                    <div className="flex gap-1.5 items-center bg-museum-cream-light px-4 py-2 rounded-full border border-museum-cream-dark">
                                        <div className="w-1.5 h-1.5 bg-museum-brown-medium rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                                        <div className="w-1.5 h-1.5 bg-museum-brown-medium rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                                        <div className="w-1.5 h-1.5 bg-museum-brown-medium rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                                    </div>
                                </div>
                            )}
                            <div ref={messagesEndRef} />
                        </div>

                        {/* Chat Input */}
                        <form onSubmit={sendMessage} className="p-6 pt-2 pb-8 border-t border-museum-cream-dark flex gap-3 items-center">
                            <div className="flex-1 relative">
                                <input
                                    value={input}
                                    onChange={e => setInput(e.target.value)}
                                    placeholder={t.chatPlaceholder}
                                    className="w-full bg-museum-cream-light border-2 border-transparent focus:border-museum-brown-medium/20 focus:bg-white rounded-2xl py-3.5 px-5 text-sm text-museum-brown-dark placeholder:text-museum-brown-light/50 outline-none transition-all duration-300 font-medium"
                                />
                            </div>
                            <button
                                type="submit"
                                disabled={loading || !input.trim()}
                                className={`w-12 h-12 rounded-2xl flex items-center justify-center transition-all duration-300 shadow-md ${loading || !input.trim()
                                    ? 'bg-museum-cream-dark text-museum-brown-light/30 cursor-not-allowed shadow-none'
                                    : 'bg-museum-brown-dark text-white hover:bg-museum-brown-medium hover:scale-105 active:scale-95'
                                    }`}
                            >
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
                            </button>
                        </form>
                    </div>
                </main>
            </div>
            {/* Home bar filler */}
            <div className="w-16 h-1.5 bg-white/20 rounded-full mx-auto my-3"></div>
        </div>
    );
};

export default ArtifactDetail;
