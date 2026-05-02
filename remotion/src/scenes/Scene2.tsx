import React from "react";
import {
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  Easing,
  spring,
  AbsoluteFill,
} from "remotion";
import { fontFamily } from "../fonts";

const ROWS = [
  {
    letter: "R",
    rest: "etrieval",
    desc: "Fetch relevant docs from your knowledge base at query time",
  },
  {
    letter: "A",
    rest: "ugmented",
    desc: "Inject retrieved context directly into the LLM prompt",
  },
  {
    letter: "G",
    rest: "eneration",
    desc: "LLM generates an accurate, grounded response",
  },
];

export const Scene2: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const e = (delay: number, dur = 20) =>
    interpolate(frame, [delay, delay + dur], [0, 1], {
      easing: Easing.bezier(0.16, 1, 0.3, 1),
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    });

  const up = (delay: number, dist = 40, dur = 25) =>
    interpolate(frame, [delay, delay + dur], [dist, 0], {
      easing: Easing.bezier(0.16, 1, 0.3, 1),
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    });

  const letterDelays = [22, 34, 46];
  const wordDelays = [45, 57, 69];
  const descDelays = [88, 100, 112];

  return (
    <AbsoluteFill style={{ background: "#0a0a0a", fontFamily }}>
      {/* Radial glow */}
      <div style={{
        position: "absolute",
        top: 600, left: "50%",
        transform: "translateX(-50%)",
        width: 900, height: 900,
        borderRadius: "50%",
        background: "radial-gradient(circle, rgba(99,102,241,0.1) 0%, transparent 70%)",
        opacity: e(8),
      }}/>

      {/* Label */}
      <div style={{
        position: "absolute", top: 160, left: 60,
        color: "#22c55e", fontSize: 28, fontWeight: 600,
        letterSpacing: 5, textTransform: "uppercase" as const,
        opacity: e(5),
      }}>
        The Solution
      </div>

      {/* Headline */}
      <div style={{
        position: "absolute", top: 218, left: 60, right: 60,
        color: "#fff", fontSize: 62, fontWeight: 800, lineHeight: 1.1,
        opacity: e(10),
        transform: `translateY(${up(10)}px)`,
      }}>
        Give the LLM a searchable memory
      </div>

      {/* RAG rows */}
      {ROWS.map((row, i) => {
        const letterScale = spring({ frame: frame - letterDelays[i], fps, config: { damping: 200 } });
        const wordOp = e(wordDelays[i], 18);
        const descOp = e(descDelays[i], 20);
        const topY = 460 + i * 250;

        return (
          <div key={i} style={{ position: "absolute", top: topY, left: 60, right: 60 }}>
            {/* Letter + word row */}
            <div style={{ display: "flex", alignItems: "flex-end", gap: 0 }}>
              <span style={{
                fontSize: 148,
                fontWeight: 800,
                color: "#6366f1",
                lineHeight: 1,
                display: "inline-block",
                transform: `scale(${letterScale})`,
                transformOrigin: "left bottom",
                textShadow: "0 0 80px rgba(99,102,241,0.5)",
              }}>
                {row.letter}
              </span>
              <span style={{
                fontSize: 72,
                fontWeight: 700,
                color: "white",
                lineHeight: 1,
                marginBottom: 10,
                opacity: wordOp,
              }}>
                {row.rest}{i < ROWS.length - 1 ? "-" : ""}
              </span>
            </div>
            {/* Description */}
            <div style={{
              color: "#6b7280", fontSize: 30, fontWeight: 400,
              marginTop: -8, marginLeft: 4,
              opacity: descOp,
            }}>
              {row.desc}
            </div>
          </div>
        );
      })}

      {/* Bottom tagline */}
      <div style={{
        position: "absolute", bottom: 185, left: 60, right: 60,
        opacity: e(148, 28),
        transform: `translateY(${up(148, 30)}px)`,
        borderTop: "1px solid #1f2937",
        paddingTop: 28,
        textAlign: "center" as const,
        color: "#9ca3af", fontSize: 32, lineHeight: 1.5,
      }}>
        No retraining required — just retrieval
      </div>
    </AbsoluteFill>
  );
};
