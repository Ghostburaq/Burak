import { defineConfig } from 'astro/config';
import tailwind from '@astrojs/tailwind';
import sitemap from '@astrojs/sitemap';

// TODO: Domain im Fakten-Block ergaenzen und hier eintragen.
const SITE_URL = 'https://kabuu-engineering.example';

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
