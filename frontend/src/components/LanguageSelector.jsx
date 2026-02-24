import React, { useState } from 'react';
import translations from '../translations';

const BROWN_DARK = '#5C3D1E';
const BROWN_GOLD = '#8B6914';
const CREAM = '#F5F0EA';

const LanguageSelector = ({ onSelectLanguage }) => {
    const [selected, setSelected] = useState('en');
    const t = translations[selected];

    const languages = [
        { code: 'en', name: 'English' },
        { code: 'fr', name: 'Français' },
        { code: 'rw', name: 'Kinyarwanda' },
    ];

    return (
        <div style={{ minHeight: '100vh', background: '#2C2C2C', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
            {/* Phone Frame */}
            <div style={{
                background: 'linear-gradient(145deg, #8B6914, #6B4F1A)',
                borderRadius: '40px',
                padding: '14px 12px 10px',
                boxShadow: '0 30px 80px rgba(0,0,0,0.6)',
                width: '360px',
            }}>
                {/* Screen */}
                <div style={{ background: CREAM, borderRadius: '28px', overflow: 'hidden', minHeight: '600px', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '24px' }}>
                    {/* Card */}
                    <div style={{
                        background: 'white',
                        borderRadius: '20px',
                        padding: '32px 28px',
                        width: '100%',
                        boxShadow: '0 4px 20px rgba(0,0,0,0.08)',
                        textAlign: 'center',
                    }}>
                        <h1 style={{ color: BROWN_DARK, fontSize: '22px', fontWeight: '700', marginBottom: '10px', lineHeight: '1.3' }}>
                            {t.appTitle}
                        </h1>
                        <p style={{ color: BROWN_GOLD, fontSize: '13px', lineHeight: '1.6', marginBottom: '28px' }}>
                            {t.appSubtitle}
                        </p>

                        <p style={{ color: BROWN_DARK, fontSize: '13px', fontWeight: '600', marginBottom: '16px' }}>
                            {t.selectLanguage}
                        </p>

                        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginBottom: '24px' }}>
                            {languages.map((lang) => (
                                <button
                                    key={lang.code}
                                    onClick={() => setSelected(lang.code)}
                                    style={{
                                        padding: '14px',
                                        borderRadius: '12px',
                                        border: selected === lang.code ? `2px solid ${BROWN_GOLD}` : '2px solid #E8E0D8',
                                        background: selected === lang.code ? BROWN_GOLD : 'white',
                                        color: selected === lang.code ? 'white' : BROWN_DARK,
                                        fontWeight: selected === lang.code ? '600' : '400',
                                        fontSize: '15px',
                                        cursor: 'pointer',
                                        transition: 'all 0.2s',
                                        fontFamily: 'Inter, sans-serif',
                                    }}
                                >
                                    {lang.name}
                                </button>
                            ))}
                        </div>

                        <button
                            onClick={() => onSelectLanguage(selected)}
                            style={{
                                width: '100%',
                                padding: '16px',
                                background: BROWN_DARK,
                                color: 'white',
                                border: 'none',
                                borderRadius: '14px',
                                fontSize: '16px',
                                fontWeight: '700',
                                cursor: 'pointer',
                                marginBottom: '20px',
                                fontFamily: 'Inter, sans-serif',
                            }}
                        >
                            {t.start}
                        </button>

                        {/* Dots */}
                        <div style={{ display: 'flex', justifyContent: 'center', gap: '6px' }}>
                            {['#8B6914', '#C4A882', '#E0D5C8'].map((c, i) => (
                                <div key={i} style={{ width: '8px', height: '8px', borderRadius: '50%', background: c }} />
                            ))}
                        </div>
                    </div>
                </div>
                {/* Home bar */}
                <div style={{ width: '60px', height: '5px', background: 'rgba(255,255,255,0.3)', borderRadius: '3px', margin: '8px auto 0' }} />
            </div>
        </div>
    );
};

export default LanguageSelector;
