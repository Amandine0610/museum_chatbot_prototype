import React, { useState } from 'react';
import ThemeToggle from './ThemeToggle';

const EULA_STORAGE_KEY = 'rwandaMuseumEulaAccepted';

export function isEulaAccepted() {
    return localStorage.getItem(EULA_STORAGE_KEY) === 'true';
}

export function markEulaAccepted() {
    localStorage.setItem(EULA_STORAGE_KEY, 'true');
}

// ─── EULA content in all three languages ─────────────────────────────────────

const CONTENT = {
    en: {
        title: 'Terms of Use',
        subtitle: 'Rwanda Museum Interactive Guide',
        intro: 'Please read and accept the following terms before using the chatbot.',
        clauses: [
            {
                title: '1. Purpose of the System',
                body: 'This chatbot provides informational guidance about museum artifacts and exhibitions within Rwanda\'s national museums. It is designed to enhance your educational visit experience.',
            },
            {
                title: '2. Data Usage',
                body: 'The system processes your questions solely to generate responses. It does not collect, store, or share any personally identifying information. No account or registration is required.',
            },
            {
                title: '3. Third-Party Processing',
                body: 'Your queries are processed through an external AI service (Google Gemini API) to generate responses. By using this system, you acknowledge that your messages are transmitted to this third-party service in accordance with Google\'s privacy policy.',
            },
            {
                title: '4. Accuracy Disclaimer',
                body: 'The chatbot provides informational assistance based on available museum documentation. It may not always provide a perfect or complete historical interpretation. For authoritative information, please consult on-site staff or official museum publications.',
            },
            {
                title: '5. User Agreement',
                body: 'By clicking "I Agree" below, you acknowledge that you have read and understood these terms, and you consent to using the Rwanda Museum Interactive Guide chatbot under the conditions described above.',
            },
        ],
        footerNote: 'Your agreement is saved locally and will not be requested again on this device.',
        agreeBtn: 'I Agree',
        declineBtn: 'Decline',
        deniedTitle: 'Access Denied',
        deniedMsg: 'You must accept the terms to use the Rwanda Museum Interactive Guide. Please scan the QR code again and accept the agreement to continue.',
    },
    fr: {
        title: 'Conditions d\'utilisation',
        subtitle: 'Guide Interactif des Musées du Rwanda',
        intro: 'Veuillez lire et accepter les conditions suivantes avant d\'utiliser le chatbot.',
        clauses: [
            {
                title: '1. Objectif du Système',
                body: 'Ce chatbot fournit des informations sur les artefacts et les expositions des musées nationaux du Rwanda. Il est conçu pour enrichir votre expérience de visite éducative.',
            },
            {
                title: '2. Utilisation des Données',
                body: 'Le système traite vos questions uniquement pour générer des réponses. Il ne collecte, ne stocke ni ne partage aucune information personnelle identifiable. Aucun compte ni inscription n\'est requis.',
            },
            {
                title: '3. Traitement par des Tiers',
                body: 'Vos requêtes sont traitées par un service d\'intelligence artificielle externe (Google Gemini API). En utilisant ce système, vous reconnaissez que vos messages sont transmis à ce service tiers conformément à la politique de confidentialité de Google.',
            },
            {
                title: '4. Avertissement sur l\'Exactitude',
                body: 'Le chatbot fournit une assistance informative basée sur la documentation disponible des musées. Il ne peut pas toujours offrir une interprétation historique parfaite ou complète. Pour des informations officielles, veuillez consulter le personnel du musée ou les publications officielles.',
            },
            {
                title: '5. Accord de l\'Utilisateur',
                body: 'En cliquant sur « J\'accepte » ci-dessous, vous reconnaissez avoir lu et compris ces conditions, et vous consentez à utiliser le chatbot du Guide Interactif des Musées du Rwanda dans les conditions décrites ci-dessus.',
            },
        ],
        footerNote: 'Votre accord est enregistré localement et ne sera plus demandé sur cet appareil.',
        agreeBtn: 'J\'accepte',
        declineBtn: 'Refuser',
        deniedTitle: 'Accès Refusé',
        deniedMsg: 'Vous devez accepter les conditions pour utiliser le Guide Interactif des Musées du Rwanda. Veuillez scanner à nouveau le code QR et accepter l\'accord pour continuer.',
    },
    rw: {
        title: 'Amategeko y\'Ikoreshwa',
        subtitle: 'Umuyobozi w\'Imurikagurisha ry\'u Rwanda',
        intro: 'Nyamuneka soma kandi wemere amategeko akurikira mbere yo gukoresha chatbot.',
        clauses: [
            {
                title: '1. Intego y\'Uburyo',
                body: 'Iyi chatbot itanga amakuru ku bikoresho n\'ibisobanuro by\'ibirebwa mu mamuseyo y\'igihugu cy\'u Rwanda. Yagennwe kugira ngo inoroze urugendo rwawe rw\'uburezi.',
            },
            {
                title: '2. Gukoresha Amakuru',
                body: 'Uburyo busesengura ibibazo byawe gusa ngo butange ibisubizo. Ntibukusanya, ntibwubike, kandi ntibusangire amakuru agaragaza umuturage. Nta konti cyangwa kwiyandikisha bisabwa.',
            },
            {
                title: '3. Gukata Impano ya Gatatu',
                body: 'Ibibazo byawe bikorwa na serivisi ya AI y\'inyuma (Google Gemini API) ngo bitange ibisubizo. Mu gukoresha ubu buryo, wemera ko ubutumwa bwawe buhererekezwa kuri serivisi ya gatatu hakurikijwe politiki y\'ibanga ya Google.',
            },
            {
                title: '4. Integuza ku Kwizera',
                body: 'Chatbot itanga ubufasha bw\'amakuru bishingiye ku nyandiko zihari z\'imurikagurisha. Ntirashobora buri gihe gutanga isobanuro ryuzuye ry\'amateka. Ku makuru y\'ubunyamabanga, nyamuneka baza abakozi bo ahantu cyangwa inyandiko za murikagurisha.',
            },
            {
                title: '5. Amasezerano y\'Ukoresha',
                body: 'Mu gufataho "Nemera" hepfo, wemera ko wasomye kandi usobanukiwe ibi birego, kandi wemerera gukoresha chatbot y\'Umuyobozi w\'Imurikagurisha ry\'u Rwanda mu bikorwa bisobanurwa haruguru.',
            },
        ],
        footerNote: 'Amasezerano yawe abikwa mu buryo bw\'aho kandi ntazasabwa nanone kuri iki gikoresho.',
        agreeBtn: 'Nemera',
        declineBtn: 'Nanze',
        deniedTitle: 'Kwinjira Birabujijwe',
        deniedMsg: 'Ugomba kwemera amategeko kugira ngo ukoreshe Umuyobozi w\'Imurikagurisha ry\'u Rwanda. Nyamuneka suzuma kode QR nanone maze wemere amasezerano kugira ngo ukomeze.',
    },
};

