import { Composition, Folder } from "remotion";
import { NexaPqTikTok } from "./NexaPqTikTok";
import { DipScene } from "./scenes/DipScene";
import { HarmonicsScene } from "./scenes/HarmonicsScene";
import { HookScene } from "./scenes/HookScene";
import { MeasureScene } from "./scenes/MeasureScene";
import { MultimeterScene } from "./scenes/MultimeterScene";
import { OutroScene } from "./scenes/OutroScene";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="NexaPqTikTok"
        component={NexaPqTikTok}
        durationInFrames={990}
        fps={30}
        width={1080}
        height={1920}
      />
      <Folder name="Szenen">
        <Composition
          id="Hook"
          component={HookScene}
          durationInFrames={105}
          fps={30}
          width={1080}
          height={1920}
          defaultProps={{ style: { backgroundColor: "#0A0E14" } }}
        />
        <Composition
          id="Multimeter"
          component={MultimeterScene}
          durationInFrames={165}
          fps={30}
          width={1080}
          height={1920}
          defaultProps={{ style: { backgroundColor: "#0A0E14" } }}
        />
        <Composition
          id="Oberschwingungen"
          component={HarmonicsScene}
          durationInFrames={210}
          fps={30}
          width={1080}
          height={1920}
          defaultProps={{ style: { backgroundColor: "#0A0E14" } }}
        />
        <Composition
          id="Einbruch"
          component={DipScene}
          durationInFrames={210}
          fps={30}
          width={1080}
          height={1920}
          defaultProps={{ style: { backgroundColor: "#0A0E14" } }}
        />
        <Composition
          id="Messen"
          component={MeasureScene}
          durationInFrames={180}
          fps={30}
          width={1080}
          height={1920}
          defaultProps={{ style: { backgroundColor: "#0A0E14" } }}
        />
        <Composition
          id="Outro"
          component={OutroScene}
          durationInFrames={120}
          fps={30}
          width={1080}
          height={1920}
          defaultProps={{ style: { backgroundColor: "#0A0E14" } }}
        />
      </Folder>
    </>
  );
};
