# taliafiege.com — One-Pager

Premium single-page site for **Talia Fiege — IFBB Pro Athlete, Online Fitness Coach & Entrepreneur**.

One self-contained file: `index.html` (HTML + CSS + vanilla JS). No build step, no framework.
Deploy by uploading `index.html` to any static host (Netlify, Vercel, Cloudflare Pages, or as a custom-code page in Wix).

## Before going live — fill these in

| Placeholder | Where | What to do |
|---|---|---|
| `PRICE_PLAN` | Coaching → Custom Training Plan | Replace the visible `$—` with the real one-time price |
| `PRICE_COACHING` | Coaching → 1:1 Online Coaching | Replace `$—/mo` with the real monthly price |
| `PRICE_PREP` | Coaching → Contest Prep | Replace `$—/mo` with the real monthly price |
| `CODE` ×6 | My Essentials | Swap `[CODE]` for each brand's discount code |
| Affiliate links ×6 | My Essentials | Replace `href="#"` with the real affiliate URLs |
| `YOUTUBE_CHANNEL_URL` | Contact → socials | Set the real channel URL, then delete `aria-disabled="true"`, the `data-placeholder` attribute and the "(link coming)" text |

Search the file for `data-placeholder` to jump to every spot.

## Not connected yet

- **Email capture** (`#optinForm`) — front-end only. Set `action`/`method` to your Kit, Mailchimp or Klaviyo endpoint and remove the JS demo handler.
- **Contact form** (`#contactForm`) — front-end only. Point it at Formspree, Basin or Wix Forms.
- **Transformation photos** (Results section) — three placeholder frames. Swap-in markup is in an HTML comment right above them. Only publish client photos with written permission.

## Notes

- Photos are hotlinked from the existing Wix CDN. For best performance, re-host them and serve WebP/AVIF.
- No third-party brand logos are used on purpose (trademark and hotlinking risk) — brand names are set in type.
- The FTC affiliate disclosure under "My Essentials" is required. Do not remove it.
- Motion (parallax, 3D card tilt, scroll reveals) is disabled automatically for `prefers-reduced-motion` and on touch devices.
