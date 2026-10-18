import type React from "react";
import { Interactive } from "remotion";
import { colors, headFont } from "../theme";

const HeadlineInner = ({
  children,
  style,
}: {
  readonly children: React.ReactNode;
  readonly style?: React.CSSProperties;
}) => (
  <div
    style={{
      fontFamily: headFont,
      fontSize: 96,
      fontWeight: 700,
      lineHeight: 1.05,
      letterSpacing: "-0.02em",
      color: colors.fg,
      ...style,
    }}
  >
    {children}
  </div>
);

export const Headline = Interactive.create({
  Component: HeadlineInner,
  layout: "none",
  schema: {
    ...Interactive.textSchema,
    ...Interactive.childrenSchema,
  },
});