const LANG_LABELS = { en: 'EN', fr: 'FR', rw: 'RW' };
const CLAUSE_ICONS = [
    // Building / Purpose
    <svg key="1" className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" /></svg>,
    // Lock / Data
    <svg key="2" className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" /></svg>,
    // Globe / Third-party
    <svg key="3" className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" /></svg>,
    // Info / Accuracy
    <svg key="4" className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>,
    // Checkmark / Agreement
    <svg key="5" className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>,
];

function EULAModal({ onAccept, onDecline, initialLang = 'en' }) {
    const [lang, setLang] = useState(['en', 'fr', 'rw'].includes(initialLang) ? initialLang : 'en');
    const [declined, setDeclined] = useState(false);

    const t = CONTENT[lang];

    function handleAccept() {
        markEulaAccepted();
        onAccept();
    }

    function handleDecline() {
        setDeclined(true);
        if (onDecline) onDecline();
    }

    if (declined) {
        return (
            <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
                <div className="bg-museum-cream-light dark:bg-museum-night-elevated rounded-2xl shadow-card max-w-sm w-full p-8 text-center border border-museum-brown-light/30 dark:border-museum-night-border">
                    <div className="w-16 h-16 rounded-full bg-red-100 dark:bg-red-950/50 flex items-center justify-center mx-auto mb-4">
                        <svg className="w-8 h-8 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01M5.07 19H19a2 2 0 001.75-2.96L13.75 4a2 2 0 00-3.5 0L3.25 16.04A2 2 0 005.07 19z" />
                        </svg>
                    </div>
                    <h2 className="text-xl font-semibold text-museum-text-main dark:text-museum-night-text mb-2">{t.deniedTitle}</h2>
                    <p className="text-museum-text-muted dark:text-museum-night-muted text-sm leading-relaxed">{t.deniedMsg}</p>
                </div>
            </div>
        );
    }

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
            <div
                className="bg-museum-cream-light dark:bg-museum-night-surface rounded-2xl shadow-card w-full max-w-lg border border-museum-brown-light/30 dark:border-museum-night-border flex flex-col"
                style={{ maxHeight: '90vh' }}
                role="dialog"
                aria-modal="true"
                aria-labelledby="eula-title"
            >
                <div className="bg-museum-brown-dark dark:bg-[#2d241c] rounded-t-2xl px-6 py-4 flex-shrink-0">
                    <div className="flex items-center justify-between mb-2 gap-2">
                        <div className="flex items-center gap-3 min-w-0">
                            <div className="w-8 h-8 rounded-full bg-museum-gold/20 flex items-center justify-center flex-shrink-0">
                                <svg className="w-4 h-4 text-museum-gold" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                                </svg>
                            </div>
                            <div>
                                <h2 id="eula-title" className="text-white font-semibold text-sm leading-tight">
                                    {t.title}
                                </h2>
                                <p className="text-museum-gold text-xs">{t.subtitle}</p>
                            </div>
                        </div>

                        <div className="flex items-center gap-1.5 flex-shrink-0">
                            <ThemeToggle className="!border-white/25 !bg-white/10 !text-white hover:!bg-white/20 scale-90" />
                            <div className="flex gap-1">
                                {['en', 'fr', 'rw'].map((l) => (
                                    <button
                                        key={l}
                                        onClick={() => setLang(l)}
                                        className={`px-2.5 py-1 rounded-md text-xs font-semibold transition-all ${
                                            lang === l
                                                ? 'bg-museum-gold text-museum-brown-dark'
                                                : 'bg-white/10 text-white/70 hover:bg-white/20'
                                        }`}
                                    >
                                        {LANG_LABELS[l]}
                                    </button>
                                ))}
                            </div>
                        </div>
                    </div>

                    <div className="flex rounded-sm overflow-hidden h-1 mt-2">
                        <div className="flex-1 bg-[#20603D]" />
                        <div className="flex-1 bg-[#FAD201]" />
                        <div className="flex-1 bg-[#20603D]" />
                    </div>
                </div>

                <div className="overflow-y-auto flex-1 px-6 py-4 no-scrollbar">
                    <p className="text-museum-text-muted dark:text-museum-night-muted text-xs mb-4 leading-relaxed">{t.intro}</p>

                    <div className="space-y-3">
                        {t.clauses.map((clause, i) => (
                            <div key={i} className="rounded-xl border border-museum-cream-dark dark:border-museum-night-border bg-white/60 dark:bg-museum-night-elevated/80 p-4">
                                <div className="flex items-start gap-3">
                                    <div className="w-7 h-7 rounded-lg bg-museum-brown-dark/10 dark:bg-museum-night-bg flex items-center justify-center flex-shrink-0 mt-0.5 text-museum-brown-dark dark:text-museum-gold">
                                        {CLAUSE_ICONS[i]}
                                    </div>
                                    <div>
                                        <h3 className="text-museum-text-main dark:text-museum-night-text font-semibold text-sm mb-1">{clause.title}</h3>
                                        <p className="text-museum-text-muted dark:text-museum-night-muted text-xs leading-relaxed">{clause.body}</p>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                <div className="flex-shrink-0 px-6 py-4 border-t border-museum-cream-dark dark:border-museum-night-border bg-museum-cream-light dark:bg-museum-night-surface rounded-b-2xl">
                    <p className="text-museum-text-muted dark:text-museum-night-muted text-xs text-center mb-3">{t.footerNote}</p>
                    <div className="flex gap-3">
                        <button
                            onClick={handleDecline}
                            className="flex-1 py-3 px-4 rounded-xl border-2 border-museum-brown-light dark:border-museum-night-border text-museum-text-main dark:text-museum-night-text font-medium text-sm transition-all hover:bg-museum-cream-dark dark:hover:bg-museum-night-elevated active:scale-95"
                        >
                            {t.declineBtn}
                        </button>
                        <button
                            onClick={handleAccept}
                            className="flex-1 py-3 px-4 rounded-xl bg-museum-brown-dark dark:bg-museum-gold dark:text-museum-brown-dark text-white font-semibold text-sm transition-all hover:bg-museum-brown-medium dark:hover:bg-museum-gold/90 active:scale-95 shadow-md"
                        >
                            {t.agreeBtn}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default EULAModal;
