const fs = require('fs');

const appCssPath = '/home/shiro/July/脑机、人工智能导论/frontend/src/styles/app.css';
let appCss = fs.readFileSync(appCssPath, 'utf-8');

// Replace the old grid layout for spatial shell
appCss = appCss.replace(
  /\.course-spatial-shell\s*\{[^}]+\}/,
  `.course-spatial-shell {
  display: grid;
  grid-template-columns: minmax(300px, 0.35fr) minmax(760px, 1.65fr);
  gap: clamp(40px, 5vw, 80px);
  align-items: start;
  min-width: 0;
}`
);

// Add 3D container styles
appCss = appCss.replace(
  /\.course-path-stage\s*\{[^}]+\}/,
  `.course-path-stage-container {
  perspective: 1500px;
  width: 100%;
  position: relative;
  min-height: calc(100vh - var(--nav-height) - 112px);
}

.course-path-stage {
  position: relative;
  width: 100%;
  height: 100%;
  min-height: 800px;
  min-width: 0;
  transform-style: preserve-3d;
  will-change: transform;
}`
);

// Add noise overlay, SVG styles, core module badge, and vertical right text
appCss += `

/* ── New Path Details (Reference Image Overhaul) ── */
.noise-overlay {
  position: absolute;
  inset: -20%;
  pointer-events: none;
  z-index: -1;
  background-image: url('data:image/svg+xml,%3Csvg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg"%3E%3Cfilter id="noiseFilter"%3E%3CfeTurbulence type="fractalNoise" baseFrequency="0.8" numOctaves="3" stitchTiles="stitch"/%3E%3C/filter%3E%3Crect width="100%25" height="100%25" filter="url(%23noiseFilter)" opacity="0.06"/%3E%3C/svg%3E');
  transform: translateZ(-10px); /* Push behind */
}

.course-path-svg {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
  pointer-events: none;
}

.svg-path-solid {
  fill: none;
  stroke: var(--border-strong);
  stroke-width: 1.5;
}

.svg-path-dotted {
  fill: none;
  stroke: var(--border-strong);
  stroke-width: 1.5;
  stroke-dasharray: 4 6;
}

.svg-dot {
  fill: var(--text-1);
}

.blue-dot {
  display: inline-block;
  width: 10px !important;
  height: 10px !important;
  background: var(--primary) !important;
  border-radius: 50%;
  margin-left: 8px;
}

.core-module-badge {
  position: absolute;
  top: 25%;
  right: 25%;
  display: flex;
  align-items: center;
  gap: 12px;
  color: var(--primary);
  font-size: 10px;
  letter-spacing: 0.15em;
  z-index: 2;
  transform: translateZ(20px);
}

.core-module-badge .badge-line {
  width: 60px;
  height: 1px;
  background: var(--primary);
}

.core-module-badge .badge-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--primary);
}

.vertical-rail-right {
  position: absolute;
  right: -40px;
  top: 20%;
  display: grid;
  gap: 20px;
  justify-items: center;
  color: var(--text-1);
  font-family: var(--font-mono);
  font-size: 10px;
  letter-spacing: 0.14em;
  writing-mode: vertical-rl;
  z-index: 2;
  transform: translateZ(10px);
}

.vertical-rail-right .num {
  font-size: 14px;
  transform: rotate(90deg);
  margin-bottom: 20px;
}

.vertical-rail-right .text {
  color: var(--text-3);
  text-transform: uppercase;
}

.vertical-rail-right .dots {
  display: grid;
  gap: 8px;
  margin-top: 40px;
}

.vertical-rail-right .dots i {
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: var(--border-strong);
}

/* Update node positions to perfectly align with the new SVG curve */
.path-node-1 { top: 9%; left: 16%; width: 340px; }
.path-node-2 { top: 21%; left: 52%; width: 380px; }
.path-node-3 { top: 38%; left: 24%; width: 360px; }
.path-node-4 { top: 52%; left: 62%; width: 350px; }
.path-node-5 { top: 73%; left: 38%; width: 400px; }

`;

fs.writeFileSync(appCssPath, appCss);
console.log('app.css updated');
