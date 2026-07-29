// Zentrale Site-Konstanten. Fakten stammen aus BRIEF.md Abschnitt 1 und sind bestaetigt.
// Offene Punkte in OFFENE_PUNKTE.md.

export const site = {
  brand: 'Engineering.Kabuu',
  owner: 'Burak Uecoez',
  rechtsform: 'Einzelunternehmen',
  address: {
    street: 'Im Abt 9 A',
    zip: '8240',
    city: 'Thayngen',
    country: 'Schweiz',
  },
  contact: {
    email: 'engineering.kabuu@gmail.com',
    phoneDisplay: '079 512 98 07',
    phoneLink: '+41795129807',
  },
  // TODO: Domain festlegen. Bis dahin steht die Netlify-Subdomain als Fallback in astro.config.mjs.
  domain: 'engineering-kabuu.example',
  claim: 'Netzqualitaet und EMV messen, bevor investiert wird.',
};

export const nav = [
  { href: '/', label: 'Start' },
  { href: '/leistungen', label: 'Leistungen' },
  { href: '/ablauf', label: 'Ablauf' },
  { href: '/ueber', label: 'Ueber mich' },
  { href: '/kontakt', label: 'Kontakt' },
];

export const legalNav = [
  { href: '/impressum', label: 'Kontakt / Impressum' },
  { href: '/datenschutz', label: 'Datenschutz' },
  { href: '/agb', label: 'AGB' },
];
