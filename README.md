# taliafiege.com — One-Pager (Apple-style slide deck)

Single-page site for **Talia Fiege — IFBB Pro Athlete, Online Fitness Coach & Entrepreneur**, built as ten full-screen slides that snap into place like a keynote.

One self-contained file: `index.html` (HTML + CSS + vanilla JS). No build step, no framework.
Deploy by uploading `index.html` to any static host (Netlify, Vercel, Cloudflare Pages, or as a custom-code page in Wix).

## The slides

| # | Slide | Content |
|---|---|---|
| 1 | Home | Name, IFBB Pro badge, two CTAs, portrait with layered 3D shadow |
| 2 | Credentials | IFBB Pro · Certified Trainer · Co-Owner MomBodz |
| 3 | About | The story, with portrait |
| 4 | Coaching | Three pricing cards, 3D tilt on hover |
| 5 | Programs | The three Wix challenge pages |
| 6 | Results | Testimonials + transformation placeholders |
| 7 | Gallery | Full-bleed horizontal photo strip |
| 8 | Essentials | Six affiliate brands + FTC disclosure + Etsy |
| 9 | Free Guide | Email capture |
| 10 | Contact | Email, socials, contact form, footer |

**Navigation:** click the dots on the right, use the nav links, or press `↑` `↓` `PageUp` `PageDown` `Home` `End`. A progress bar tracks position.

## Design

Apple's light palette: `#FFFFFF` and `#F5F5F7` alternating, text `#1D1D1F`, secondary `#6E6E73`, accent blue `#0071E3`. Depth comes from four-layer box-shadows rather than borders, plus a subtle 3D tilt on the hero portrait and the coaching cards.

Snapping is `mandatory` only from 1000×860 px upward, where every slide provably fits the viewport; below that it drops to `proximity` so nothing can be scrolled past or trapped. Motion and snapping switch off entirely for `prefers-reduced-motion`.

## Before going live — fill these in

| Placeholder | Where | What to do |
|---|---|---|
| `PRICE_PLAN` | Coaching → Custom Training Plan | Replace the visible `$—` with the real one-time price |
| `PRICE_COACHING` | Coaching → 1:1 Online Coaching | Replace `$—/mo` with the real monthly price |
| `PRICE_PREP` | Coaching → Contest Prep | Replace `$—/mo` with the real monthly price |
| `CODE` ×6 | Essentials | Swap `[CODE]` for each brand's discount code |
| Affiliate links ×6 | Essentials | Replace `href="#"` with the real affiliate URLs |
| `YOUTUBE_CHANNEL_URL` | Contact → socials | Set the real channel URL, then delete `aria-disabled="true"`, the `data-placeholder` attribute and the "(link coming)" text |

Search the file for `data-placeholder` to jump to every spot.

## Not connected yet

- **Email capture** (`#optinForm`) — front-end only. Set `action`/`method` to your Kit, Mailchimp or Klaviyo endpoint and remove the JS demo handler.
- **Contact form** (`#contactForm`) — front-end only. Point it at Formspree, Basin or Wix Forms.
- **Transformation photos** (Results slide) — three placeholder frames. Swap-in markup is in an HTML comment right above them. Only publish client photos with written permission.

## Notes

- Photos are hotlinked from the existing Wix CDN. For best performance, re-host them and serve WebP/AVIF.
- No third-party brand logos are used on purpose (trademark and hotlinking risk) — brand names are set in type.
- The FTC affiliate disclosure on the Essentials slide is required. Do not remove it.
- Adding content to a slide can push it past the viewport. After editing, re-check that each slide still fits at 1000×860, or it will overflow inside the mandatory-snap range.
