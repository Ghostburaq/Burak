// Baut die fertige Netlify-Seite nach dist/.
// Die Trainerinhalte (Regeln, Modi, Sprachprofile) kommen direkt aus dem
// Claude-Code-Skill unter .claude/skills/sprachtrainer, damit beide Versionen
// dieselbe Quelle nutzen.
import { build } from "esbuild";
import { cpSync, mkdirSync, readdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { createHash, webcrypto as crypto } from "node:crypto";

rmSync("dist", { recursive: true, force: true });
mkdirSync("dist/icons", { recursive: true });

await build({
  entryPoints: ["src/app.js"],
  bundle: true,
  minify: true,
  format: "esm",
  target: ["es2022", "safari16"],
  loader: { ".md": "text" },
  outfile: "dist/app.js",
  legalComments: "none",
});

for (const f of ["index.html", "style.css", "_headers", "icon.svg", "manifest.webmanifest"]) {
  cpSync(`src/${f}`, `dist/${f}`);
}
for (const f of readdirSync("src/icons").filter((n) => n.endsWith(".png"))) {
  cpSync(`src/icons/${f}`, `dist/icons/${f}`);
}

// Optional: API-Key verschlüsselt einbauen (AES-256-GCM, Schlüssel per PBKDF2 aus dem Passwort).
// Key und Passwort kommen nur aus Umgebungsvariablen. Im Repo und im Klartext steht nichts davon.
const apiKey = process.env.ANTHROPIC_API_KEY?.trim();
if (apiKey) {
  const pass = (process.env.APP_PASSPHRASE || "").toUpperCase().replace(/[^A-Z0-9]/g, ""); // wie normalize() in src/crypto.js
  if (pass.length < 16) {
    throw new Error("APP_PASSPHRASE fehlt oder ist zu kurz (mindestens 16 Zeichen A-Z/0-9, z.B. XXXX-XXXX-XXXX-XXXX-XXXX).");
  }
  const ITER = 600000;
  const b64 = (u8) => Buffer.from(u8).toString("base64");
  const salt = crypto.getRandomValues(new Uint8Array(16));
  const iv = crypto.getRandomValues(new Uint8Array(12));
  const base = await crypto.subtle.importKey("raw", new TextEncoder().encode(pass), "PBKDF2", false, ["deriveKey"]);
  const key = await crypto.subtle.deriveKey({ name: "PBKDF2", salt, iterations: ITER, hash: "SHA-256" }, base, { name: "AES-GCM", length: 256 }, false, ["encrypt"]);
  const ct = new Uint8Array(await crypto.subtle.encrypt({ name: "AES-GCM", iv }, key, new TextEncoder().encode(apiKey)));
  writeFileSync("dist/keyblob.json", JSON.stringify({ v: 1, alg: "AES-GCM/PBKDF2-SHA256", iter: ITER, salt: b64(salt), iv: b64(iv), ct: b64(ct) }));
  console.log("API-Key verschlüsselt eingebaut (dist/keyblob.json)");
} else {
  console.log("Kein ANTHROPIC_API_KEY gesetzt: App fragt nach dem Key.");
}

// Service Worker mit Versionsstempel aus dem Inhalt: neue Version = neuer Cache.
const shell = ["app.js", "index.html", "style.css", "icon.svg", "manifest.webmanifest", ...readdirSync("dist/icons").map((n) => `icons/${n}`)].sort();
const hash = createHash("sha256");
for (const f of shell) hash.update(readFileSync(`dist/${f}`));
const version = `sprachtrainer-${hash.digest("hex").slice(0, 12)}`;
const files = ["./", ...shell];
writeFileSync(
  "dist/sw.js",
  readFileSync("src/sw.js", "utf8").replace("__VERSION__", version).replace("__FILES__", JSON.stringify(files)),
);
console.log(`dist/ gebaut, Version ${version}`);
