import type React from "react";
import { Interactive, useCurrentFrame } from "remotion";
import { colors } from "../theme";

type WaveformProps = {
  readonly color: string;
  // Anteil der 5. und 7. Oberschwingung (0 = sauberer Sinus)
  readonly harmonics: number;
  // Restspannung während des Einbruchs (1 = kein Einbruch)
  readonly dipDepth: number;
  // Lage des Einbruchs in Perioden auf der laufenden Zeitachse
  readonly dipStart: number;
  readonly dipLength: number;
  readonly cyclesPerFrame: number;
  readonly style?: React.CSSProperties;
};

const W = 920;
const H = 440;
const CYCLES = 4;
const SAMPLES = 360;

const WaveformInner = ({
  color,
  harmonics,
  dipDepth,
  dipStart,
  dipLength,
  cyclesPerFrame,
  style,
}: WaveformProps) => {
  const frame = useCurrentFrame();
  const amp = H * 0.36;

  let d = "";
  for (let i = 0; i <= SAMPLES; i++) {
    const x = (i / SAMPLES) * W;
    const c = (i / SAMPLES) * CYCLES + frame * cyclesPerFrame;
    const p = 2 * Math.PI * c;
    const inDip = c >= dipStart && c <= dipStart + dipLength;
    const v =
      (Math.sin(p) +
        harmonics * 0.55 * Math.sin(5 * p + 0.6) +
        harmonics * 0.35 * Math.sin(7 * p + 1.1)) *
      (inDip ? dipDepth : 1);
    d += `${i === 0 ? "M" : "L"}${x.toFixed(1)},${(H / 2 - v * amp).toFixed(1)} `;
  }

  return (
    <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`} style={style}>
      <line x1={0} y1={H / 2} x2={W} y2={H / 2} stroke={colors.grid} strokeWidth={3} />
      <line x1={0} y1={H / 2 - amp} x2={W} y2={H / 2 - amp} stroke={colors.grid} strokeWidth={2} strokeDasharray="10 12" />
      <line x1={0} y1={H / 2 + amp} x2={W} y2={H / 2 + amp} stroke={colors.grid} strokeWidth={2} strokeDasharray="10 12" />
      <path d={d} fill="none" stroke={color} strokeWidth={8} strokeLinejoin="round" strokeLinecap="round" />
    </svg>
  );
};

export const Waveform = Interactive.create({
  Component: WaveformInner,
  layout: "none",
  schema: {
    color: { type: "color", default: colors.accent, description: "Farbe" },
    harmonics: { type: "number", hiddenFromList: false, default: 0, min: 0, max: 1, step: 0.05, description: "Oberschwingungen" },
    dipDepth: { type: "number", hiddenFromList: false, default: 1, min: 0, max: 1, step: 0.05, description: "Restspannung im Einbruch" },
    dipStart: { type: "number", hiddenFromList: false, default: 100, step: 0.5, description: "Start Einbruch (Perioden)" },
    dipLength: { type: "number", hiddenFromList: false, default: 5, step: 0.5, description: "Dauer Einbruch (Perioden)" },
    cyclesPerFrame: { type: "number", hiddenFromList: false, default: 0.04, step: 0.005, description: "Laufgeschwindigkeit" },
  },
});
