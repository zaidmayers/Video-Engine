# Video Engine - Claude Code Instructions

Use the Remotion best practices skill.

Create an educational explainer video (1080x1920, 30fps, 30 seconds).

SAFE ZONE: All text must stay 150px from top, 170px from bottom, 60px side margins minimum.
FONT SIZES: Headlines 56px+, body 36px+, labels 28px minimum. Nothing under 28px.

STEP 1 - RESEARCH & SCRIPT: Research the topic and write a 5-scene script. Each scene needs: a one-line headline, 1-2 sentences of explanation, and a visual description. Show me the script and wait for approval before coding.

STEP 2 - DESIGN & ANIMATE: After approval, build all 5 scenes with these specs:

VISUAL STYLE:
- Background: #0a0a0a
- Primary text: white
- Accent: #6366f1 (indigo)
- Success/emphasis: #22c55e (green)
- Font: Inter (weights 400, 600, 800)
- All icons/diagrams built as SVG components (no external assets)

ANIMATION RULES:
- Every element enters with spring({ damping: 200 }), no linear motion
- Stagger related items by 8-12 frames
- Use TransitionSeries with 12-frame fade transitions between scenes
- Diagrams and flowcharts draw themselves (SVG stroke-dashoffset animation)
- Key numbers use count-up animation with interpolate() and tabular-nums
- Final scene: particle effect background (10-15 circles drifting upward)

Each scene should have a clear visual metaphor, diagrams, flowcharts, icons, or step-by-step animations. No walls of text. Think Kurzgesagt meets Fireship: dense information, beautiful motion, fast pacing.

BACKGROUND MUSIC (REQUIRED, do not skip):
- Search Pixabay for a royalty-free lo-fi or electronic beat
- If it fails, search for any free-to-use .mp3 beat online and download to public/music.mp3
- Add audio using Remotion's <Audio> component with volume set to 0.3
- Music must loop for the full video duration

REVIEW: After building, launch Remotion Studio (npx remotion studio) so I can preview in browser.