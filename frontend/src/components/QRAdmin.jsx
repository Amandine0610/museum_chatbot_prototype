import React from 'react';
import MUSEUMS from '../data/museums';
import ThemeToggle from './ThemeToggle';

const QR_API = (url) =>
    `https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(url)}`;

const QRAdmin = () => {
    const base = window.location.origin;

    return (
        <div className="min-h-screen bg-museum-cream-light dark:bg-museum-night-bg text-museum-text-main dark:text-museum-night-text p-6 md:p-10 transition-colors">
            <div className="max-w-5xl mx-auto">
                <div className="flex flex-wrap items-start justify-between gap-4 mb-8">
                    <div>
                        <h1 className="text-2xl md:text-3xl font-extrabold text-museum-brown-dark dark:text-museum-night-text mb-2">
                            Rwanda Museums — QR codes
                        </h1>
                        <p className="text-museum-brown-medium dark:text-museum-night-muted text-sm md:text-base max-w-2xl">
                            One QR per museum; each opens the guide in that museum&apos;s context.
                        </p>
                    </div>
                    <ThemeToggle />
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                    {MUSEUMS.map((museum) => {
                        const url = `${base}/?museumId=${museum.id}`;
                        return (
                            <div
                                key={museum.id}
                                className="bg-white dark:bg-museum-night-elevated rounded-2xl p-6 shadow-md border border-museum-cream-dark dark:border-museum-night-border text-center"
                            >
                                <img
                                    src={QR_API(url)}
                                    alt={`QR for ${museum.name.en}`}
                                    className="w-[180px] h-[180px] mx-auto rounded-lg mb-3"
                                />
                                <h3 className="text-museum-brown-dark dark:text-museum-gold text-sm font-bold mb-1">
                                    Museum ID: {museum.id}
                                </h3>
                                <p className="text-museum-brown-dark dark:text-museum-night-text font-bold text-base mb-1">
                                    {museum.name.en}
                                </p>
                                <p className="text-museum-brown-medium dark:text-museum-night-muted text-xs mb-3">
                                    {museum.location}
                                </p>
                                <code className="block bg-museum-cream-light dark:bg-museum-night-bg text-left text-[0.65rem] p-2 rounded-lg text-museum-brown-dark dark:text-museum-night-muted break-all mb-3">
                                    {url}
                                </code>
                                <button
                                    type="button"
                                    onClick={() => window.open(url, '_blank')}
                                    className="museum-button-primary px-4 py-2 text-sm w-full"
                                >
                                    Open URL
                                </button>
                            </div>
                        );
                    })}
                </div>

                <div className="mt-10 p-4 rounded-xl border border-amber-200 dark:border-amber-900/50 bg-amber-50 dark:bg-amber-950/30 text-sm text-museum-brown-dark dark:text-museum-night-text">
                    <strong className="block mb-2">How to use</strong>
                    <ol className="list-decimal pl-5 space-y-1 text-museum-brown-medium dark:text-museum-night-muted">
                        <li>Save each QR image (right-click → Save image).</li>
                        <li>Print and place at the museum entrance.</li>
                        <li>Visitors scan → language choice → chat opens for that museum.</li>
                    </ol>
                </div>
            </div>
        </div>
    );
};

export default QRAdmin;
