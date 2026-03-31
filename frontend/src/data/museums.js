const MUSEUMS = [
    {
        id: 1,
        name: { en: "King's Palace Museum", fr: "Musée du Palais Royal", rw: "Ingoro y'Abami i Nyanza" },
        location: "Nyanza, Southern Province",
        image: "/museums/kings_palace.jpg",
        logo: "/museums/rcha_logo.png",
        description: {
            en: "A reconstruction of the traditional royal residence, the King's Palace Museum offers a detailed look at Rwandan monarchical system and its 19th-century architecture.",
            fr: "Une reconstitution de la résidence royale traditionnelle, le Musée du Palais Royal offre un aperçu détaillé du système monarchique rwandais et de son architecture du XIXe siècle.",
            rw: "Ingoro y'Abami i Nyanza ikubiyemo amateka y'ubwami bw'u Rwanda n'imyubakire gakondo yo hambere."
        }
    },
    {
        id: 2,
        name: { en: "Ethnographic Museum", fr: "Musée Ethnographique", rw: "Inzu ndangamurage y'Imyubakire n'Amateka i Huye" },
        location: "Huye, Southern Province",
        image: "/museums/ethnographic.jpg",
        logo: "/museums/rcha_logo.png",
        description: {
            en: "One of Africa's finest ethnographic collections, this museum depicts Rwandan history from ancient times to the modern era across seven galleries.",
            fr: "L'une des plus belles collections ethnographiques d'Afrique, ce musée dépeint l'histoire du Rwanda de l'Antiquité à l'ère moderne à travers sept galeries.",
            rw: "Iyi ngoro irimo bimwe mu bikoresho by'amateka n'umuco by'u Rwanda kuva mu bihe bya kera kugeza ubu."
        }
    },
    {
        id: 3,
        name: { en: "Museum Ingabo", fr: "Musée Ingabo", rw: "Inzu ndangamurage Ingabo" },
        location: "Rebero Hill, Kigali",
        image: "/artefacts/ingabo_hero.jpg",
        logo: "/museums/rcha_logo.png",
        description: {
            en: "Founded by artist King Ngabo, this museum focuses on Rwanda's journey from tragedy to renaissance through symbolic art installations.",
            fr: "Fondé par l'artiste King Ngabo, ce musée se concentre sur le parcours du Rwanda de la tragédie à la renaissance à travers des installations artistiques symboliques.",
            rw: "Iyi nzu ndangamurage yashinzwe n'umuhanzi King Ngabo, igaragaza urugendo r'u Rwanda rwo kuva mu mwijima rwerekeza mu mucyo."
        }
    },
    {
        id: 4,
        name: { en: "Campaign Against Genocide Museum", fr: "Musée de la Campagne contre le Génocide", rw: "Inzu ndangamurage yo guhagarika Jenoside (CAG)" },
        location: "Parliament Building, Kigali",
        image: "/museums/cag_monument.jpg",
        logo: "/museums/rcha_logo.png",
        description: {
            en: "Located in the Parliament Building, it documents the 100-day campaign by the RPA to stop the 1994 Genocide against the Tutsi.",
            fr: "Situé dans le bâtiment du Parlement, il documente la campagne de 100 jours menée par l'APR pour arrêter le génocide de 1994 contre les Tutsi.",
            rw: "Iyi nzu ndangamurage iri mu nyubako y'Inteko Ishinga Amategeko, ivuga amateka y'urugamba rwo guhagarika Jenoside yakorewe Abatutsi muri 1994."
        }
    },
    {
        id: 5,
        name: { en: "Kandt House Museum", fr: "Musée de la Maison Kandt", rw: "Inzu ndangamurage ya Richard Kandt" },
        location: "Nyarugenge, Kigali",
        image: "/museums/kings_palace.jpg",
        logo: "/museums/rcha_logo.png",
        description: {
            en: "The former residence of Richard Kandt, this museum explores the natural history of Rwanda and the evolution of Kigali as a capital city.",
            fr: "Ancienne résidence de Richard Kandt, ce musée explore l'histoire naturelle du Rwanda et l'évolution de Kigali en tant que capitale.",
            rw: "Iyi nzu ndangamurage yahoze ari inzu Richard Kandt yabagamo, igaragaza amateka y'u Rwanda n'uburyo umujyi wa Kigali watangiye."
        }
    },
    {
        id: 6,
        name: { en: "Environment Museum", fr: "Musée de l'Environnement", rw: "Inzu ndangamurage y'Ibidukikije" },
        location: "Karongi, Western Province",
        image: "/museums/ethnographic.jpg",
        logo: "/museums/rcha_logo.png",
        description: {
            en: "The only environment museum in Africa, featuring geological displays and an indigenous herbal garden on its roof.",
            fr: "Le seul musée de l'environnement en Afrique, présentant des expositions géologiques et un jardin d'herbes indigènes sur son toit.",
            rw: "Iyi niyo nzu ndangamurage y'ibidukikije yonyine muri Afurika, igaragaza urusobe rw'ibinyabuzima n'ubuvuzi gakondo."
        }
    },
    {
        id: 7,
        name: { en: "Kigali Genocide Memorial", fr: "Mémorial du Génocide de Kigali", rw: "Urwibutso rwa Jenoside rwa Kigali (Gisozi)" },
        location: "Gisozi, Kigali",
        image: "/museums/cag_monument.jpg",
        logo: "/museums/rcha_logo.png",
        description: {
            en: "A place of remembrance and learning, providing a final resting place for victims and educating about preventing future atrocities.",
            fr: "Un lieu de souvenir et d'apprentissage, offrant un lieu de repos final aux victimes et éduquant sur la prévention de futures atrocités.",
            rw: "Aha ni ahantu ho kwibuka no kwigira ku mateka, kugira ngo Jenoside itazongera kubaho ukundi."
        }
    },
    {
        id: 8,
        name: { en: "Rwanda Art Museum", fr: "Musée d'Art du Rwanda", rw: "Inzu ndangamurage y'Ibikorwa by'Ubugeni n'Ubuhanzi mu Rwanda" },
        location: "Kanombe, Kigali",
        image: "/artefacts/imigongo.jpg",
        logo: "/museums/rcha_logo.png",
        description: {
            en: "Located in the former Presidential Palace, this museum displays contemporary Rwandan art and explores the evolution of artistic expression in the country.",
            fr: "Situé dans l'ancien palais présidentiel, ce musée expose l'art rwandais contemporain et explore l'évolution de l'expression artistique dans le pays.",
            rw: "Iyi nzu ndangamurage iri mu nzu yahoze ari kwa Perezida, igaragaza ubuhanzi bw'umwimerere bw'Abanyarwanda n'uburyo bwagiye bwihinduranya."
        }
    }
];

export default MUSEUMS;
