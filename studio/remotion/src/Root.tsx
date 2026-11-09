import { MyComposition } from "./Composition";
import { ErinnerungComp } from "./Erinnerung";
import { ErinnerungWarmComp } from "./ErinnerungWarm";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <MyComposition />
      <ErinnerungComp />
      <ErinnerungWarmComp />
    </>
  );
};
