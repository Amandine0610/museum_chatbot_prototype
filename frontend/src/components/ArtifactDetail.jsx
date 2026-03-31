import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import translations from '../translations';
import MUSEUMS from '../data/museums';
import ThemeToggle from './ThemeToggle';

const LANG_META = {
    en: { label: 'English',     flag: '🇬🇧', next: 'fr' },
    fr: { label: 'Français',    flag: '🇫🇷', next: 'rw' },
    rw: { label: 'Kinyarwanda', flag: '🇷🇼', next: 'en' },
};

/* Suggestions per language to spark conversation */
const SUGGESTIONS = {
    en: ['Opening hours?', 'Tell me the history', 'What can I see here?', 'Who founded this museum?'],
    fr: ['Horaires d\'ouverture?', 'Parlez-moi de l\'histoire', 'Que puis-je voir ici?', 'Qui a fondé ce musée?'],
    rw: ['Amasaha y\'ifungura?', 'Mfashishe amateka', 'Ni iki nshobora kureba?', 'Ni nde washinze iyi ngoro?'],
};

const ArtifactDetail = ({ language, setLanguage, onBack, initialMuseumId }) => {
    const t = translations[language] || translations.en;
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [showSuggestions, setShowSuggestions] = useState(true);
    const messagesEndRef = useRef(null);
    const inputRef = useRef(null);

    const currentMuseum = MUSEUMS.find(m => m.id === initialMuseumId) || MUSEUMS[0];
    const museumName = currentMuseum.name[language] || currentMuseum.name.en;

    const cycleLanguage = () => {
        setLanguage(LANG_META[language]?.next || 'en');
    };

    useEffect(() => {
        let active = true;
        setMessages([]);
        setShowSuggestions(true);
        setLoading(true);

        const fetchWelcome = async () => {
            try {
                const apiUrl = import.meta.env.VITE_API_URL || '';
                const res = await axios.post(`${apiUrl}/api/chat`, {
                    query: 'special:welcome',
                    language,
                    museumId: initialMuseumId,
                }, { timeout: 90000 });
                if (active) {
                    setMessages([{
                        role: 'bot',
                        text: res.data.response.replace(/\*\*/g, '').replace(/__/g, ''),
                        time: new Date(),
                    }]);
                }
            } catch {
                if (active) {
                    setMessages([{
                        role: 'bot',
                        text: t.welcomeMsg(museumName),
                        time: new Date(),
                    }]);
                }
            } finally {
                if (active) setLoading(false);
            }
        };

        fetchWelcome();
        return () => { active = false; };
    }, [language, initialMuseumId]);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages, loading]);

    const sendMessage = async (text) => {
        const userText = (text || input).trim();
        if (!userText || loading) return;
        setInput('');
        setShowSuggestions(false);
        setMessages(prev => [...prev, { role: 'user', text: userText, time: new Date() }]);
        setLoading(true);

        try {
            const apiUrl = import.meta.env.VITE_API_URL || '';
            const res = await axios.post(`${apiUrl}/api/chat`, {
                query: userText,
                language,
                museumId: initialMuseumId,
            }, { timeout: 90000 });
            let reply = res.data.response
                .replace(/\*\*/g, '')
                .replace(/__/g, '');
            setMessages(prev => [...prev, { role: 'bot', text: reply, time: new Date() }]);
        } catch (err) {
            const errMsg = err.response
                ? `Error ${err.response.status}`
                : t.connectionError;
            setMessages(prev => [...prev, { role: 'bot', text: errMsg, time: new Date(), isError: true }]);
        } finally {
            setLoading(false);
            inputRef.current?.focus();
        }
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        sendMessage();
    };

    const fmt = (d) => d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    return (
        <div className="phone-frame">
            <div className="phone-notch"></div>
            <div className="phone-screen flex flex-col bg-[#F5F0EA] dark:bg-museum-night-bg">

                {/* ── TOP HEADER ── */}
                <header className="bg-museum-brown-dark dark:bg-[#2d241c] px-4 py-3 flex items-center justify-between text-white z-20 shadow-lg flex-shrink-0 border-b border-black/10 dark:border-white/5">
                    <div className="flex items-center gap-3">
                        <button
                            onClick={onBack}
                            className="p-1.5 hover:bg-white/10 rounded-full transition-colors"
                            aria-label="Back"
                        >
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                                <polyline points="15 18 9 12 15 6"></polyline>
                            </svg>
                        </button>
                        <div>
                            <p className="text-[9px] font-bold uppercase tracking-[0.15em] text-museum-gold opacity-90">
                                Official Guide
                            </p>
                            <h1 className="text-[13px] font-bold leading-tight truncate max-w-[170px]">
                                {museumName}
                            </h1>
                        </div>
                    </div>
                    <div className="flex items-center gap-2">
                        <ThemeToggle className="!border-white/25 !bg-white/10 !text-white hover:!bg-white/20" />
                        <button
                            onClick={cycleLanguage}
                            className="flex items-center gap-1.5 bg-white/10 hover:bg-white/20 border border-white/20 px-3 py-1.5 rounded-full transition-all text-[11px] font-bold"
                        >
                            <span>{LANG_META[language]?.flag}</span>
                            <span>{LANG_META[language]?.label}</span>
                        </button>
                    </div>
                </header>

                <div className="relative h-36 overflow-hidden flex-shrink-0">
                    <img
                        src={currentMuseum.image}
                        alt={museumName}
                        className="w-full h-full object-cover"
                        onError={e => { e.target.style.display = 'none'; }}
                    />
                    <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-black/20 to-transparent" />
                    {/* Online badge */}
                    <div className="absolute bottom-3 left-4 flex items-center gap-2">
                        <div className="w-7 h-7 rounded-full bg-museum-gold/20 border border-museum-gold/50 backdrop-blur-sm flex items-center justify-center text-sm">
                            🏛️
                        </div>
                        <div>
                            <p className="text-white text-[11px] font-semibold leading-none">{museumName}</p>
                            <div className="flex items-center gap-1 mt-0.5">
                                <span className="w-1.5 h-1.5 bg-green-400 rounded-full animate-pulse"></span>
                                <p className="text-[9px] text-green-300 font-medium uppercase tracking-wide">
                                    {language === 'fr' ? 'En ligne' : language === 'rw' ? 'Kuri interineti' : 'Online'}
                                </p>
                            </div>
                        </div>
                    </div>
                </div>

                <div className="flex-1 overflow-y-auto px-4 py-3 flex flex-col gap-3 no-scrollbar pb-32">

                    {messages.map((msg, i) => (
                        <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} animate-fade-in`}>
                            {msg.role === 'bot' && (
                                <div className="w-7 h-7 rounded-full bg-museum-brown-dark flex items-center justify-center text-xs mr-2 mt-0.5 flex-shrink-0 shadow-sm">
                                    🏛️
                                </div>
                            )}
                            <div className={`max-w-[78%] ${msg.role === 'user' ? 'max-w-[72%]' : ''}`}>
                                <div className={`px-4 py-3 rounded-2xl text-[13.5px] leading-[1.65] shadow-sm ${
                                    msg.role === 'user'
                                        ? 'bg-museum-brown-medium text-white rounded-tr-sm dark:bg-museum-brown-medium/90'
                                        : msg.isError
                                            ? 'bg-red-50 text-red-700 border border-red-100 rounded-tl-sm dark:bg-red-950/40 dark:text-red-200 dark:border-red-900/50'
                                            : 'bg-white text-museum-brown-dark border border-museum-cream-dark rounded-tl-sm dark:bg-museum-night-elevated dark:text-museum-night-text dark:border-museum-night-border'
                                }`}>
                                    <p className="whitespace-pre-wrap">{msg.text}</p>
                                </div>
                                <p className={`text-[9px] mt-1 font-medium opacity-40 uppercase tracking-wider ${
                                    msg.role === 'user'
                                        ? 'text-right text-museum-brown-medium dark:text-museum-night-muted'
                                        : 'text-museum-brown-medium dark:text-museum-night-muted'
                                }`}>
                                    {fmt(msg.time)}
                                </p>
                            </div>
                        </div>
                    ))}

                    {/* Typing indicator */}
                    {loading && (
                        <div className="flex justify-start">
                            <div className="w-7 h-7 rounded-full bg-museum-brown-dark flex items-center justify-center text-xs mr-2 flex-shrink-0">
                                🏛️
                            </div>
                            <div className="bg-white border border-museum-cream-dark px-4 py-3 rounded-2xl rounded-tl-sm shadow-sm dark:bg-museum-night-elevated dark:border-museum-night-border">
                                <div className="flex gap-1 items-center h-4">
                                    <span className="w-1.5 h-1.5 bg-museum-brown-medium/60 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                                    <span className="w-1.5 h-1.5 bg-museum-brown-medium/60 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                                    <span className="w-1.5 h-1.5 bg-museum-brown-medium/60 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                                </div>
                            </div>
                        </div>
                    )}

                    <div ref={messagesEndRef} />
                </div>

                <div className="absolute bottom-0 left-0 right-0 bg-white/90 backdrop-blur-md border-t border-museum-cream-dark px-4 pt-3 pb-5 flex-shrink-0 dark:bg-museum-night-surface/95 dark:border-museum-night-border dark:backdrop-blur-lg" style={{ maxWidth: 'inherit' }}>

                    {showSuggestions && messages.length > 0 && !loading && (
                        <div className="flex gap-2 overflow-x-auto no-scrollbar mb-3 pb-0.5">
                            {SUGGESTIONS[language]?.map((s, i) => (
                                <button
                                    key={i}
                                    onClick={() => sendMessage(s)}
                                    className="flex-shrink-0 text-[11px] font-medium px-3 py-1.5 bg-museum-cream-light border border-museum-brown-light/30 text-museum-brown-dark rounded-full hover:bg-museum-brown-light/20 hover:border-museum-brown-medium/40 transition-all whitespace-nowrap dark:bg-museum-night-elevated dark:border-museum-night-border dark:text-museum-night-text dark:hover:bg-museum-night-border/80"
                                >
                                    {s}
                                </button>
                            ))}
                        </div>
                    )}

                    <form onSubmit={handleSubmit} className="flex gap-2 items-end">
                        <div className="flex-1 relative">
                            <input
                                ref={inputRef}
                                value={input}
                                onChange={e => setInput(e.target.value)}
                                placeholder={t.chatPlaceholder}
                                disabled={loading}
                                className="w-full bg-[#F5F0EA] border-2 border-transparent focus:border-museum-brown-medium/30 focus:bg-white rounded-2xl py-3 px-4 text-[13px] text-museum-brown-dark placeholder:text-museum-brown-light/50 outline-none transition-all duration-200 font-medium disabled:opacity-60 dark:bg-museum-night-bg dark:text-museum-night-text dark:placeholder:text-museum-night-muted focus:dark:bg-museum-night-elevated focus:dark:border-museum-brown-light/40"
                            />
                        </div>
                        <button
                            type="submit"
                            disabled={loading || !input.trim()}
                            className={`w-11 h-11 rounded-xl flex items-center justify-center transition-all duration-200 flex-shrink-0 ${
                                loading || !input.trim()
                                    ? 'bg-museum-cream-dark text-museum-brown-light/30 cursor-not-allowed dark:bg-museum-night-border dark:text-museum-night-muted'
                                    : 'bg-museum-brown-dark text-white hover:bg-museum-brown-medium active:scale-95 shadow-md dark:bg-museum-gold dark:text-museum-brown-dark dark:hover:bg-museum-gold/90'
                            }`}
                        >
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                                <line x1="22" y1="2" x2="11" y2="13"></line>
                                <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
                            </svg>
                        </button>
                    </form>
                </div>

            </div>
        </div>
    );
};

export default ArtifactDetail;
