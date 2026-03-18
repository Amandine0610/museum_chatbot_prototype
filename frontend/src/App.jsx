import React, { useState, useEffect } from 'react';
import LanguageSelector from './components/LanguageSelector';
import ArtifactDetail from './components/ArtifactDetail';
import QRAdmin from './components/QRAdmin';

function App() {
    const [language, setLanguage] = useState(null);
    const [initialArtifactId, setInitialArtifactId] = useState(null);
    const [initialMuseumId, setInitialMuseumId] = useState(null);
    const [showAdmin, setShowAdmin] = useState(false);

    useEffect(() => {
        const params = new URLSearchParams(window.location.search);
        const artId = params.get('id');
        const museumId = params.get('museumId');
        const langCode = params.get('lang');
        const admin = params.get('admin');

        if (admin === 'qr') {
            setShowAdmin(true);
            return;
        }

        if (artId) setInitialArtifactId(parseInt(artId));
        if (museumId) setInitialMuseumId(parseInt(museumId));

        // If a museumId is in the URL, auto-select language (default English)
        // so the visitor lands directly in the museum portal after the language screen
        if (langCode && ['en', 'fr', 'rw'].includes(langCode)) {
            setLanguage(langCode);
        }
    }, []);

    if (showAdmin) return <QRAdmin />;

    return language
        ? <ArtifactDetail
            language={language}
            setLanguage={setLanguage}
            onBack={() => {
                setLanguage(null);
                setInitialArtifactId(null);
                setInitialMuseumId(null);
                window.history.replaceState({}, document.title, "/");
            }}
            initialArtifactId={initialArtifactId}
            initialMuseumId={initialMuseumId}
        />
        : <LanguageSelector
            onSelectLanguage={(lang, museumId) => {
                setLanguage(lang);
                if (museumId) setInitialMuseumId(museumId);
            }}
            museumId={initialMuseumId}
        />;
}

export default App;
