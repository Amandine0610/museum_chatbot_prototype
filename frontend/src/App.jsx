import React, { useState, useEffect } from 'react';
import LanguageSelector from './components/LanguageSelector';
import ArtifactDetail from './components/ArtifactDetail';
import QRAdmin from './components/QRAdmin';
import EULAModal, { isEulaAccepted } from './components/EULAModal';

function App() {
    const [language, setLanguage] = useState(null);
    const [initialArtifactId, setInitialArtifactId] = useState(null);
    const [initialMuseumId, setInitialMuseumId] = useState(null);
    const [showAdmin, setShowAdmin] = useState(false);
    const [eulaAccepted, setEulaAccepted] = useState(false);
    // true when the URL came from a QR scan (museumId present)
    const [requiresEula, setRequiresEula] = useState(false);
    const [eulaInitialLang, setEulaInitialLang] = useState('en');

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

        // Every visitor must accept the EULA once (localStorage) before the guide or chatbot.
        // Covers direct visits, QR links (?museumId=…), and shared URLs.
        setRequiresEula(true);
        setEulaAccepted(isEulaAccepted());

        if (artId) setInitialArtifactId(parseInt(artId));
        if (museumId) setInitialMuseumId(parseInt(museumId));

        if (langCode && ['en', 'fr', 'rw'].includes(langCode)) {
            setLanguage(langCode);
            setEulaInitialLang(langCode);
        }
    }, []);

    if (showAdmin) return <QRAdmin />;

    // Show EULA before anything else when the visitor scans a QR code
    if (requiresEula && !eulaAccepted) {
        return (
            <EULAModal
                initialLang={eulaInitialLang}
                onAccept={() => setEulaAccepted(true)}
                onDecline={() => {/* declined state handled inside EULAModal */}}
            />
        );
    }

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
