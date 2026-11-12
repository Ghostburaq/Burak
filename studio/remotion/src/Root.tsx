import { MyComposition } from "./Composition";
import { ErinnerungComp } from "./Erinnerung";
import { ErinnerungWarmComp } from "./ErinnerungWarm";
import { ShowcaseComp } from "./Showcase";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <MyComposition />
      <ErinnerungComp />
      <ErinnerungWarmComp />
      <ShowcaseComp />
    </>
  );
};
