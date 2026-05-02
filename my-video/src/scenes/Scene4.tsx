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

const CHUNKS = [
  { text: "Q1 2025 revenue surged 47% YoY driven by...", score: "0.92" },
  { text: "January 2025 saw record user growth of 2.1M...", score: "0.87" },
  { text: "Q1 2025 summary: margin expansion to 32%...", score: "0.79" },
];

const VECTOR_HEIGHTS = [55, 35, 70, 45, 60, 30, 65, 50];
const VECTOR_COLORS = ["#6366f1","#818cf8","#6366f1","#a5b4fc","#818cf8","#6366f1","#a5b4fc","#6366f1"];

export const Scene4: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const e = (delay: number, dur = 20) =>
    interpolate(frame, [delay, delay + dur], [0, 1], {
      easing: Easing.bezier(0.16, 1, 0.3, 1),
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    });

  const up = (delay: number, dist = 30, dur = 22) =>
    interpolate(frame, [delay, delay + dur], [dist, 0], {
      easing: Easing.bezier(0.16, 1, 0.3, 1),
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    });

  const arrowDraw = (delay: number, len: number) =>
    interpolate(frame, [delay, delay + 25], [len, 0], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    });

  const queryScale = spring({ frame: frame - 32, fps, config: { damping: 200 } });
  const answerScale = spring({ frame: frame - 185, fps, config: { damping: 200 } });

  return (
    <AbsoluteFill style={{ background: "#0a0a0a", fontFamily }}>
      {/* Label */}
      <div style={{
        position: "absolute", top: 160, left: 60,
        color: "#6366f1", fontSize: 28, fontWeight: 600,
        letterSpacing: 5, textTransform: "uppercase" as const,
        opacity: e(5),
      }}>
        Step 2 — Query
      </div>

      {/* Headline */}
      <div style={{
        position: "absolute", top: 218, left: 60, right: 60,
        color: "#fff", fontSize: 66, fontWeight: 800, lineHeight: 1.1,
        opacity: e(10),
        transform: `translateY(${up(10, 40)}px)`,
      }}>
        Retrieve, then generate
      </div>

      {/* Query input */}
      <div style={{
        position: "absolute", top: 380, left: 60, right: 60,
        transform: `scale(${queryScale})`,
        transformOrigin: "top center",
        background: "#111827",
        border: "2px solid #374151",
        borderRadius: 16, padding: "18px 26px",
      }}>
        <div style={{ color: "#6b7280", fontSize: 24, marginBottom: 4 }}>Query</div>
        <div style={{ color: "#e5e7eb", fontSize: 32, fontWeight: 600 }}>
          "What happened in Q1 2025?"
        </div>
      </div>

      {/* Arrow 1: query → vector */}
      <div style={{
        position: "absolute", top: 495, left: "50%",
        transform: "translateX(-50%)",
        opacity: e(62, 15),
      }}>
        <svg width={40} height={50} viewBox="0 0 40 50">
          <line x1="20" y1="2" x2="20" y2="32" stroke="#4f46e5" strokeWidth="2.5"
            strokeDasharray={32} strokeDashoffset={arrowDraw(62, 32)}/>
          <path d="M 9 26 L 20 42 L 31 26" fill="none" stroke="#4f46e5" strokeWidth="2.5"
            strokeDasharray={30} strokeDashoffset={arrowDraw(72, 30)}/>
        </svg>
      </div>

      {/* Embedding vector visualization */}
      <div style={{
        position: "absolute", top: 548, left: 60, right: 60,
        opacity: e(75),
        transform: `translateY(${up(75)}px)`,
        background: "#0f1628",
        border: "2px solid #4f46e5",
        borderRadius: 16, padding: "16px 24px",
      }}>
        <div style={{ color: "#6b7280", fontSize: 24, marginBottom: 10 }}>
          Embedding Vector
        </div>
        <div style={{ display: "flex", alignItems: "flex-end", gap: 8, height: 80 }}>
          {VECTOR_HEIGHTS.map((h, i) => (
            <div key={i} style={{
              flex: 1,
              height: h,
              background: VECTOR_COLORS[i],
              borderRadius: 4,
              opacity: 0.7,
            }}/>
          ))}
          <div style={{
            color: "#6b7280", fontSize: 26, marginLeft: 8,
            alignSelf: "center",
          }}>…</div>
        </div>
        <div style={{ color: "#4f46e5", fontSize: 22, marginTop: 8 }}>
          [0.23, -0.87, 0.45, 0.12, 0.67, -0.34, 0.91, 0.08, ...]
        </div>
      </div>

      {/* Arrow 2: vector → DB */}
      <div style={{
        position: "absolute", top: 700, left: "50%",
        transform: "translateX(-50%)",
        opacity: e(98, 15),
      }}>
        <svg width={40} height={50} viewBox="0 0 40 50">
          <line x1="20" y1="2" x2="20" y2="32" stroke="#8b5cf6" strokeWidth="2.5"
            strokeDasharray={32} strokeDashoffset={arrowDraw(98, 32)}/>
          <path d="M 9 26 L 20 42 L 31 26" fill="none" stroke="#8b5cf6" strokeWidth="2.5"
            strokeDasharray={30} strokeDashoffset={arrowDraw(108, 30)}/>
        </svg>
      </div>

      {/* Vector DB + top-K chunks */}
      <div style={{
        position: "absolute", top: 752, left: 60, right: 60,
        opacity: e(110),
        transform: `translateY(${up(110)}px)`,
      }}>
        {/* DB header */}
        <div style={{
          background: "#0f1628", border: "2px solid #22c55e",
          borderRadius: "16px 16px 0 0", padding: "14px 24px",
          display: "flex", alignItems: "center", gap: 14,
        }}>
          <svg width={32} height={32} viewBox="0 0 32 32">
            <ellipse cx="16" cy="8" rx="12" ry="5" fill="none" stroke="#22c55e" strokeWidth="2"/>
            <line x1="4" y1="8" x2="4" y2="24" stroke="#22c55e" strokeWidth="2"/>
            <line x1="28" y1="8" x2="28" y2="24" stroke="#22c55e" strokeWidth="2"/>
            <ellipse cx="16" cy="24" rx="12" ry="5" fill="none" stroke="#22c55e" strokeWidth="2"/>
          </svg>
          <span style={{ color: "#22c55e", fontSize: 28, fontWeight: 700 }}>
            Vector DB — Searching...
          </span>
        </div>
        {/* Retrieved chunks */}
        {CHUNKS.map((chunk, i) => {
          const chunkOp = e(128 + i * 12, 20);
          const chunkScale = spring({ frame: frame - (128 + i * 12), fps, config: { damping: 200 } });
          return (
            <div key={i} style={{
              background: "#0a1528",
              border: "1px solid #1e3a5f",
              borderTop: "none",
              borderRadius: i === CHUNKS.length - 1 ? "0 0 16px 16px" : 0,
              padding: "14px 24px",
              display: "flex", alignItems: "center", gap: 16,
              opacity: chunkOp,
              transform: `scale(${chunkScale})`,
              transformOrigin: "top center",
            }}>
              <div style={{
                width: 10, height: 10, borderRadius: "50%",
                background: "#22c55e", flexShrink: 0,
              }}/>
              <div style={{ flex: 1 }}>
                <div style={{ color: "#d1d5db", fontSize: 26, lineHeight: 1.4 }}>
                  {chunk.text}
                </div>
              </div>
              <div style={{
                background: "#052e16", border: "1px solid #22c55e",
                borderRadius: 8, padding: "4px 12px",
                color: "#22c55e", fontSize: 22, fontWeight: 700, flexShrink: 0,
              }}>
                {chunk.score}
              </div>
            </div>
          );
        })}
      </div>

      {/* Arrow 3: chunks → LLM */}
      <div style={{
        position: "absolute", top: 1140, left: "50%",
        transform: "translateX(-50%)",
        opacity: e(160, 15),
      }}>
        <svg width={40} height={50} viewBox="0 0 40 50">
          <line x1="20" y1="2" x2="20" y2="32" stroke="#6366f1" strokeWidth="2.5"
            strokeDasharray={32} strokeDashoffset={arrowDraw(160, 32)}/>
          <path d="M 9 26 L 20 42 L 31 26" fill="none" stroke="#6366f1" strokeWidth="2.5"
            strokeDasharray={30} strokeDashoffset={arrowDraw(170, 30)}/>
        </svg>
      </div>

      {/* LLM box */}
      <div style={{
        position: "absolute", top: 1192, left: 60, right: 60,
        opacity: e(170),
        transform: `translateY(${up(170)}px)`,
        background: "#1e1b4b", border: "2px solid #6366f1",
        borderRadius: 16, padding: "18px 26px",
        display: "flex", alignItems: "center", gap: 20,
      }}>
        <div style={{
          width: 60, height: 60, borderRadius: 14,
          background: "#312e81",
          display: "flex", alignItems: "center", justifyContent: "center",
          flexShrink: 0,
        }}>
          <svg width={36} height={36} viewBox="0 0 36 36">
            <circle cx="18" cy="18" r="14" fill="none" stroke="#818cf8" strokeWidth="2"/>
            <path d="M 10 18 Q 18 10 26 18 Q 18 26 10 18" fill="none" stroke="#818cf8" strokeWidth="2"/>
            <circle cx="18" cy="18" r="3" fill="#818cf8"/>
          </svg>
        </div>
        <div>
          <div style={{ color: "#a5b4fc", fontSize: 24 }}>LLM + injected context</div>
          <div style={{ color: "#fff", fontSize: 30, fontWeight: 700 }}>Generating answer...</div>
        </div>
      </div>

      {/* Answer */}
      <div style={{
        position: "absolute", top: 1360, left: 60, right: 60,
        transform: `scale(${answerScale})`,
        transformOrigin: "top center",
        background: "#052e16", border: "2px solid #22c55e",
        borderRadius: 16, padding: "20px 26px",
      }}>
        <div style={{ color: "#22c55e", fontSize: 26, fontWeight: 600, marginBottom: 6 }}>
          ✓ Grounded Answer
        </div>
        <div style={{ color: "#d1d5db", fontSize: 28, lineHeight: 1.5 }}>
          "Based on retrieved data: Q1 2025 saw 47% revenue growth, record user acquisition, and 32% margin expansion."
        </div>
      </div>
    </AbsoluteFill>
  );
};
