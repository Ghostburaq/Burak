import type { APIRoute } from 'astro';

// robots.txt wird beim Build erzeugt, damit die Sitemap-Adresse immer auf die
// tatsaechliche Site-URL zeigt (siehe astro.config.mjs).
export const GET: APIRoute = ({ site }) => {
  const base = site?.toString().replace(/\/$/, '') ?? '';
  const body = [
    'User-agent: *',
    'Allow: /',
    '',
    '# Die Danke-Seite ist kein Suchergebnis.',
    'Disallow: /danke',
    '',
    `Sitemap: ${base}/sitemap-index.xml`,
    '',
  ].join('\n');

  return new Response(body, {
    headers: { 'Content-Type': 'text/plain; charset=utf-8' },
  });
};
