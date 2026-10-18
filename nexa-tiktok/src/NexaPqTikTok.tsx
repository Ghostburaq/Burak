import { Track, useVideoConfig } from "remotion";
import { DipScene } from "./scenes/DipScene";
import { HarmonicsScene } from "./scenes/HarmonicsScene";
import { HookScene } from "./scenes/HookScene";
import { MeasureScene } from "./scenes/MeasureScene";
import { MultimeterScene } from "./scenes/MultimeterScene";
import { OutroScene } from "./scenes/OutroScene";
import { colors } from "./theme";

export const NexaPqTikTok = () => {
  const { fps } = useVideoConfig();

  return (
    <Track name="Szenen">
      <HookScene name="Hook" durationInFrames={3.5 * fps} style={{ backgroundColor: colors.bg }} />
      <MultimeterScene
        name="Multimeter"
        from={3.5 * fps}
        durationInFrames={5.5 * fps}
        style={{ backgroundColor: colors.bg }}
      />
      <HarmonicsScene
        name="Oberschwingungen"
        from={9 * fps}
        durationInFrames={7 * fps}
        style={{ backgroundColor: colors.bg }}
      />
      <DipScene name="Einbruch" from={16 * fps} durationInFrames={7 * fps} style={{ backgroundColor: colors.bg }} />
      <MeasureScene name="Messen" from={23 * fps} durationInFrames={6 * fps} style={{ backgroundColor: colors.bg }} />
      <OutroScene name="Outro" from={29 * fps} durationInFrames={4 * fps} style={{ backgroundColor: colors.bg }} />
    </Track>
  );
};
