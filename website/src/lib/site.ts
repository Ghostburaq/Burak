// Zentrale Site-Konstanten. Fakten stammen aus BRIEF.md Abschnitt 1 und sind bestätigt.
// Offene Punkte in OFFENE_PUNKTE.md.

export const site = {
  brand: 'Engineering.Kabuu',
  owner: 'Burak Ücöz',
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
  // Die Site-URL wird nicht hier gepflegt. Sie kommt beim Netlify-Build aus der
  // Umgebungsvariable URL, siehe astro.config.mjs. In Komponenten ueber Astro.site
  // verfuegbar. Nach dem Verbinden der eigenen Domain stimmt sie automatisch.
  claim: 'Netzqualität und EMV messen, bevor investiert wird.',
};

export const nav = [
  { href: '/', label: 'Start' },
  { href: '/leistungen', label: 'Leistungen' },
  { href: '/ablauf', label: 'Ablauf' },
  { href: '/faq', label: 'Häufige Fragen' },
  { href: '/ueber', label: 'Über mich' },
  { href: '/kontakt', label: 'Kontakt' },
];

export const legalNav = [
  { href: '/impressum', label: 'Kontakt / Impressum' },
  { href: '/datenschutz', label: 'Datenschutz' },
  { href: '/agb', label: 'AGB' },
];
