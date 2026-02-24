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
        title: { en: 'Royal Drum (Ingoma)', fr: 'Tambour Royal (Ingoma)', rw: 'Ingoma y\'Ubwami' },
        museum: { en: 'Ethnographic Museum – Huye', fr: 'Musée Ethnographique – Huye', rw: 'Inyubako y\'Umurage – Huye' },
        image: '/artefacts/ingoma.jpg', // place image here; shows gradient if missing
        description: {
            en: `The Ingoma, or royal drum, holds profound significance in Rwandan culture. These sacred drums were not merely musical instruments but symbols of royal power and spiritual connection. Traditionally crafted from specific trees and animal hide, each drum carries the heartbeat of the kingdom. During important ceremonies, the rhythmic sounds of Ingoma united communities and honored ancestral spirits. The intricate carvings and decorations tell stories of lineage, power, and the eternal bond between the people and their land.`,
            fr: `L'Ingoma, ou tambour royal, revêt une signification profonde dans la culture rwandaise. Ces tambours sacrés n'étaient pas de simples instruments de musique, mais des symboles du pouvoir royal et de la connexion spirituelle. Traditionnellement fabriqué à partir d'arbres spécifiques et de peaux d'animaux, chaque tambour porte le cœur du royaume. Lors des cérémonies importantes, les sons rythmiques de l'Ingoma unissaient les communautés et honoraient les esprits ancestraux.`,
            rw: `Ingoma y'ubwami ifite akamaro gakomeye mu muco w'u Rwanda. Ingoma zera ntizari gusa ibikoresho byo kuririmba, ahubwo zari ibimenyetso by'ububasha bw'ubwami no gutumanahana n'inzuka. Zakozwe ku giti cy'umwimerere no mu ruhu rw'inyamaswa, buri ngoma yarebeye umutima w'ubwami. Mu bikorwa by'ingenzi, amajwi y'ingoma yashyiraga hamwe amatsinda kandi agashimira inzuka z'abakurambere.`,
        },
        source: 'Rwanda Cultural Heritage Academy',
    },
    {
        id: 2,
        title: { en: 'Royal Throne (Intebe)', fr: 'Trône Royal (Intebe)', rw: 'Intebe y\'Umwami' },
        museum: { en: "King's Palace Museum – Nyanza", fr: "Musée du Palais Royal – Nyanza", rw: "Inyubako ya Nyiri Ubutaka – Nyanza" },
        image: '/artefacts/intebe.jpg',
        description: {
            en: `The Intebe y'Umwami (Royal Throne) is one of the most treasured artefacts in Rwandan heritage. Reserved exclusively for the Mwami (King), the throne was crafted from rare woods and animal hides, adorned with intricate beadwork representing royal lineage. During coronation ceremonies, the throne was the focal point of elaborate rituals that reinforced the divine authority of Rwanda's monarchy.`,
            fr: `L'Intebe y'Umwami (Trône Royal) est l'un des artefacts les plus précieux du patrimoine rwandais. Réservé exclusivement au Mwami (Roi), le trône était fabriqué à partir de bois rares et de peaux d'animaux, orné d'un travail de perles complexe représentant la lignée royale. Lors des cérémonies de couronnement, le trône était le point focal de rituels élaborés.`,
            rw: `Intebe y'Umwami ni kimwe mu bicuruzwa by'umurage w'u Rwanda by'agaciro gakomeye. Yasoherwaga gusa na Mwami, intebe yakozwe mu biti bw'agaciro no mu ruhu rw'inyamaswa, ikinishijwe n'ubukorezi bw'amababa buhagaze umuryango w'ubwami. Mu bikorwa byo kwikanda, intebe yari aho gukorerwaho ceremony nziza.`,
        },
        source: 'Rwanda Cultural Heritage Academy',
    },
];

