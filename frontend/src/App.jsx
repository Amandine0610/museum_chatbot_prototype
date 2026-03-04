import React, { useState, useEffect } from 'react';
import LanguageSelector from './components/LanguageSelector';
import ArtifactDetail from './components/ArtifactDetail';

function App() {
    const [language, setLanguage] = useState(null);
    const [initialArtifactId, setInitialArtifactId] = useState(null);

    useEffect(() => {
        const params = new URLSearchParams(window.location.search);
        const artId = params.get('id');
        const langCode = params.get('lang');

        if (artId) setInitialArtifactId(parseInt(artId));
        if (langCode && ['en', 'fr', 'rw'].includes(langCode)) {
            setLanguage(langCode);
        }
    }, []);

    return language
        ? <ArtifactDetail
            language={language}
            setLanguage={setLanguage}
            onBack={() => {
                setLanguage(null);
                setInitialArtifactId(null);
                // Clear URL params on back
                window.history.replaceState({}, document.title, "/");
            }}
            initialArtifactId={initialArtifactId}
        />
        : <LanguageSelector onSelectLanguage={setLanguage} />;
}

export default App;
