# Deploying taliafiege.com

`index.html` works in **both** setups without editing the file. It detects at load whether it is running inside a page builder's iframe and adapts.

Pick a route below. Route A is the recommended one; Route B exists so you can ship inside Wix today and move later without a rebuild.

---

## Route A — host the one-pager, keep Wix for the programs

The page runs exactly as designed: full-screen slides, snapping, side dots, and text Google can index on the domain itself.

### 1. Put the file online

Any static host works and all of these are free at this size.

- **Netlify Drop** — go to <https://app.netlify.com/drop> and drag the folder containing `index.html` onto the page. You get a live URL in seconds.
- **Cloudflare Pages** — Create a project → Direct Upload → upload the folder.
- **Vercel** — Add New → Project → deploy the folder.

Nothing to build or configure. The file has no dependencies beyond Google Fonts and the photo URLs.

### 2. Decide what happens to the Wix site

The three challenge pages on slide 5 and the booking calendar live on Wix. They have to stay reachable, so Wix keeps a home:

| | Root domain `taliafiege.com` | Wix site |
|---|---|---|
| **Recommended** | the new one-pager | `programs.taliafiege.com` |
| Alternative | the new one-pager | keep an unused Wix URL, link out to it |

In Wix: **Settings → Domains → Connect a domain** → assign `programs.taliafiege.com` to the Wix site. Then point the root domain at your static host by following that host's DNS instructions.

### 3. Follow the moved Wix site

One line in the config block at the top of `index.html`:

```js
wixBase: "https://programs.taliafiege.com",
```

All three challenge links and the booking calendar URL move with it automatically. Leave it as `""` if Wix stays on `www.taliafiege.com`.

### 4. Check afterwards

- The three challenge links open the right programs.
- `taliafiege.com` serves the one-pager over HTTPS.
- Old Wix URLs that people have bookmarked still resolve (Wix keeps serving them on the subdomain).

---

## Route B — embed it in Wix

Use this if the domain has to stay on Wix for now.

### 1. Host the file anyway

Do step 1 of Route A. Wix's embed element accepts a URL, and that is far more reliable than pasting 70 KB of code into the editor's code box.

### 2. Add it to the page

Wix Editor → **Add (+) → Embed Code → Embed a Site** → paste your hosted URL.

Then:

- Stretch the element to **full width**.
- Set the height to **700–900 px**. Inside the iframe the page switches to continuous scrolling, so nothing is cut off — a taller frame simply shows more at once.
- Remove the Wix header/footer around it if you want the embed to read as the page.

If you prefer to paste code instead of a URL, use **Embed Code → Custom Embed → Code** and paste:

```html
<iframe src="https://YOUR-HOST/index.html"
        title="Talia Fiege — IFBB Pro Athlete & Online Fitness Coach"
        style="width:100%;height:820px;border:0"
        loading="lazy"></iframe>
```

### 3. What changes inside the iframe

The page notices it is embedded and adjusts itself:

| | Standalone | Embedded |
|---|---|---|
| Scroll snapping | on (mandatory from 1000×880) | off — a snapping scroller nested in another page fights the host |
| Side dot navigation | shown | hidden |
| Scroll chaining | n/a | contained, so reaching the end does not start scrolling the Wix page |
| Vertical padding | full | tightened |

Everything else — the nav, the 3D effects, the coverflow gallery, the lightbox, both forms — works the same.

### 4. What you lose, honestly

- **SEO.** Google indexes iframe content separately from the page that contains it. The headlines, the story and the coaching copy will not count toward `taliafiege.com` ranking for those terms. Keep real Wix text on the page — at minimum an H1 and a short intro — or the site loses ground it currently has.
- **Links to sections.** Nothing outside the iframe can link to a slide, and the browser URL never changes as you scroll.
- **Nested scrolling.** On phones, a scrolling box inside a scrolling page is never as clean as a normal page.

None of this is fatal for a launch, and moving to Route A later needs no code changes — only the DNS switch and the `wixBase` line.

---

## Before either route goes live

See `README.md` → *Before going live*. In short: the config block still needs the affiliate links, the discount codes and the YouTube URL, and the three prices are still `$—` in the markup. Everything unfilled renders as a visibly disabled "coming soon" state rather than a dead link, so a partial launch is safe.
