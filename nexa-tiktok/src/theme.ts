import { loadFont } from "@remotion/fonts";
import { staticFile } from "remotion";

export const headFont = "Space Grotesk";
export const monoFont = "JetBrains Mono";

for (const weight of ["500", "700"]) {
  loadFont({
    family: headFont,
    url: staticFile(`fonts/space-grotesk-latin-${weight}-normal.woff2`),
    weight,
  });
  loadFont({
    family: monoFont,
    url: staticFile(`fonts/jetbrains-mono-latin-${weight}-normal.woff2`),
    weight,
  });
}

export const colors = {
  bg: "#0A0E14",
  fg: "#F2F5F8",
  muted: "#8A96A3",
  accent: "#2EE6D6",
  warn: "#FFB020",
  alert: "#FF4D4D",
  grid: "#1C2530",
};
