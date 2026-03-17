import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import translations from '../translations';
import MUSEUMS from '../data/museums';

const LANG_LABELS = { en: 'English', fr: 'Français', rw: 'Kinyarwanda' };

const ArtifactDetail = ({ language, setLanguage, onBack, initialArtifactId, initialMuseumId }) => {
    const t = translations[language] || translations.en;
    
    const [showChat, setShowChat] = useState(true); // Integrated chat is now primary
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const messagesEndRef = useRef(null);

    // Get current museum info
    const currentMuseum = MUSEUMS.find(m => m.id === initialMuseumId) || MUSEUMS[0];

    const nextLanguage = () => {
        const langs = Object.keys(LANG_LABELS);
        const idx = langs.indexOf(language);
        const next = langs[(idx + 1) % langs.length];
        setLanguage(next);
    };

    // Intelligent Initial Greeting
    useEffect(() => {
        let isMounted = true;
        const fetchWelcome = async () => {
            setLoading(true);
            try {
                const apiUrl = import.meta.env.VITE_API_URL || '';
                const res = await axios.post(`${apiUrl}/api/chat`, { 
                    query: 'special:welcome', 
                    language,
                    museumId: initialMuseumId 
                });
                
                if (isMounted) {
                    setMessages([{
                        role: 'bot',
                        text: res.data.response.replace(/\*\*/g, ''),
                        time: new Date()
                    }]);
                }
            } catch (error) {
                // Fallback to minimal greeting if API fails
                if (isMounted) {
                    const museumName = currentMuseum.name[language] || currentMuseum.name.en;
                    setMessages([{
                        role: 'bot',
                        text: `Welcome to ${museumName}!`,
                        time: new Date()
                    }]);
                }
            } finally {
                if (isMounted) setLoading(false);
            }
        };

        fetchWelcome();
        return () => { isMounted = false; };
    }, [language, initialMuseumId]);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const sendMessage = async (e) => {
        e.preventDefault();
        if (!input.trim() || loading) return;
        const userText = input.trim();
        setInput('');
        setMessages(p => [...p, { role: 'user', text: userText, time: new Date() }]);
        setLoading(true);
        try {
            const apiUrl = import.meta.env.VITE_API_URL || '';
            const res = await axios.post(`${apiUrl}/api/chat`, { 
                query: userText, 
                language,
                museumId: initialMuseumId 
            });

            let botResponse = res.data.response;
            // Clean up Markdown-like bolding for raw text display if needed
            botResponse = botResponse.replace(/\*\*/g, ''); 

            setMessages(p => [...p, { role: 'bot', text: botResponse, time: new Date() }]);

        } catch (error) {
            const errorMsg = error.response
                ? `Error ${error.response.status}: ${JSON.stringify(error.response.data)}`
                : `Network Error: ${error.message}`;

            setMessages(p => [...p, {
                role: 'bot',
                text: `I'm having a bit of trouble connecting to the archives. Please try again in a moment.\n\n[Diagnostic]: ${errorMsg}\n[Target URL]: ${apiUrl || 'Current Origin (Local)'}`,
                time: new Date()
            }]);
        } finally {
            setLoading(false);
        }
    };

    const fmt = (d) => d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    const Header = () => (
        <header className="bg-museum-brown-dark px-4 py-3 flex items-center justify-between text-white z-20 shadow-md">
            <div className="flex items-center gap-4">
                <button onClick={onBack} className="p-1.5 hover:bg-white/10 rounded-full transition-colors">
                    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><polyline points="15 18 9 12 15 6"></polyline></svg>
                </button>
                <div className="flex flex-col">
                    <h1 className="text-sm font-bold leading-none mb-1">{currentMuseum.name[language] || currentMuseum.name.en}</h1>
                    <div className="flex items-center gap-1.5">
                        <span className="w-1.5 h-1.5 bg-green-400 rounded-full animate-pulse"></span>
                        <p className="text-[10px] text-museum-gold opacity-80 font-bold uppercase tracking-wider">v3.9 Live Archives</p>
                    </div>
                </div>
            </div>
            <button
                onClick={nextLanguage}
                className="bg-white/15 px-3 py-1.5 rounded-full text-[11px] font-bold border border-white/10 backdrop-blur-sm hover:bg-white/30 transition-all flex items-center gap-1.5"
            >
                <span>🌐</span>
                {LANG_LABELS[language]}
            </button>
        </header>
    );

    const MuseumHero = () => (
        <div className="relative h-48 overflow-hidden bg-museum-brown-dark flex items-center justify-center">
            <img 
                src={currentMuseum?.image} 
                className="absolute inset-0 w-full h-full object-cover opacity-70" 
                alt="Museum Hero"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent"></div>
            <div className="absolute bottom-4 left-6 right-6 flex items-center gap-4">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-museum-gold flex items-center justify-center text-museum-brown-dark shadow-sm">
                        <span className="text-xl font-bold">🏛️</span>
                    </div>
                    <div>
                        <h1 className="text-lg font-bold leading-tight">{currentMuseum.name[language] || currentMuseum.name.en}</h1>
                        <div className="flex items-center gap-2">
                            <p className="text-xs text-museum-gold opacity-90 font-medium">Digital Curator v3.9</p>
                            <span className="w-1.5 h-1.5 bg-green-400 rounded-full animate-pulse"></span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );

    return (
        <div className="phone-frame">
            <div className="phone-notch"></div>
            <div className="phone-screen flex flex-col bg-museum-cream-light">
                <Header />
                <MuseumHero />

                {/* Main Chat Interface */}
                <div className="flex-1 flex flex-col relative overflow-hidden">
                    <div className="flex-1 overflow-y-auto px-6 py-4 flex flex-col gap-4 no-scrollbar pb-24">
                        {/* Messages Flow */}
                        {messages.map((msg, i) => (
                            <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} animate-fade-in`}>
                                <div className={`p-4 rounded-2xl text-[14px] leading-[1.6] shadow-sm max-w-[85%] whitespace-pre-wrap ${msg.role === 'user'
                                    ? 'bg-museum-brown-medium text-white rounded-tr-none font-medium'
                                    : 'bg-white text-museum-brown-dark rounded-tl-none border border-museum-cream-dark'
                                    }`}>
                                    <p>{msg.text}</p>
                                    <p className={`text-[9px] mt-2 font-bold uppercase tracking-widest opacity-40 ${msg.role === 'user' ? 'text-white' : 'text-museum-brown-medium'}`}>
                                        {fmt(msg.time)}
                                    </p>
                                </div>
                            </div>
                        ))}
                        {loading && (
                            <div className="flex justify-start">
                                <div className="flex gap-1.5 items-center bg-white px-4 py-3 rounded-2xl border border-museum-cream-dark">
                                    <div className="w-1.5 h-1.5 bg-museum-brown-medium rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                                    <div className="w-1.5 h-1.5 bg-museum-brown-medium rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                                    <div className="w-1.5 h-1.5 bg-museum-brown-medium rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                                </div>
                            </div>
                        )}
                        <div ref={messagesEndRef} />
                    </div>

                    {/* Fixed Input Bar */}
                    <div className="absolute bottom-0 left-0 right-0 bg-white/80 backdrop-blur-md border-t border-museum-cream-dark p-6 pb-8">
                        <form onSubmit={sendMessage} className="flex gap-3 items-center">
                            <div className="flex-1 relative">
                                <input
                                    value={input}
                                    onChange={e => setInput(e.target.value)}
                                    placeholder="Ask about artifacts..."
                                    className="w-full bg-museum-cream-light border-2 border-transparent focus:border-museum-brown-medium/20 focus:bg-white rounded-2xl py-3.5 px-5 text-sm text-museum-brown-dark placeholder:text-museum-brown-light/50 outline-none transition-all duration-300 font-medium"
                                />
                            </div>
                            <button
                                type="submit"
                                disabled={loading || !input.trim()}
                                className={`w-12 h-12 rounded-2xl flex items-center justify-center transition-all duration-300 shadow-md ${loading || !input.trim()
                                    ? 'bg-museum-cream-dark text-museum-brown-light/30 cursor-not-allowed'
                                    : 'bg-museum-brown-medium text-white hover:bg-museum-brown-dark active:scale-95'
                                    }`}
                            >
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
                            </button>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ArtifactDetail;
