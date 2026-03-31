import express from 'express';

const router = express.Router();

// Museum data - in production, this would come from a database
const MUSEUMS = [
  {
    id: 'ingabo',
    name: 'Museum Ingabo',
    name_rw: 'Ishyingiro ry\'Ingabo',
    name_fr: 'Musée Ingabo',
    location: 'Rwanda',
    description: 'Museum Ingabo is dedicated to preserving the cultural heritage of Rwanda, featuring the Inzira y\'Inzitane exhibition.',
    description_rw: 'Ishyingiro ry\'Ingabo ryifashishwa mu kubika ibihe by\'umuco w\'u Rwanda, rifite ibitekerezo byo mu nzira y\'inzitane.',
    description_fr: 'Le Musée Ingabo est dédié à la préservation du patrimoine culturel du Rwanda, avec l\'exposition Inzira y\'Inzitane.'
  },
  {
    id: 'ethnographic',
    name: 'Ethnographic Museum Huye',
    name_rw: 'Ishyingiro ry\'Imiterere y\'Ubumenyi',
    name_fr: 'Musée Ethnographique de Huye',
    location: 'Huye, Rwanda',
    description: 'One of the finest museums in East Africa, showcasing Rwandan cultural artifacts and traditional crafts.',
    description_rw: 'Kimwe mu mishyingiro myiza y\'Afrika y\'Iburasirazuba, ikwerekeye ibikoresho by\'umuco w\'u Rwanda.',
    description_fr: 'L\'un des meilleurs musées d\'Afrique de l\'Est, présentant des artefacts culturels rwandais.'
  },
  {
    id: 'kings_palace',
    name: 'King\'s Palace Museum',
    name_rw: 'Ishyingiro ry\'Umugenge',
    name_fr: 'Musée du Palais Royal',
    location: 'Nyanza, Rwanda',
    description: 'A reconstructed royal palace showcasing traditional Rwandan architecture and the legacy of the monarchy.',
    description_rw: 'Umugenge wifashishije kubaka ibyapa by\'umuco w\'u Rwanda n\'ibikingi by\'umwami.',
    description_fr: 'Un palais royal reconstruit présentant l\'architecture traditionnelle rwandaise.'
  },
  {
    id: 'genocide_memorial',
    name: 'Kigali Genocide Memorial',
    name_rw: 'Ishyingiro ry\'Ikarengera',
    name_fr: 'Mémorial du Génocide de Kigali',
    location: 'Kigali, Rwanda',
    description: 'A place of remembrance for the 1994 genocide victims, dedicated to education and prevention.',
    description_rw: 'Ahantu h\'ikundaniro y\'abarwayi ba Jenoside yo muri 1994, hifashishijwe mu bubу n\'ugukingira.',
    description_fr: 'Un lieu de mémoire pour les victimes du génocide de 1994, dédié à l\'éducation et à la prévention.'
  }
];

/**
 * GET /api/museums
 * Get list of all museums
 */
router.get('/', (req, res) => {
  const { lang } = req.query;

  const localizedMuseums = MUSEUMS.map(museum => ({
    id: museum.id,
    name: lang === 'rw' ? museum.name_rw :
      lang === 'fr' ? museum.name_fr :
        museum.name,
    location: museum.location,
    description: lang === 'rw' ? museum.description_rw :
      lang === 'fr' ? museum.description_fr :
        museum.description
  }));

  res.json(localizedMuseums);
});

/**
 * GET /api/museums/:id
 * Get specific museum by ID
 */
router.get('/:id', (req, res) => {
  const { id } = req.params;
  const { lang } = req.query;

  const museum = MUSEUMS.find(m => m.id === id);

  if (!museum) {
    return res.status(404).json({ error: 'Museum not found' });
  }

  res.json({
    id: museum.id,
    name: lang === 'rw' ? museum.name_rw :
      lang === 'fr' ? museum.name_fr :
        museum.name,
    location: museum.location,
    description: lang === 'rw' ? museum.description_rw :
      lang === 'fr' ? museum.description_fr :
        museum.description
  });
});

export default router;