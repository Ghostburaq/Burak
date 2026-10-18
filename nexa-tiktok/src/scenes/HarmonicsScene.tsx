import { Interactive, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { Headline } from "../elements/Headline";
import { Waveform } from "../elements/Waveform";
import { colors, monoFont } from "../theme";

const HarmonicsSceneInner = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const thd = interpolate(frame, [0.5 * fps, 3 * fps], [0, 8], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <>
      <Headline
        name="Titel"
        style={{ position: "absolute", left: 80, right: 160, top: 240, fontSize: 104, color: colors.warn }}
      >
        Oberschwingungen
      </Headline>
      <Headline
        name="Quellen"
        style={{
          position: "absolute",
          left: 80,
          right: 160,
          top: 380,
          fontSize: 54,
          fontWeight: 500,
          color: colors.muted,
        }}
      >
        Umrichter, LED-Treiber, Netzteile
      </Headline>
      <Waveform
        name="Kurve wird verzerrt"
        color={colors.warn}
        harmonics={interpolate(frame, [0.5 * fps, 3 * fps], [0, 0.5], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
        })}
        dipDepth={1}
        dipStart={100}
        dipLength={5}
        cyclesPerFrame={0.04}
        style={{ position: "absolute", left: 80, top: 560 }}
      />
      <div
        style={{
          position: "absolute",
          left: 80,
          top: 1050,
          fontFamily: monoFont,
          fontWeight: 700,
          fontSize: 150,
          color: colors.fg,
        }}
      >
        THD {thd.toFixed(1).replace(".", ",")} %
      </div>
      <Headline
        name="Grenzwert"
        style={{
          position: "absolute",
          left: 80,
          right: 160,
          top: 1260,
          fontSize: 60,
          fontWeight: 500,
          opacity: interpolate(frame, [3.2 * fps, 3.6 * fps], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          }),
        }}
      >
        EN 50160 erlaubt bis 8 %. Gemessen über eine Woche, 95 % der 10-Minuten-Werte.
      </Headline>
      <Headline
        name="Folgen"
        style={{
          position: "absolute",
          left: 80,
          right: 160,
          top: 1530,
          fontSize: 54,
          fontWeight: 500,
          color: colors.alert,
          opacity: interpolate(frame, [4.6 * fps, 5 * fps], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          }),
        }}
      >
        Folgen: heisse Neutralleiter, gestresste Kondensatoren, Fehlauslösungen.
      </Headline>
    </>
  );
};

export const HarmonicsScene = Interactive.create({
  Component: HarmonicsSceneInner,
  layout: "absolute-fill",
  schema: { ...Interactive.backgroundSchema },
});
