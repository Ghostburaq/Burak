import { Easing, Interactive, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { Headline } from "../elements/Headline";
import { colors, monoFont } from "../theme";

const MeasureSceneInner = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  return (
    <>
      <Headline name="Titel" style={{ position: "absolute", left: 80, right: 160, top: 380, fontSize: 120 }}>
        Messen statt raten.
      </Headline>
      <Headline
        name="Punkt 1"
        style={{
          position: "absolute",
          left: 80,
          right: 160,
          top: 700,
          fontSize: 60,
          fontWeight: 500,
          borderLeft: `10px solid ${colors.accent}`,
          paddingLeft: 36,
          opacity: interpolate(frame, [0.6 * fps, 0.9 * fps], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          }),
          translate: interpolate(frame, [0.6 * fps, 1 * fps], ["40px 0px", "0px 0px"], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
            easing: Easing.bezier(0.16, 1, 0.3, 1),
          }),
        }}
      >
        Messgerät Klasse A nach IEC 61000-4-30
      </Headline>
      <Headline
        name="Punkt 2"
        style={{
          position: "absolute",
          left: 80,
          right: 160,
          top: 940,
          fontSize: 60,
          fontWeight: 500,
          borderLeft: `10px solid ${colors.accent}`,
          paddingLeft: 36,
          opacity: interpolate(frame, [1.6 * fps, 1.9 * fps], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          }),
          translate: interpolate(frame, [1.6 * fps, 2 * fps], ["40px 0px", "0px 0px"], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
            easing: Easing.bezier(0.16, 1, 0.3, 1),
          }),
        }}
      >
        Mindestens eine Woche am Stück
      </Headline>
      <Headline
        name="Punkt 3"
        style={{
          position: "absolute",
          left: 80,
          right: 160,
          top: 1180,
          fontSize: 60,
          fontWeight: 500,
          borderLeft: `10px solid ${colors.accent}`,
          paddingLeft: 36,
          opacity: interpolate(frame, [2.6 * fps, 2.9 * fps], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          }),
          translate: interpolate(frame, [2.6 * fps, 3 * fps], ["40px 0px", "0px 0px"], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
            easing: Easing.bezier(0.16, 1, 0.3, 1),
          }),
        }}
      >
        Ereignis-Zeitstempel neben das Störungsprotokoll legen
      </Headline>
      <div
        style={{
          position: "absolute",
          left: 80,
          right: 160,
          top: 1500,
          fontFamily: monoFont,
          fontSize: 48,
          color: colors.muted,
          opacity: interpolate(frame, [3.6 * fps, 4 * fps], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          }),
        }}
      >
        Dann weisst du, ob es das Netz war. Oder deine Anlage.
      </div>
    </>
  );
};

export const MeasureScene = Interactive.create({
  Component: MeasureSceneInner,
  layout: "absolute-fill",
  schema: { ...Interactive.backgroundSchema },
});
