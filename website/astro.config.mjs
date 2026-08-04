import { defineConfig } from 'astro/config';
import tailwind from '@astrojs/tailwind';
import sitemap from '@astrojs/sitemap';

// TODO: Domain festlegen und hier eintragen. Muss mit `domain` in
// src/lib/site.ts uebereinstimmen (steuert Canonical-URLs, Sitemap, og:image).
const SITE_URL = 'https://engineering-kabuu.example';

export default defineConfig({
  site: SITE_URL,
  trailingSlash: 'never',
  integrations: [
    tailwind({ applyBaseStyles: false }),
    sitemap(),
  ],
  build: {
    inlineStylesheets: 'auto',
  },
});
