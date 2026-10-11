// Baut die statische Netlify-Seite nach dist/.
// Die Trainerinhalte (Regeln, Modi, Sprachprofile) kommen direkt aus dem
// Claude-Code-Skill unter .claude/skills/sprachtrainer, damit beide Versionen
// dieselbe Quelle nutzen.
import { build } from "esbuild";
import { cpSync, mkdirSync, rmSync } from "node:fs";

rmSync("dist", { recursive: true, force: true });
mkdirSync("dist");

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

for (const f of ["index.html", "style.css", "_headers", "icon.svg"]) {
  cpSync(`src/${f}`, `dist/${f}`);
}
console.log("dist/ gebaut");
