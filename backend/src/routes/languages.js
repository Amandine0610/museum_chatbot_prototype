import express from 'express';

const router = express.Router();

const LANGUAGES = [
    {
        code: 'en',
        name: 'English',
        nativeName: 'English',
        flag: '🇬🇧'
    },
    {
        code: 'fr',
        name: 'Français',
        nativeName: 'French',
        flag: '🇫🇷'
    },
    {
        code: 'rw',
        name: 'Kinyarwanda',
        nativeName: 'Kinyarwanda',
        flag: '🇷🇼'
    }
];

/**
 * GET /api/languages
 * Get list of supported languages
 */
router.get('/', (req, res) => {
    res.json(LANGUAGES);
});

export default router;
