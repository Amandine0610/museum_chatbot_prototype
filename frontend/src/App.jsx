import { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { Send, User, Bot, Loader2 } from 'lucide-react';

const API_URL = 'http://localhost:3000';

function App() {
    const [messages, setMessages] = useState([
        { role: 'bot', content: 'Muraho! I am your cultural guide. Ask me anything about Rwandan museums, history, or heritage.' }
    ]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const sendMessage = async (e) => {
        e.preventDefault();
        if (!input.trim()) return;

        const userMessage = { role: 'user', content: input };
        setMessages(prev => [...prev, userMessage]);
        setInput('');
        setIsLoading(true);

        try {
            const response = await axios.post(`${API_URL}/chat`, {
                message: userMessage.content,
                language: 'en' // Default to English for now
            });

            const botMessage = {
                role: 'bot',
                content: response.data.response || "I'm sorry, I couldn't understand that."
            };
            setMessages(prev => [...prev, botMessage]);

        } catch (error) {
            console.error('Error sending message:', error);
            const errorMessage = {
                role: 'bot',
                content: 'Sorry, I am having trouble connecting to the museum archives right now. Please try again later.'
            };
            setMessages(prev => [...prev, errorMessage]);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="flex flex-col h-screen bg-museum-bg font-sans">
            {/* Header */}
            <header className="bg-rwanda-blue text-white p-4 shadow-md flex items-center justify-between">
                <div className="flex items-center space-x-2">
                    <div className="w-10 h-10 bg-rwanda-yellow rounded-full flex items-center justify-center text-rwanda-green font-bold text-xl">
                        R
                    </div>
                    <h1 className="text-xl font-bold">Rwandan Museum Chatbot</h1>
                </div>
                <div className="text-sm opacity-90">Beta v1.0</div>
            </header>

            {/* Chat Area */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.map((msg, index) => (
                    <div
                        key={index}
                        className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                        <div
                            className={`max-w-[80%] p-4 rounded-2xl shadow-sm flex items-start space-x-3 ${msg.role === 'user'
                                    ? 'bg-rwanda-blue text-white rounded-br-none'
                                    : 'bg-white border border-gray-200 text-gray-800 rounded-bl-none'
                                }`}
                        >
                            <div className={`p-2 rounded-full ${msg.role === 'user' ? 'bg-white/20' : 'bg-gray-100'}`}>
                                {msg.role === 'user' ? <User size={18} /> : <Bot size={18} className="text-rwanda-green" />}
                            </div>
                            <div className="leading-relaxed whitespace-pre-wrap">{msg.content}</div>
                        </div>
                    </div>
                ))}
                {isLoading && (
                    <div className="flex justify-start">
                        <div className="bg-white border border-gray-200 p-4 rounded-2xl rounded-bl-none shadow-sm flex items-center space-x-3">
                            <Loader2 className="animate-spin text-rwanda-green" size={20} />
                            <span className="text-gray-500 text-sm">Consulting the archives...</span>
                        </div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <form onSubmit={sendMessage} className="p-4 bg-white border-t border-gray-200">
                <div className="max-w-4xl mx-auto flex space-x-2">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder="Ask about a museum artifact..."
                        className="flex-1 p-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-rwanda-blue focus:border-transparent transition-all"
                    />
                    <button
                        type="submit"
                        disabled={isLoading || !input.trim()}
                        className="bg-rwanda-green text-white p-3 rounded-xl hover:bg-opacity-90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                        <Send size={24} />
                    </button>
                </div>
            </form>
        </div>
    );
}

export default App;
