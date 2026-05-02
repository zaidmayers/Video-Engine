import React from "react";
import {
  useCurrentFrame,
  interpolate,
  Easing,
  AbsoluteFill,
} from "remotion";
import { fontFamily } from "../fonts";

const NODES = [
  {
    label: "Documents",
    desc: "PDFs, wikis, emails, Notion pages...",
    color: "#6366f1",
    icon: (
      <svg width={48} height={48} viewBox="0 0 48 48">
        <rect x="8" y="4" width="28" height="36" rx="4" fill="none" stroke="#6366f1" strokeWidth="2.5"/>
        <line x1="14" y1="14" x2="30" y2="14" stroke="#6366f1" strokeWidth="2"/>
        <line x1="14" y1="21" x2="30" y2="21" stroke="#6366f1" strokeWidth="2"/>
        <line x1="14" y1="28" x2="24" y2="28" stroke="#6366f1" strokeWidth="2"/>
        <rect x="28" y="2" width="12" height="12" rx="2" fill="#0a0a0a" stroke="#6366f1" strokeWidth="1.5"/>
        <path d="M 28 2 L 28 10 L 36 10" fill="none" stroke="#6366f1" strokeWidth="1.5"/>
      </svg>
    ),
  },
  {
    label: "Text Chunks",
    desc: "256–512 token semantic splits",
    color: "#8b5cf6",
    icon: (
      <svg width={48} height={48} viewBox="0 0 48 48">
        <rect x="4" y="8" width="18" height="14" rx="3" fill="none" stroke="#8b5cf6" strokeWidth="2.5"/>
        <rect x="26" y="8" width="18" height="14" rx="3" fill="none" stroke="#8b5cf6" strokeWidth="2.5"/>
        <rect x="4" y="26" width="18" height="14" rx="3" fill="none" stroke="#8b5cf6" strokeWidth="2.5"/>
        <rect x="26" y="26" width="18" height="14" rx="3" fill="none" stroke="#8b5cf6" strokeWidth="2.5"/>
        <line x1="22" y1="15" x2="26" y2="15" stroke="#8b5cf6" strokeWidth="2" strokeDasharray="2 2"/>
        <line x1="22" y1="33" x2="26" y2="33" stroke="#8b5cf6" strokeWidth="2" strokeDasharray="2 2"/>
      </svg>
    ),
  },
  {
    label: "Embeddings",
    desc: "Dense vectors encoding meaning",
    color: "#a855f7",
    icon: (
      <svg width={48} height={48} viewBox="0 0 48 48">
        {[0,1,2,3,4,5,6,7].map(i => (
          <rect key={i} x={4 + i * 5} y={48 - 8 - (i % 5 + 1) * 6} width="4"
            height={(i % 5 + 1) * 6} rx="1"
            fill="#a855f7" opacity={0.5 + (i % 3) * 0.2}/>
        ))}
        <line x1="4" y1="40" x2="44" y2="40" stroke="#a855f7" strokeWidth="1.5"/>
      </svg>
    ),
  },
  {
    label: "Vector DB",
    desc: "Pinecone, Chroma, Weaviate...",
    color: "#22c55e",
    icon: (
      <svg width={48} height={48} viewBox="0 0 48 48">
        <ellipse cx="24" cy="12" rx="18" ry="7" fill="none" stroke="#22c55e" strokeWidth="2.5"/>
        <line x1="6" y1="12" x2="6" y2="36" stroke="#22c55e" strokeWidth="2.5"/>
        <line x1="42" y1="12" x2="42" y2="36" stroke="#22c55e" strokeWidth="2.5"/>
        <ellipse cx="24" cy="36" rx="18" ry="7" fill="none" stroke="#22c55e" strokeWidth="2.5"/>
        <ellipse cx="24" cy="24" rx="18" ry="7" fill="none" stroke="#22c55e" strokeWidth="1.5" opacity={0.5}/>
      </svg>
    ),
  },
];

const ARROW_LEN = 55;
const NODE_DELAYS = [28, 72, 116, 160];
const ARROW_DELAYS = [55, 99, 143];

