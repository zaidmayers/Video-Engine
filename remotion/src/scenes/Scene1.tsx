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

const NODES = [
  { x: 90, y: 90 }, { x: 160, y: 65 }, { x: 230, y: 90 },
  { x: 65, y: 160 }, { x: 160, y: 160 }, { x: 255, y: 160 },
  { x: 90, y: 230 }, { x: 160, y: 255 }, { x: 230, y: 230 },
];
const EDGES = [
  [0,1],[1,2],[0,4],[1,4],[2,4],[3,4],[4,5],[4,6],[4,7],[4,8],[6,7],[7,8],[0,3],[2,5],
];

export const Scene1: React.FC = () => {
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

  const brainScale = spring({ frame: frame - 28, fps, config: { damping: 200 } });
  const iceOpacity = e(52, 22);
  const xProgress = interpolate(frame, [98, 130], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const calendarSlide = interpolate(frame, [78, 105], [-60, 0], {
    easing: Easing.bezier(0.16, 1, 0.3, 1),
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const queryBounce = interpolate(frame, [130, 155], [-30, 0], {
    easing: Easing.bezier(0.34, 1.56, 0.64, 1),
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={{ background: "#0a0a0a", fontFamily }}>
      {/* Grid */}
      <svg style={{ position: "absolute", top: 0, left: 0, opacity: 0.06 }} width={1080} height={1920}>
        <defs>
          <pattern id="s1grid" width="80" height="80" patternUnits="userSpaceOnUse">
            <path d="M 80 0 L 0 0 0 80" fill="none" stroke="#6366f1" strokeWidth="1"/>
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#s1grid)"/>
      </svg>

      {/* Section label */}
      <div style={{
        position: "absolute", top: 160, left: 60,
        color: "#6366f1", fontSize: 28, fontWeight: 600,
        letterSpacing: 5, textTransform: "uppercase" as const,
        opacity: e(5),
      }}>
        The Problem
      </div>

      {/* Headline */}
      <div style={{
        position: "absolute", top: 218, left: 60, right: 60,
        color: "#fff", fontSize: 70, fontWeight: 800, lineHeight: 1.1,
        opacity: e(12),
        transform: `translateY(${up(12)}px)`,
      }}>
        LLMs have a knowledge cutoff
      </div>

      {/* Subtext */}
      <div style={{
        position: "absolute", top: 430, left: 60, right: 60,
        color: "#6b7280", fontSize: 34, lineHeight: 1.5,
        opacity: e(22),
      }}>
        Static training data means stale answers, hallucinations, and blind spots.
      </div>

      {/* Brain network — center visual */}
      <div style={{
        position: "absolute", top: 552, left: "50%",
        transform: `translateX(-50%) scale(${brainScale})`,
        transformOrigin: "50% 50%",
      }}>
        <svg width={320} height={320} viewBox="0 0 320 320">
          {/* Ice fill */}
          <circle cx="160" cy="160" r="145" fill="#0d1b3e" opacity={iceOpacity}/>
          {/* Ice border */}
          <circle cx="160" cy="160" r="145" fill="none" stroke="#3b82f6"
            strokeWidth="3" strokeDasharray="12 6" opacity={iceOpacity}/>
          {/* Ice cracks */}
          <path d="M 20 60 L 55 80 L 38 115" fill="none" stroke="#bfdbfe" strokeWidth="1.5" opacity={iceOpacity * 0.5}/>
          <path d="M 280 50 L 250 80 L 270 115" fill="none" stroke="#bfdbfe" strokeWidth="1.5" opacity={iceOpacity * 0.5}/>
          <path d="M 35 250 L 70 235 L 58 278" fill="none" stroke="#bfdbfe" strokeWidth="1.5" opacity={iceOpacity * 0.5}/>
          {/* Neural edges */}
          {EDGES.map(([a, b], i) => (
            <line key={i}
              x1={NODES[a].x} y1={NODES[a].y}
              x2={NODES[b].x} y2={NODES[b].y}
              stroke="#c084fc" strokeWidth="1.5" opacity={0.35}
            />
          ))}
          {/* Neural nodes */}
          {NODES.map((n, i) => (
            <circle key={i} cx={n.x} cy={n.y} r={i === 4 ? 16 : 9}
              fill={i === 4 ? "#c084fc" : "#8b5cf6"} opacity={0.8}/>
          ))}
          {/* Center LLM label */}
          <text x="160" y="167" textAnchor="middle" fill="#fff" fontSize="16"
            fontFamily="sans-serif" fontWeight="bold">LLM</text>
          {/* Snowflake */}
          <g transform="translate(160, 235)" opacity={iceOpacity}>
            <line x1="0" y1="-14" x2="0" y2="14" stroke="#93c5fd" strokeWidth="2.5"/>
            <line x1="-14" y1="0" x2="14" y2="0" stroke="#93c5fd" strokeWidth="2.5"/>
            <line x1="-10" y1="-10" x2="10" y2="10" stroke="#93c5fd" strokeWidth="2"/>
            <line x1="10" y1="-10" x2="-10" y2="10" stroke="#93c5fd" strokeWidth="2"/>
            <circle cx="0" cy="-14" r="2" fill="#93c5fd"/>
            <circle cx="0" cy="14" r="2" fill="#93c5fd"/>
            <circle cx="-14" cy="0" r="2" fill="#93c5fd"/>
            <circle cx="14" cy="0" r="2" fill="#93c5fd"/>
          </g>
        </svg>
      </div>

      {/* Cutoff badge */}
      <div style={{
        position: "absolute", top: 920, left: 60, right: 60,
        opacity: e(78),
        transform: `translateX(${calendarSlide}px)`,
        background: "#1e1b4b",
        border: "2px solid #6366f1",
        borderRadius: 20, padding: "22px 32px",
        display: "flex", alignItems: "center", gap: 20,
      }}>
        <svg width={44} height={44} viewBox="0 0 44 44">
          <rect x="2" y="6" width="40" height="36" rx="5" fill="none" stroke="#6366f1" strokeWidth="2.5"/>
          <line x1="14" y1="2" x2="14" y2="11" stroke="#6366f1" strokeWidth="2.5" strokeLinecap="round"/>
          <line x1="30" y1="2" x2="30" y2="11" stroke="#6366f1" strokeWidth="2.5" strokeLinecap="round"/>
          <line x1="2" y1="17" x2="42" y2="17" stroke="#6366f1" strokeWidth="1.5"/>
          <text x="22" y="34" textAnchor="middle" fill="#93c5fd" fontSize="8.5"
            fontFamily="sans-serif" fontWeight="bold">FROZEN</text>
        </svg>
        <div>
          <div style={{ color: "#6b7280", fontSize: 24 }}>Training cutoff</div>
          <div style={{ color: "#a5b4fc", fontSize: 38, fontWeight: 700 }}>Jan 2024</div>
        </div>
        <div style={{ marginLeft: "auto" }}>
          <svg width={44} height={44} viewBox="0 0 44 44">
            <line x1="8" y1="8" x2="36" y2="36" stroke="#ef4444" strokeWidth="5" strokeLinecap="round"
              strokeDasharray={40} strokeDashoffset={40 - xProgress * 40}/>
            <line x1="36" y1="8" x2="8" y2="36" stroke="#ef4444" strokeWidth="5" strokeLinecap="round"
              strokeDasharray={40} strokeDashoffset={40 - xProgress * 40}/>
          </svg>
        </div>
      </div>

      {/* Query bubble */}
      <div style={{
        position: "absolute", top: 1080, left: 60, right: 60,
        opacity: e(128),
        transform: `translateY(${queryBounce}px)`,
      }}>
        <div style={{
          background: "#111827", border: "2px solid #374151",
          borderRadius: 16, padding: "20px 28px",
          color: "#d1d5db", fontSize: 32,
        }}>
          <span style={{ color: "#9ca3af" }}>User: </span>
          "What happened in Q1 2025?"
        </div>
        <div style={{
          marginTop: 12,
          opacity: e(155, 15),
          background: "#1f0a0a", border: "2px solid #ef4444",
          borderRadius: 16, padding: "16px 28px",
          color: "#ef4444", fontSize: 30, fontWeight: 600,
          display: "flex", alignItems: "center", gap: 12,
        }}>
          <svg width={28} height={28} viewBox="0 0 28 28">
            <circle cx="14" cy="14" r="12" fill="none" stroke="#ef4444" strokeWidth="2"/>
            <line x1="14" y1="7" x2="14" y2="16" stroke="#ef4444" strokeWidth="2.5" strokeLinecap="round"/>
            <circle cx="14" cy="21" r="1.5" fill="#ef4444"/>
          </svg>
          No knowledge of this event
        </div>
      </div>
    </AbsoluteFill>
  );
};
