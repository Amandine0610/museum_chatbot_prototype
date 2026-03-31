import React, { useState } from 'react';
import translations from '../translations';
import ThemeToggle from './ThemeToggle';

const LanguageSelector = ({ onSelectLanguage, museumId }) => {
    const [selectedLang, setSelectedLang] = useState('en');
    const t = translations[selectedLang] || translations.en;

    const languages = [
        { code: 'en', name: 'English',     flag: '🇬🇧' },
        { code: 'fr', name: 'Français',    flag: '🇫🇷' },
        { code: 'rw', name: 'Kinyarwanda', flag: '🇷🇼' },
    ];

    const handleStart = () => {
        // museumId comes from the QR code URL; default to 1 if somehow missing
        onSelectLanguage(selectedLang, museumId || 1);
    };

    return (
        <div className="phone-frame">
            <div className="phone-notch"></div>
            <div className="phone-screen p-6 flex flex-col justify-center items-center relative">
                <div className="absolute top-4 right-4 z-10">
                    <ThemeToggle />
                </div>
                <div className="premium-card w-full text-center">

                    {/* Icon */}
                    <div className="w-14 h-14 rounded-2xl bg-museum-brown-dark flex items-center justify-center text-2xl mx-auto mb-4 shadow-md">
                        🏛️
                    </div>

                    <h1 className="text-[22px] font-bold mb-2 leading-tight text-museum-brown-dark dark:text-museum-night-text">
                        {t.appTitle}
                    </h1>
                    <p className="text-museum-brown-medium dark:text-museum-night-muted text-sm leading-relaxed mb-8 opacity-80">
                        {t.appSubtitle}
                    </p>

                    <p className="text-museum-brown-dark dark:text-museum-night-muted text-xs font-semibold uppercase tracking-widest mb-4 opacity-60">
                        {t.selectLanguage}
                    </p>

                    <div className="flex flex-col gap-3 mb-8">
                        {languages.map((lang) => (
                            <button
                                key={lang.code}
                                onClick={() => setSelectedLang(lang.code)}
                                className={`w-full py-3.5 px-5 rounded-2xl border-2 transition-all duration-300 text-[15px] font-medium flex items-center gap-3 ${
                                    selectedLang === lang.code
                                        ? 'bg-museum-brown-medium border-museum-brown-medium text-white shadow-md scale-[1.02] dark:bg-museum-gold dark:border-museum-gold dark:text-museum-brown-dark'
                                        : 'bg-white border-museum-cream-dark text-museum-brown-dark hover:bg-museum-cream-light hover:border-museum-brown-light dark:bg-museum-night-surface dark:border-museum-night-border dark:text-museum-night-text dark:hover:bg-museum-night-elevated dark:hover:border-museum-brown-light/50'
                                }`}
                            >
                                <span className="text-xl">{lang.flag}</span>
                                <span>{lang.name}</span>
                            </button>
                        ))}
                    </div>

                    <button
                        onClick={handleStart}
                        className="museum-button-primary w-full text-base py-4 shadow-[0_8px_20px_rgba(74,55,40,0.25)]"
                    >
                        {t.start}
                    </button>

                </div>
            </div>
            <div className="w-16 h-1.5 bg-white/20 dark:bg-white/10 rounded-full mx-auto my-3"></div>
        </div>
    );
};

export default LanguageSelector;
