import React from 'react';
import MUSEUMS from '../data/museums';

// Simple inline QR code using the free qrcode.react library
// If that's not installed, we'll use a URL-based API instead (no install needed)
const QR_API = (url) =>
    `https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(url)}`;

const QRAdmin = () => {
    // Use window.location.origin to build the correct base URL
    const base = window.location.origin;

    return (
        <div style={{ fontFamily: 'system-ui, sans-serif', background: '#F5F0EA', minHeight: '100vh', padding: '2rem' }}>
            <div style={{ maxWidth: 900, margin: '0 auto' }}>
                <h1 style={{ color: '#5C3D1E', fontSize: '1.8rem', fontWeight: 800, marginBottom: 8 }}>
                    🏛️ Rwanda Museums — QR Code Management
                </h1>
                <p style={{ color: '#8B6914', marginBottom: '2rem', fontSize: '0.95rem' }}>
                    Print one QR code per museum and place it at the entrance. Each QR opens the chatbot in that museum's specific context.
                </p>

                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))', gap: '1.5rem' }}>
                    {MUSEUMS.map(museum => {
                        const url = `${base}/?museumId=${museum.id}`;
                        return (
                            <div key={museum.id} style={{
                                background: 'white',
                                borderRadius: 16,
                                padding: '1.5rem',
                                boxShadow: '0 4px 16px rgba(92,61,30,0.1)',
                                border: '1px solid #E8DDD0',
                                textAlign: 'center'
                            }}>
                                <img
                                    src={QR_API(url)}
                                    alt={`QR for ${museum.name.en}`}
                                    style={{ width: 180, height: 180, borderRadius: 8, marginBottom: 12 }}
                                />
                                <h3 style={{ color: '#5C3D1E', fontSize: '1rem', fontWeight: 700, marginBottom: 4 }}>
                                    Museum ID: {museum.id}
                                </h3>
                                <p style={{ color: '#5C3D1E', fontWeight: 800, fontSize: '1.05rem', marginBottom: 4 }}>
                                    {museum.name.en}
                                </p>
                                <p style={{ color: '#8B6914', fontSize: '0.8rem', marginBottom: 12 }}>
                                    📍 {museum.location}
                                </p>
                                <code style={{
                                    display: 'block',
                                    background: '#F5F0EA',
                                    padding: '0.5rem',
                                    borderRadius: 8,
                                    fontSize: '0.7rem',
                                    color: '#5C3D1E',
                                    wordBreak: 'break-all',
                                    marginBottom: 12
                                }}>
                                    {url}
                                </code>
                                <button
                                    onClick={() => window.open(url, '_blank')}
                                    style={{
                                        background: '#8B6914',
                                        color: 'white',
                                        border: 'none',
                                        borderRadius: 8,
                                        padding: '0.5rem 1rem',
                                        cursor: 'pointer',
                                        fontSize: '0.85rem',
                                        fontWeight: 600
                                    }}
                                >
                                    Test this URL ↗
                                </button>
                            </div>
                        );
                    })}
                </div>

                <div style={{ marginTop: '2rem', padding: '1rem', background: '#fff3cd', borderRadius: 12, border: '1px solid #ffc107' }}>
                    <strong>📋 How to use:</strong>
                    <ol style={{ marginTop: 8, paddingLeft: 20, color: '#5C3D1E', fontSize: '0.9rem' }}>
                        <li>Right-click each QR code image → "Save Image As" to download it</li>
                        <li>Print and place at the museum entrance</li>
                        <li>Visitors scan → language selector opens → they pick their language → museum portal opens</li>
                    </ol>
                </div>
            </div>
        </div>
    );
};

export default QRAdmin;
