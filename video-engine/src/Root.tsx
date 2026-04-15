import "./index.css";
import { Composition } from "remotion";
import { MyComposition } from "./Composition";
import { WhiteboardComposition, CALCULATED_TOTAL_FRAMES } from "../WhiteboardComposition";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="MyComp"
        component={MyComposition}
        durationInFrames={60}
        fps={30}
        width={1280}
        height={720}
      />
      <Composition
        id="Whiteboard"
        component={WhiteboardComposition}
        durationInFrames={CALCULATED_TOTAL_FRAMES}
        fps={30}
        width={1920}
        height={1080}
      />
    </>
  );
};
