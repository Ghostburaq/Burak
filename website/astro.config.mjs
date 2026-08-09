import { defineConfig } from 'astro/config';
import tailwind from '@astrojs/tailwind';
import sitemap from '@astrojs/sitemap';

// Site-URL kommt beim Netlify-Build automatisch aus der Umgebung.
//   URL              -> primaere Adresse der Site (eigene Domain, sobald verbunden)
//   DEPLOY_PRIME_URL -> Adresse dieses Deploys (Deploy Previews, Branch-Deploys)
// Lokal wird auf localhost zurueckgefallen. Es muss also nichts von Hand
// eingetragen werden: Canonical-Links, Sitemap und og:image stimmen nach dem
// Verbinden der eigenen Domain automatisch.
const SITE_URL =
  process.env.URL ||
  process.env.DEPLOY_PRIME_URL ||
  'http://localhost:4321';

export default defineConfig({
  site: SITE_URL,
  trailingSlash: 'never',
  integrations: [
    tailwind({ applyBaseStyles: false }),
    // Die Danke-Seite traegt noindex und ist in robots.txt gesperrt, also
    // gehoert sie auch nicht in die Sitemap.
    sitemap({ filter: (page) => !page.includes('/danke') }),
  ],
  build: {
    inlineStylesheets: 'auto',
  },
});
