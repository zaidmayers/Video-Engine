import React from "react";
import {
  useCurrentFrame,
  interpolate,
  Easing,
  AbsoluteFill,
} from "remotion";
import { fontFamily } from "../fonts";

const PARTICLES = Array.from({ length: 14 }, (_, i) => ({
  id: i,
  x: 60 + (i * 74) % 960,
  startY: 1750 - (i * 128) % 1400,
  size: 5 + (i * 6) % 16,
  color: (["#6366f1", "#22c55e", "#818cf8", "#4ade80"] as const)[i % 4],
}));

export const Scene5: React.FC = () => {
  const frame = useCurrentFrame();

  const e = (delay: number, dur = 20) =>
    interpolate(frame, [delay, delay + dur], [0, 1], {
      easing: Easing.bezier(0.16, 1, 0.3, 1),
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    });

  const up = (delay: number, dist = 40, dur = 22) =>
    interpolate(frame, [delay, delay + dur], [dist, 0], {
      easing: Easing.bezier(0.16, 1, 0.3, 1),
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    });

  const hallucinations = Math.round(
    interpolate(frame, [32, 72], [47, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })
  );
  const freshness = Math.round(
    interpolate(frame, [52, 92], [0, 100], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })
  );

  const globalParticleOp = e(0, 25);

  return (
    <AbsoluteFill style={{ background: "#0a0a0a", fontFamily }}>
      {/* Particles */}
      {PARTICLES.map(p => {
        const y = interpolate(frame, [0, 150], [p.startY, p.startY - 500], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
        });
        return (
          <div key={p.id} style={{
            position: "absolute",
            left: p.x,
            top: y,
            width: p.size * 2,
            height: p.size * 2,
            borderRadius: "50%",
            background: p.color,
            opacity: globalParticleOp * 0.22,
          }}/>
        );
      })}

      {/* Green radial glow */}
      <div style={{
        position: "absolute",
        top: 800, left: "50%",
        transform: "translateX(-50%)",
        width: 850, height: 850,
        borderRadius: "50%",
        background: "radial-gradient(circle, rgba(34,197,94,0.08) 0%, transparent 70%)",
        opacity: e(8),
      }}/>

      {/* Label */}
      <div style={{
        position: "absolute", top: 160, left: 60,
        color: "#22c55e", fontSize: 28, fontWeight: 600,
        letterSpacing: 5, textTransform: "uppercase" as const,
        opacity: e(5),
      }}>
        Why It Matters
      </div>

      {/* Headline */}
      <div style={{
        position: "absolute", top: 218, left: 60, right: 60,
        color: "#fff", fontSize: 80, fontWeight: 800, lineHeight: 1.15,
        opacity: e(8),
        transform: `translateY(${up(8)}px)`,
      }}>
        Accurate.
        <br />Current.
        <br />Grounded.
      </div>

      {/* Stat Card 1: Hallucinations */}
      <div style={{
        position: "absolute", top: 580, left: 60, right: 60,
        opacity: e(25),
        transform: `translateY(${up(25)}px)`,
        background: "#0f1628",
        border: `2px solid ${hallucinations === 0 ? "#22c55e" : "#374151"}`,
        borderRadius: 24, padding: "28px 36px",
      }}>
        <div style={{ color: "#9ca3af", fontSize: 28, fontWeight: 400, marginBottom: 6 }}>
          Hallucinations
        </div>
        <div style={{
          color: hallucinations === 0 ? "#22c55e" : "white",
          fontSize: 84, fontWeight: 800, lineHeight: 1,
          fontVariantNumeric: "tabular-nums",
        }}>
          {hallucinations === 0 ? "Zero ✓" : hallucinations}
        </div>
      </div>

      {/* Stat Card 2: Freshness */}
      <div style={{
        position: "absolute", top: 820, left: 60, right: 60,
        opacity: e(45),
        transform: `translateY(${up(45)}px)`,
        background: "#0f1628",
        border: "2px solid #374151",
        borderRadius: 24, padding: "28px 36px",
      }}>
        <div style={{ color: "#9ca3af", fontSize: 28, fontWeight: 400, marginBottom: 6 }}>
          Knowledge Freshness
        </div>
        <div style={{
          color: freshness === 100 ? "#22c55e" : "white",
          fontSize: 84, fontWeight: 800, lineHeight: 1,
          fontVariantNumeric: "tabular-nums",
        }}>
          {freshness}%
        </div>
        <div style={{
          marginTop: 16, height: 10, background: "#1f2937",
          borderRadius: 5, overflow: "hidden",
        }}>
          <div style={{
            width: `${freshness}%`, height: "100%",
            background: "linear-gradient(90deg, #6366f1, #22c55e)",
            borderRadius: 5,
          }}/>
        </div>
      </div>

      {/* Stat Card 3: Documents */}
      <div style={{
        position: "absolute", top: 1060, left: 60, right: 60,
        opacity: e(65),
        transform: `translateY(${up(65)}px)`,
        background: "#0f1628",
        border: "2px solid #374151",
        borderRadius: 24, padding: "28px 36px",
      }}>
        <div style={{ color: "#9ca3af", fontSize: 28, fontWeight: 400, marginBottom: 6 }}>
          Documents Supported
        </div>
        <div style={{
          color: "#6366f1",
          fontSize: 84, fontWeight: 800, lineHeight: 1,
          opacity: e(75, 22),
        }}>
          Unlimited ∞
        </div>
      </div>

      {/* No retraining tag */}
      <div style={{
        position: "absolute", top: 1310, left: 60, right: 60,
        opacity: e(105, 30),
        transform: `translateY(${up(105, 30)}px)`,
        background: "#052e16",
        border: "2px solid #22c55e",
        borderRadius: 16, padding: "18px 28px",
        display: "flex", alignItems: "center", gap: 16,
      }}>
        <svg width={32} height={32} viewBox="0 0 32 32">
          <circle cx="16" cy="16" r="14" fill="none" stroke="#22c55e" strokeWidth="2"/>
          <path d="M 8 16 L 13 21 L 24 10" fill="none" stroke="#22c55e" strokeWidth="2.5" strokeLinecap="round"/>
        </svg>
        <span style={{ color: "#22c55e", fontSize: 30, fontWeight: 600 }}>
          No retraining — update the index, done
        </span>
      </div>

      {/* Bottom tagline */}
      <div style={{
        position: "absolute", bottom: 185, left: 60, right: 60,
        opacity: e(120, 30),
        textAlign: "center" as const,
        color: "#6b7280", fontSize: 30, lineHeight: 1.5,
      }}>
        RAG = smarter LLMs, zero extra training cost
      </div>
    </AbsoluteFill>
  );
};
