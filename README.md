# taliafiege.com — One-Pager (Apple-style slide deck)

Single-page site for **Talia Fiege — IFBB Pro Athlete, Online Fitness Coach & Entrepreneur**, built as ten full-screen slides that snap into place like a keynote.

One self-contained file: `index.html` (HTML + CSS + vanilla JS). No build step, no framework. It runs both as a standalone site and inside a Wix embed — see **[DEPLOY.md](DEPLOY.md)**.

## The slides

| # | Slide | Content |
|---|---|---|
| 1 | Home | Name, IFBB Pro badge, two CTAs, portrait with aura, floating glass chips and parallax |
| 2 | Credentials | IFBB Pro · Certified Trainer · First Show, First Place |
| 3 | About | The story, with portrait |
| 4 | Coaching | Three pricing cards, 3D tilt on hover |
| 5 | Programs | The three Wix challenge pages |
| 6 | Results | Testimonials + transformation placeholders |
| 7 | Gallery | Full-bleed 3D coverflow strip, click to open the lightbox |
| 8 | Essentials | Six affiliate brands with copy-code buttons + FTC disclosure + Etsy |
| 9 | Free Guide | Email capture |
| 10 | Apply | Coaching application, email, socials, Linktree links, footer |

**Navigation:** click the dots on the right, use the nav links, or press `↑` `↓` `PageUp` `PageDown` `Home` `End`. A progress bar tracks position.

## Design

Apple's light palette: `#FFFFFF` and `#F5F5F7` alternating, text `#1D1D1F`, secondary `#6E6E73`, accent blue `#0071E3`.

Depth is a system, not a set of one-off shadows:

- **Elevation scale** (`--e1` … `--e4`) — each level stacks a contact shadow, a key shadow and two ambient layers, plus an inset top bevel. Cards use `--e2` and rise to `--e3` on hover; the hero portrait sits at `--e4`.
- **Ambient colour fields** — every slide carries two large blurred radial gradients (blue / warm, alternating direction per slide) so the white never reads as flat paper.
- **3D reveals** — elements rotate up out of the page (`rotate: x 9deg → 0`) as they enter. These use the independent `translate` / `rotate` / `scale` properties, so they compose with the pointer tilt, which owns `transform`.
- **Pointer-tracked light** — any `.sheen` surface gets a soft specular that follows the cursor via `--mx` / `--my`.
- **3D tilt** — coaching cards tilt up to 7° through `--rx` / `--ry`.
- **Hero parallax** — portrait, aura and the two glass credential chips move at different depths from a single pointer handler on `#heroStage`.
- **Coverflow gallery** — photos rotate on the Y axis and recede in Z based on their distance from the strip's centre, driven by the scroll position.
- **Floating capsule nav** — from 940 px the nav becomes a rounded glass capsule with its own shadow; below that it is a plain bar.
- **Gallery lightbox** — clicking a photo opens a native `<dialog>` with a blurred backdrop, arrow-key navigation, a counter and focus return. `showModal()` does not stop the page behind it from scrolling, so the page is explicitly locked and its position restored on close.

Snapping is `mandatory` only from 1000×880 px upward, where every slide provably fits the viewport; below that it drops to `proximity` so nothing can be scrolled past or trapped. Motion, snapping and the pointer effects switch off for `prefers-reduced-motion`, and the tilt/parallax also stay off on touch devices.

### Gotcha for future edits

`.pillar p`, `.program p` and `.about p` style body copy inside those blocks. An element selector like that beats a bare modifier class (`.pillar__num`), so new modifier classes in those blocks need the extra specificity — for example `.pillar .pillar__num`, which is how the big gradient numerals are kept at their real size.

## Before going live — fill these in

### 1. The config block

Near the top of `index.html`, right after the font `<link>`, is a `window.SITE` block. Photos, links, discount codes and the booking behaviour all live there — you should not need to touch the markup for any of it:

| Key | What it does |
|---|---|
| `wixBase` | Where the Wix site lives. Set it to e.g. `"https://programs.taliafiege.com"` and the challenge links on slide 5 follow. Empty keeps the URLs as written. |
| `booking.mode` | `"application"` (default) points every CTA at the form on the last slide. `"calendar"` points them at `booking.calendarUrl` instead and relabels the buttons. |
| `youtube` | Channel URL. Empty leaves the YouTube chip disabled. |
| `links` | `{ label, url }` entries from your Linktree. They render as pills under the socials; an empty list hides that whole block. |
| `images.hero` / `images.about` | New portraits for slides 1 and 3. Empty keeps the current photo. |
| `images.gallery` | Replaces the whole gallery strip. Accepts `"url"` or `{ src, alt, wide }`. `wide: true` makes a landscape frame. |
| `essentials` | The six existing affiliate partners, each `{ url, code }`. |
| `extraPartners` | `{ name, category, url, code }` for new deals. Each becomes another card; the grid switches to four columns past six cards. |

Anything left empty stays in a clean "coming soon" state — a card shows no code and its Shop link is disabled and cannot be clicked, so the page never ships a dead link or an invented code. Fill a value in and that card switches itself on: the code appears as a pill with a copy-to-clipboard button, and the Shop link opens in a new tab with `rel="sponsored noopener"`.

A partner with a code but no URL (or the reverse) is fine — each half works on its own.

### 2. Prices — still in the markup

| Placeholder | Where | What to do |
|---|---|---|
| `PRICE_PLAN` | Coaching → Custom Training Plan | Replace the visible `$—` with the real one-time price |
| `PRICE_COACHING` | Coaching → 1:1 Online Coaching | Replace `$—/mo` with the real monthly price |
| `PRICE_PREP` | Coaching → Contest Prep | Replace `$—/mo` with the real monthly price |

Search the file for `data-placeholder` to jump to all three.

## Hosting

Wix cannot serve a hand-written `index.html` as a page, so there are two routes — and **this file is ready for both without being edited**. It checks at load whether it is inside an iframe and adapts: snapping off, side dots hidden, scroll chaining contained.

- **Route A** — host it yourself, point `taliafiege.com` at it, move the Wix site to a subdomain. The page works exactly as built and its text is indexable.
- **Route B** — embed it in Wix. Ships today, costs you SEO on that content.

Step-by-step for both, plus what Route B actually costs, is in **[DEPLOY.md](DEPLOY.md)**.

Set `wixBase` in the config block if the Wix site moves to a subdomain — the three challenge links follow it automatically.

## Not connected yet

- **Email capture** (`#optinForm`) — front-end only. Set `action`/`method` to your Kit, Mailchimp or Klaviyo endpoint and remove the JS demo handler.
- **Coaching application** (`#applyForm`) — front-end only. Point it at Formspree, Basin or Wix Forms. It collects name, email, goal, experience, training availability and notes.
- **Transformation photos** (Results slide) — three placeholder frames. Swap-in markup is in an HTML comment right above them. Only publish client photos with written permission.

## Notes

- Photos are hotlinked from the existing Wix CDN. For best performance, re-host them and serve WebP/AVIF.
- No third-party brand logos are used on purpose (trademark and hotlinking risk) — brand names are set in type.
- The FTC affiliate disclosure on the Essentials slide is required. Do not remove it.
- Adding content to a slide can push it past the viewport. After editing, re-check that each slide still fits at 1000×880, or it will overflow inside the mandatory-snap range.