const ArtifactDetail = ({ language, onBack }) => {
    const t = translations[language] || translations.en;
    const [artefactIndex, setArtefactIndex] = useState(0);
    const [showChat, setShowChat] = useState(false);
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [imgError, setImgError] = useState({});
    const messagesEndRef = useRef(null);
    const artefact = ARTEFACTS[artefactIndex];

    // Set welcome message in correct language on first load / language change
    useEffect(() => {
        setMessages([{
            role: 'bot',
            text: t.welcomeMsg(artefact.museum[language] || artefact.museum.en),
            time: new Date()
        }]);
    }, [language, artefactIndex]);

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
            const res = await axios.post('/api/chat', { query: userText, language });
            setMessages(p => [...p, { role: 'bot', text: res.data.response, time: new Date() }]);
        } catch {
            setMessages(p => [...p, { role: 'bot', text: t.connectionError, time: new Date() }]);
        } finally {
            setLoading(false);
        }
    };

    const fmt = (d) => d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const title = artefact.title[language] || artefact.title.en;
    const museum = artefact.museum[language] || artefact.museum.en;
    const desc = artefact.description[language] || artefact.description.en;

    // ---- Shared Header ----
    const Header = () => (
        <div style={{ background: HEADER_BG, padding: '12px 16px', display: 'flex', alignItems: 'center', gap: '8px', color: 'white', flexShrink: 0 }}>
            <button onClick={onBack} style={{ background: 'none', border: 'none', color: 'white', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '4px', fontSize: '13px', fontWeight: '500', fontFamily: 'Inter, sans-serif' }}>
                ‹ {t.back}
            </button>
            <button style={{ background: 'none', border: 'none', color: 'white', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '4px', fontSize: '13px', fontWeight: '500', fontFamily: 'Inter, sans-serif' }}>
                ⌂ {t.home}
            </button>
            <span style={{ flex: 1, textAlign: 'center', fontSize: '12px', fontWeight: '700' }}>{museum}</span>
            <div style={{ background: 'rgba(255,255,255,0.15)', borderRadius: '20px', padding: '4px 10px', fontSize: '11px', display: 'flex', alignItems: 'center', gap: '4px', flexShrink: 0 }}>
                {LANG_LABELS[language]}
            </div>
        </div>
    );

    return (
        <div style={{ minHeight: '100vh', background: '#2C2C2C', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
            <div style={{ background: 'linear-gradient(145deg, #8B6914, #6B4F1A)', borderRadius: '40px', padding: '14px 12px 10px', boxShadow: '0 30px 80px rgba(0,0,0,0.6)', width: '360px' }}>
                <div style={{ background: CREAM_BG, borderRadius: '28px', overflow: 'hidden', height: '680px', display: 'flex', flexDirection: 'column', position: 'relative' }}>
                    <Header />

                    {/* Scrollable Content */}
                    <div style={{ flex: 1, overflowY: 'auto', paddingBottom: showChat ? '260px' : '70px', scrollbarWidth: 'none' }}>

                        {/* Artefact Image */}
                        <div style={{ position: 'relative', height: '210px', background: 'linear-gradient(135deg, #4A3728, #2C1810)', flexShrink: 0, overflow: 'hidden' }}>
                            {!imgError[artefact.id] && artefact.image ? (
                                <img
                                    src={artefact.image}
                                    alt={title}
                                    onError={() => setImgError(p => ({ ...p, [artefact.id]: true }))}
                                    style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                                />
                            ) : (
                                // Stylised placeholder when no image
                                <div style={{ width: '100%', height: '100%', background: 'linear-gradient(135deg, #4A3728 0%, #2C1810 60%, #5C3D1E 100%)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                                    <span style={{ fontSize: '48px' }}>🥁</span>
                                </div>
                            )}
                            <div style={{ position: 'absolute', inset: 0, background: 'linear-gradient(to top, rgba(0,0,0,0.65) 0%, transparent 60%)', display: 'flex', alignItems: 'flex-end', padding: '16px' }}>
                                <h2 style={{ color: 'white', fontSize: '18px', fontWeight: '700', margin: 0, textShadow: '0 1px 4px rgba(0,0,0,0.5)' }}>{title}</h2>
                            </div>
                        </div>

                        {/* Text Card */}
                        <div style={{ background: 'white', padding: '20px' }}>
                            <p style={{ color: '#4A3728', fontSize: '13px', lineHeight: '1.85', marginBottom: '16px', textAlign: 'justify' }}>
                                {desc}
                            </p>
                            <div style={{ borderTop: '1px solid #EDE7DF', paddingTop: '12px' }}>
                                <p style={{ color: BROWN_GOLD, fontSize: '12px', fontStyle: 'italic', margin: '0 0 4px' }}>{t.source}: {artefact.source}</p>
                                <p style={{ color: '#C4AE94', fontSize: '11px', margin: 0 }}>Sample artefact image (RCHA archive)</p>
                            </div>
                        </div>

                        {/* Navigation Buttons */}
                        <div style={{ display: 'flex', gap: '12px', padding: '16px 16px 8px' }}>
                            <button
                                onClick={() => { setArtefactIndex(Math.max(0, artefactIndex - 1)); setShowChat(false); }}
                                disabled={artefactIndex === 0}
                                style={{ flex: 1, padding: '13px', background: 'white', border: `1.5px solid ${artefactIndex === 0 ? '#DDD' : BROWN_GOLD}`, borderRadius: '14px', color: artefactIndex === 0 ? '#AAA' : BROWN_DARK, fontSize: '14px', fontWeight: '500', cursor: artefactIndex === 0 ? 'not-allowed' : 'pointer', fontFamily: 'Inter, sans-serif' }}
                            >
                                {t.back}
                            </button>
                            <button
                                onClick={() => { setArtefactIndex(Math.min(ARTEFACTS.length - 1, artefactIndex + 1)); setShowChat(false); }}
                                disabled={artefactIndex === ARTEFACTS.length - 1}
                                style={{ flex: 1, padding: '13px', background: artefactIndex === ARTEFACTS.length - 1 ? '#CCC' : BROWN_GOLD, border: 'none', borderRadius: '14px', color: 'white', fontSize: '14px', fontWeight: '600', cursor: artefactIndex === ARTEFACTS.length - 1 ? 'not-allowed' : 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '6px', fontFamily: 'Inter, sans-serif' }}
                            >
                                {t.next} ›
                            </button>
                        </div>

                        {/* Pagination Dots */}
                        <div style={{ display: 'flex', justifyContent: 'center', gap: '6px', paddingBottom: '12px' }}>
                            {ARTEFACTS.map((_, i) => (
                                <div key={i} style={{ width: '8px', height: '8px', borderRadius: '50%', background: i === artefactIndex ? BROWN_GOLD : '#D4C4B0', cursor: 'pointer' }} onClick={() => setArtefactIndex(i)} />
                            ))}
                        </div>
                    </div>

                    {/* Ask Questions / Hide Chat Button */}
                    {!showChat ? (
                        <div style={{ position: 'absolute', bottom: '16px', left: 0, right: 0, display: 'flex', justifyContent: 'center' }}>
                            <button
                                onClick={() => setShowChat(true)}
                                style={{ background: BROWN_DARK, color: 'white', border: 'none', borderRadius: '24px', padding: '10px 22px', fontSize: '13px', fontWeight: '600', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '8px', boxShadow: '0 4px 16px rgba(0,0,0,0.25)', fontFamily: 'Inter, sans-serif' }}
                            >
                                {t.askQuestions}
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="white"><path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z" /></svg>
                            </button>
                        </div>
                    ) : (
                        <div style={{ position: 'absolute', bottom: 0, left: 0, right: 0 }}>
                            {/* Hide Chat Button */}
                            <div style={{ display: 'flex', justifyContent: 'center', paddingBottom: '8px' }}>
                                <button
                                    onClick={() => setShowChat(false)}
                                    style={{ background: BROWN_DARK, color: 'white', border: 'none', borderRadius: '24px', padding: '8px 18px', fontSize: '12px', fontWeight: '600', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '6px', fontFamily: 'Inter, sans-serif', boxShadow: '0 2px 10px rgba(0,0,0,0.2)' }}
                                >
                                    {t.hideChat}
                                    <svg width="14" height="14" viewBox="0 0 24 24" fill="white"><path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z" /></svg>
                                </button>
                            </div>

                            {/* Chat Panel */}
                            <div style={{ background: 'white', borderTopLeftRadius: '24px', borderTopRightRadius: '24px', boxShadow: '0 -4px 20px rgba(0,0,0,0.12)', maxHeight: '270px', display: 'flex', flexDirection: 'column' }}>
                                <div style={{ padding: '16px 20px 8px' }}>
                                    <h3 style={{ color: BROWN_DARK, fontSize: '15px', fontWeight: '700', margin: '0 0 2px' }}>{t.askAboutArtefact}</h3>
                                    {messages.length <= 1 && (
                                        <p style={{ color: '#A89880', fontSize: '12px', margin: '8px 0 0', textAlign: 'center' }}>{t.chatPrompt}</p>
                                    )}
                                </div>

                                {/* Messages */}
                                <div style={{ flex: 1, overflowY: 'auto', padding: '0 16px 8px', display: 'flex', flexDirection: 'column', gap: '8px', scrollbarWidth: 'none' }}>
                                    {messages.map((msg, i) => (
                                        <div key={i} style={{ display: 'flex', justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start' }}>
                                            <div style={{ background: msg.role === 'user' ? BROWN_GOLD : '#F5F0EA', borderRadius: '12px', padding: '8px 14px', maxWidth: '82%' }}>
                                                <p style={{ color: msg.role === 'user' ? 'white' : BROWN_DARK, fontSize: '12px', lineHeight: '1.5', margin: 0 }}>{msg.text}</p>
                                                {msg.role === 'bot' && <p style={{ color: '#B0A090', fontSize: '10px', margin: '3px 0 0' }}>{fmt(msg.time)}</p>}
                                            </div>
                                        </div>
                                    ))}
                                    {loading && <p style={{ color: '#A89880', fontSize: '11px', textAlign: 'center', margin: 0 }}>{t.typing}</p>}
                                    <div ref={messagesEndRef} />
                                </div>

                                {/* Input */}
                                <form onSubmit={sendMessage} style={{ padding: '8px 12px 16px', display: 'flex', gap: '8px', alignItems: 'center', borderTop: '1px solid #F0E8E0' }}>
                                    <input
                                        value={input}
                                        onChange={e => setInput(e.target.value)}
                                        placeholder={t.chatPlaceholder}
                                        style={{ flex: 1, background: '#F5F0EA', border: '1.5px solid #E8DDD0', borderRadius: '20px', padding: '9px 16px', fontSize: '12px', color: BROWN_DARK, outline: 'none', fontFamily: 'Inter, sans-serif' }}
                                    />
                                    <button type="submit" disabled={loading} style={{ background: BROWN_GOLD, border: 'none', borderRadius: '50%', width: '36px', height: '36px', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0, opacity: loading ? 0.6 : 1 }}>
                                        <svg width="14" height="14" viewBox="0 0 24 24" fill="white"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z" /></svg>
                                    </button>
                                </form>
                            </div>
                        </div>
                    )}
                </div>
                <div style={{ width: '60px', height: '5px', background: 'rgba(255,255,255,0.3)', borderRadius: '3px', margin: '8px auto 0' }} />
            </div>
        </div>
    );
};

export default ArtifactDetail;
