import express from 'express';

const router = express.Router();

const ARTEFACTS = {
    ingabo: [
        {
            id: 'inzira',
            name: 'Inzira y\'Inzitane',
            name_rw: 'Inzira y\'Inzitane',
            name_fr: 'Le Chemin de la Résilience',
            description: 'The symbolic journey of 30 years of survival and resilience',
            description_rw: 'Indome y\'imyaka 30 yo kubikira no gutahana',
            description_fr: 'Le parcours symbolique de 30 ans de survie et de résilience'
        },
        {
            id: 'king-ngabo',
            name: 'King Ngabo Exhibit',
            name_rw: 'Ishusho y Umwami Ngabo',
            name_fr: 'Exposition du Roi Ngabo',
            description: 'Biography of King Ngabo, founder of the museum',
            description_rw: 'Ibitabo by Umwami Ngabo, wavuze ishyingiro',
            description_fr: 'Biographie du Roi Ngabo, fondateur du musée'
        }
    ],
    ethnographic: [
        {
            id: 'traditional-arts',
            name: 'Traditional Arts',
            name_rw: 'Ibyuma by\'Umuco',
            name_fr: 'Arts Traditionnels',
            description: 'Collection of traditional Rwandan crafts and pottery',
            description_rw: 'Ibyuma bikoresho n\'ibikoresho by\'umuco',
            description_fr: 'Collection d\'artisanat traditionnel rwandais'
        }
    ]
};

/**
 * GET /api/artefacts/:museumId
 * Get artefacts for a specific museum
 */
router.get('/:museumId', (req, res) => {
    const { museumId } = req.params;
    const { lang } = req.query;

    const artefacts = ARTEFACTS[museumId];

    if (!artefacts) {
        return res.json([]);
    }

    const localized = artefacts.map(artefact => ({
        id: artefact.id,
        name: lang === 'rw' ? artefact.name_rw :
            lang === 'fr' ? artefact.name_fr :
                artefact.name,
        description: lang === 'rw' ? artefact.description_rw :
            lang === 'fr' ? artefact.description_fr :
                artefact.description
    }));

    res.json(localized);
});

export default router;
