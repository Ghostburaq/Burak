// Baut die fertige Netlify-Seite nach dist/.
// Die Trainerinhalte (Regeln, Modi, Sprachprofile) kommen direkt aus dem
// Claude-Code-Skill unter .claude/skills/sprachtrainer, damit beide Versionen
// dieselbe Quelle nutzen.
import { build } from "esbuild";
import { cpSync, mkdirSync, readdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { createHash } from "node:crypto";

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
