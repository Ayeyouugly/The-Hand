import {
  AbsoluteFill,
  Video,
  Img,
  staticFile,
  interpolate,
  useCurrentFrame,
  Sequence
} from "remotion";
import masterLayoutDataRaw from "../orchestration_data/master_layout_data.json";

// Import locally extracted SVGs
import board01_svg from "../assets/master_svgs/board_01.json";
import board02_svg from "../assets/master_svgs/board_02.json";
import board03_svg from "../assets/master_svgs/board_03.json";
import board04_svg from "../assets/master_svgs/board_04.json";
import board05_svg from "../assets/master_svgs/board_05.json";
import board06_svg from "../assets/master_svgs/board_06.json";
import board07_svg from "../assets/master_svgs/board_07.json";

const svgDataMap: Record<number, any> = {
  1: board01_svg,
  2: board02_svg,
  3: board03_svg,
  4: board04_svg,
  5: board05_svg,
  6: board06_svg,
  7: board07_svg,
};

// Cast JSON to strictly typed interface
interface HandGuidance {
  hand_x?: number; // fallback logic to be used if undefined
  hand_y?: number;
  negative_space_zones?: string[];
  hand_entry_points?: string[];
  clearance_instructions?: string;
  recommended_hand_style?: string;
}

interface Timing {
  layer: string;
  start: number;
  duration: number;
  sync_to_voice: string;
}

interface BoardData {
  board_number: number;
  master_image_prompt?: string;
  svg_layers?: string[];
  draw_order_and_timings: Timing[];
  qualia_resonance?: string;
  visual_metaphors_used?: string[];
  topological_morph_notes?: string;
  svg_extraction_path?: string;
  hand_guidance: HandGuidance;
}

const masterLayoutData = masterLayoutDataRaw as BoardData[];

// Dynamically calculate the total frames for the composition
export const CALCULATED_TOTAL_FRAMES = Math.ceil(
  masterLayoutData.reduce((max, board) => {
    const timings = board.draw_order_and_timings;
    if (!timings || timings.length === 0) return max;
    const lastTiming = timings[timings.length - 1];
    const end = lastTiming.start + lastTiming.duration;
    return Math.max(max, end);
  }, 0) * 30
) + 60; // 2 seconds tail padding

const BoardLayer = ({ board, durationInFrames, startSeconds }: { board: BoardData, durationInFrames: number, startSeconds: number }) => {
  const frame = useCurrentFrame();
  const currentGlobalSeconds = startSeconds + frame / 30;

  // Progress relative to actual drawing times mapping to 0->1
  const timings = board.draw_order_and_timings || [];
  const firstDrawStart = timings.length > 0 ? timings[0].start : startSeconds;
  const lastTiming = timings[timings.length - 1];
  const lastDrawEnd = lastTiming ? lastTiming.start + lastTiming.duration : startSeconds + durationInFrames / 30;

  const drawPercent = Math.min(1, Math.max(0, interpolate(currentGlobalSeconds, [firstDrawStart, lastDrawEnd], [0, 1])));

  // Provide a central fallback (960, 540) if the JSON drops hand_x/hand_y explicitly.
  const targetX = board.hand_guidance.hand_x ?? (1920 / 2);
  const targetY = board.hand_guidance.hand_y ?? (1080 / 2);

  // 1. Math simulating realistic hand "scribbling" roughly tracking the drawing progress
  const startX = targetX - 500;
  const endX = targetX;
  
  const baseProgressX = interpolate(drawPercent, [0, 1], [startX, endX]);
  const baseProgressY = interpolate(drawPercent, [0, 1], [targetY + 200, targetY]);
  
  const scribbleX = Math.sin(drawPercent * Math.PI * 18) * 80;
  const scribbleY = Math.cos(drawPercent * Math.PI * 24) * 80;

  const currentHandX = baseProgressX + scribbleX;
  const currentHandY = baseProgressY + scribbleY;

  const svgContent = svgDataMap[board.board_number]?.svg_content || "";

  return (
    <AbsoluteFill>
      <style>
        {".board-svg-wrapper_" + board.board_number + " svg {\n" +
         "  width: 100%;\n" +
         "  height: 100%;\n" +
         "  position: absolute;\n" +
         "  top: 0;\n" +
         "  left: 0;\n" +
         "  z-index: 5;\n" +
         "}\n" +
         "/* Default hidden for any paths not explicitly timed */\n" +
         ".board-svg-wrapper_" + board.board_number + " svg path {\n" +
         "  stroke-dasharray: 4000;\n" +
         "  stroke-dashoffset: 4000;\n" +
         "}\n" + 
         timings.map(timing => {
            // Extrapolate clamp means it stays 4000 before start, and 0 after end
            const offset = interpolate(
              currentGlobalSeconds, 
              [timing.start, timing.start + timing.duration], 
              [4000, 0], 
              { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
            );
            return ".board-svg-wrapper_" + board.board_number + " #" + timing.layer + " path {\n" +
                   "  stroke-dasharray: 4000;\n" +
                   "  stroke-dashoffset: " + offset + ";\n" +
                   "  transition: stroke-dashoffset 0.1s linear;\n" +
                   "}\n";
          }).join("\n")}
      </style>

      {/* Underlying Master Layout Image: softly fades in as the SVG paths are fully drawn */}
      <AbsoluteFill>
        <Img
          src={staticFile(
            `assets/master_layout_images/board_${String(board.board_number).padStart(2, "0")}.png`
          )}
          style={{ 
            width: "100%", 
            height: "100%", 
            objectFit: "cover",
            opacity: interpolate(drawPercent, [0, 0.8, 1], [0, 0, 1]) // fully appears at the very end 
          }}
          alt={`Board ${board.board_number}`}
        />
      </AbsoluteFill>

      {/* Dynamic SVG Line Reveal Layer */}
      <AbsoluteFill 
        className={`board-svg-wrapper_${board.board_number}`}
        dangerouslySetInnerHTML={{ __html: svgContent }} 
      />

      {/* Hand Marker Overlay */}
      <AbsoluteFill
        style={{
          transform: `translate(${currentHandX - 90}px, ${currentHandY - 120}px)`,
          width: "100%",
          height: "100%",
          pointerEvents: "none",
          zIndex: 10
        }}
      >
        <Video
          src={staticFile("assets/hand_references/hand_marker_alpha.webm")}
          style={{
            width: "800px",
            height: "auto",
          }}
        />
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

export const WhiteboardComposition = () => {
  return (
    <AbsoluteFill style={{ backgroundColor: "white" }}>
      {masterLayoutData.map((board, index) => {
        const nextBoard = masterLayoutData[index + 1];

        let startSeconds = 0;
        if (index > 0 && board.draw_order_and_timings?.length > 0) {
          startSeconds = board.draw_order_and_timings[0].start;
        }

        let endSeconds = startSeconds + 5; 
        if (nextBoard && nextBoard.draw_order_and_timings?.length > 0) {
          endSeconds = nextBoard.draw_order_and_timings[0].start;
        } else if (board.draw_order_and_timings?.length > 0) {
          const lastTiming = board.draw_order_and_timings[board.draw_order_and_timings.length - 1];
          endSeconds = lastTiming.start + lastTiming.duration + 2; 
        }

        const startFrame = Math.round(startSeconds * 30);
        const durationInFrames = Math.max(1, Math.round((endSeconds - startSeconds) * 30));

        return (
          <Sequence
            key={board.board_number}
            from={startFrame}
            durationInFrames={durationInFrames}
            name={`Board_${board.board_number}`}
          >
            <BoardLayer board={board} durationInFrames={durationInFrames} startSeconds={startSeconds} />
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};
