// Zentrale Site-Konstanten. TODOs siehe OFFENE_PUNKTE.md.
export const site = {
  // TODO: Firmenname im Fakten-Block bestaetigen.
  brand: 'Kabuu Engineering',
  owner: 'Burak Uecoez',
  // TODO: Ladungsfaehige Anschrift in Deutschland ergaenzen.
  address: {
    street: 'TODO: Strasse und Hausnummer',
    zip: 'TODO: PLZ',
    city: 'TODO: Ort',
    country: 'Deutschland',
  },
  contact: {
    // TODO: Geschaeftliche E-Mail im Fakten-Block bestaetigen.
    email: 'TODO@example.com',
    // TODO: Telefonnummer eintragen.
    phone: '+49 TODO',
  },
  // TODO: Domain nach Registrierung in astro.config.mjs und hier setzen.
  domain: 'kabuu-engineering.example',
  claim: 'Netzqualitaet und EMV messen, bevor investiert wird.',
  // Formular-Endpoint zentral austauschbar. Wahl siehe OFFENE_PUNKTE.md.
  contactEndpoint: import.meta.env.PUBLIC_CONTACT_ENDPOINT ?? '',
};

export const nav = [
  { href: '/', label: 'Start' },
  { href: '/leistungen', label: 'Leistungen' },
  { href: '/ablauf', label: 'Ablauf' },
  { href: '/ueber', label: 'Ueber mich' },
  { href: '/kontakt', label: 'Kontakt' },
];

export const legalNav = [
  { href: '/impressum', label: 'Impressum' },
  { href: '/datenschutz', label: 'Datenschutz' },
  { href: '/agb', label: 'AGB' },
];
