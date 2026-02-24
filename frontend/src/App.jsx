import React, { useState } from 'react';
import LanguageSelector from './components/LanguageSelector';
import ArtifactDetail from './components/ArtifactDetail';

function App() {
    const [language, setLanguage] = useState(null);

    return language
        ? <ArtifactDetail language={language} onBack={() => setLanguage(null)} />
        : <LanguageSelector onSelectLanguage={setLanguage} />;
}

export default App;