export const Scene3: React.FC = () => {
  const frame = useCurrentFrame();

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

  const arrowProgress = (delay: number) =>
    interpolate(frame, [delay, delay + 30], [0, 1], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    });

  return (
    <AbsoluteFill style={{ background: "#0a0a0a", fontFamily }}>
      {/* Label */}
      <div style={{
        position: "absolute", top: 160, left: 60,
        color: "#6366f1", fontSize: 28, fontWeight: 600,
        letterSpacing: 5, textTransform: "uppercase" as const,
        opacity: e(5),
      }}>
        Step 1 — Index
      </div>

      {/* Headline */}
      <div style={{
        position: "absolute", top: 218, left: 60, right: 60,
        color: "#fff", fontSize: 66, fontWeight: 800, lineHeight: 1.1,
        opacity: e(10),
        transform: `translateY(${up(10)}px)`,
      }}>
        Build your knowledge base
      </div>

      {/* Subtext */}
      <div style={{
        position: "absolute", top: 355, left: 60, right: 60,
        color: "#6b7280", fontSize: 32, lineHeight: 1.5,
        opacity: e(18),
      }}>
        Index once. Search forever.
      </div>

      {/* Flowchart nodes */}
      {NODES.map((node, i) => {
        const nodeOp = e(NODE_DELAYS[i], 22);
        const nodeY = up(NODE_DELAYS[i], 28, 22);
        const topY = 428 + i * 180;

        return (
          <React.Fragment key={i}>
            {/* Arrow above (except first) */}
            {i > 0 && (
              <div style={{
                position: "absolute",
                top: topY - 58,
                left: "50%",
                transform: "translateX(-50%)",
              }}>
                <svg width={40} height={58} viewBox="0 0 40 58" overflow="visible">
                  {/* Stem */}
                  <line
                    x1="20" y1="0" x2="20" y2="38"
                    stroke={NODES[i - 1].color} strokeWidth="3" strokeLinecap="round"
                    strokeDasharray={ARROW_LEN}
                    strokeDashoffset={ARROW_LEN - arrowProgress(ARROW_DELAYS[i - 1]) * ARROW_LEN}
                  />
                  {/* Arrowhead */}
                  <path
                    d="M 8 32 L 20 48 L 32 32"
                    fill="none" stroke={NODES[i - 1].color} strokeWidth="3" strokeLinecap="round"
                    strokeDasharray={40}
                    strokeDashoffset={40 - arrowProgress(ARROW_DELAYS[i - 1] + 18) * 40}
                  />
                </svg>
              </div>
            )}

            {/* Node card */}
            <div style={{
              position: "absolute",
              top: topY,
              left: 60, right: 60,
              opacity: nodeOp,
              transform: `translateY(${nodeY}px)`,
              background: "#0f0f1a",
              border: `2px solid ${node.color}`,
              borderRadius: 20,
              padding: "22px 28px",
              display: "flex", alignItems: "center", gap: 24,
            }}>
              <div style={{
                width: 64, height: 64,
                background: `${node.color}18`,
                borderRadius: 14,
                display: "flex", alignItems: "center", justifyContent: "center",
                flexShrink: 0,
              }}>
                {node.icon}
              </div>
              <div>
                <div style={{ color: "#fff", fontSize: 34, fontWeight: 700 }}>
                  {node.label}
                </div>
                <div style={{ color: "#6b7280", fontSize: 26, marginTop: 4 }}>
                  {node.desc}
                </div>
              </div>
              {/* Step number */}
              <div style={{
                marginLeft: "auto",
                width: 44, height: 44,
                borderRadius: "50%",
                background: `${node.color}22`,
                border: `2px solid ${node.color}`,
                display: "flex", alignItems: "center", justifyContent: "center",
                color: node.color, fontSize: 22, fontWeight: 800,
                flexShrink: 0,
              }}>
                {i + 1}
              </div>
            </div>
          </React.Fragment>
        );
      })}

      {/* Bottom note */}
      <div style={{
        position: "absolute", bottom: 185, left: 60, right: 60,
        opacity: e(168, 20),
        textAlign: "center" as const,
        color: "#22c55e", fontSize: 30, fontWeight: 600,
      }}>
        ✓ Indexed once — queried in milliseconds
      </div>
    </AbsoluteFill>
  );
};
