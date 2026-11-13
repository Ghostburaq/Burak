import { MyComposition } from "./Composition";
import { ErinnerungComp } from "./Erinnerung";
import { ErinnerungWarmComp } from "./ErinnerungWarm";
import { ShowcaseComp } from "./Showcase";
import { ErklaerComp } from "./Erklaer";
import { PTPromoComp } from "./PTPromo";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <MyComposition />
      <ErinnerungComp />
      <ErinnerungWarmComp />
      <ShowcaseComp />
      <ErklaerComp />
      <PTPromoComp />
    </>
  );
};
