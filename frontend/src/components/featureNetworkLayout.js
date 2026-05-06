function mulberry32(seed) {
  let t = seed >>> 0;
  return function next() {
    t += 0x6d2b79f5;
    let r = Math.imul(t ^ (t >>> 15), 1 | t);
    r ^= r + Math.imul(r ^ (r >>> 7), 61 | r);
    return ((r ^ (r >>> 14)) >>> 0) / 4294967296;
  };
}

function jitter(rand, amount) {
  return (rand() - 0.5) * amount;
}

function distance(a, b) {
  return Math.hypot(a.x - b.x, a.y - b.y);
}

function addEdge(edges, seen, source, target, weight = 1) {
  if (source === target) return;
  const a = Math.min(source, target);
  const b = Math.max(source, target);
  const key = `${a}-${b}`;
  if (seen.has(key)) return;
  seen.add(key);
  edges.push({ source: a, target: b, weight });
}

export function createReferenceNetworkLayout({ seed = 1 } = {}) {
  const rand = mulberry32(seed);
  const nodes = [];
  const hullIndices = [];

  for (let i = 0; i < 48; i++) {
    const angle = (i / 48) * Math.PI * 2;
    const radiusJitter = 1 + jitter(rand, 0.18);
    const x = Math.cos(angle) * 3.25 * radiusJitter + jitter(rand, 0.3);
    const y = Math.sin(angle) * 3.25 * radiusJitter + jitter(rand, 0.3);
    hullIndices.push(nodes.length);
    nodes.push({
      x,
      y,
      z: jitter(rand, 0.012),
      size: rand() > 0.68 ? "large" : "medium",
      role: "hull",
    });
  }

  const clusters = [
    { x: -0.8, y: 0.35, rx: 2.15, ry: 1.55, count: 48 },
    { x: 0.95, y: 0.6,  rx: 2.0,  ry: 1.35, count: 40 },
    { x: -1.55, y: -1.2, rx: 1.75, ry: 1.15, count: 32 },
    { x: 1.85, y: -0.9,  rx: 1.45, ry: 1.1,  count: 28 },
    { x: 0.0,  y: 1.8,   rx: 1.65, ry: 1.0,  count: 24 },
    { x: -0.3, y: -0.3,  rx: 1.4,  ry: 1.2,  count: 22 },
  ];

  for (const cluster of clusters) {
    for (let i = 0; i < cluster.count; i++) {
      const angle = rand() * Math.PI * 2;
      const radius = Math.pow(rand(), 0.56);
      nodes.push({
        x:
          cluster.x +
          Math.cos(angle) * cluster.rx * radius +
          jitter(rand, 0.12),
        y:
          cluster.y +
          Math.sin(angle) * cluster.ry * radius +
          jitter(rand, 0.12),
        z: jitter(rand, 0.012),
        size: rand() > 0.9 ? "medium" : "small",
        role: "interior",
      });
    }
  }

  const focusIndex = nodes.length;
  // 焦点放在团块的几何中心（略偏上），让蓝色光晕成为整团网络的视觉重心
  nodes.push({ x: 0.1, y: 0.2, z: 0.01, size: "focus", role: "focus" });

  const faintEdges = [];
  const faintSeen = new Set();
  // More neighbours + looser thresholds → denser triangulation matching the design
  const nearestCount = 12;
  for (let i = 0; i < nodes.length; i++) {
    const nearest = nodes
      .map((node, index) => ({
        index,
        d: index === i ? Infinity : distance(nodes[i], node),
      }))
      .sort((a, b) => a.d - b.d)
      .slice(0, nearestCount);
    for (const item of nearest) {
      if (item.d < 1.8 || (item.d < 2.5 && rand() > 0.5)) {
        addEdge(
          faintEdges,
          faintSeen,
          i,
          item.index,
          0.2 + Math.max(0, 1.1 - item.d) * 0.1,
        );
      }
    }
  }

  const majorEdges = [];
  const majorSeen = new Set();

  // 主干只保留 hub→anchor 与 hub↔hub 的辐射结构，避免外圈节点形成
  // 视觉上的硬质多边形外框，让网络看起来像一个延展开的智能体而非笼子。
  const anchors = [24, 20, 8, 31, 40, 0].map((i) => hullIndices[i % hullIndices.length]);
  const hubs = [54, 72, 96, 130, 160, focusIndex].filter(
    (i) => i < nodes.length,
  );
  for (let i = 0; i < hubs.length; i++) {
    addEdge(majorEdges, majorSeen, hubs[i], anchors[i % anchors.length], 1);
  }
  addEdge(majorEdges, majorSeen, hubs[0], hubs[1], 1);
  addEdge(majorEdges, majorSeen, hubs[2], hubs[3], 1);
  addEdge(majorEdges, majorSeen, hubs[4], focusIndex, 1);

  // 焦点居中后，蓝色辐射线选取与团块半径相当的远端目标，保持线长统一感
  const remoteTargets = nodes
    .map((node, index) => ({
      index,
      d: distance(nodes[focusIndex], node),
    }))
    .filter(
      (item) =>
        item.index !== focusIndex &&
        item.d > 2.5 &&
        item.d < 5.0,
    )
    .sort((a, b) => Math.abs(a.d - 3.4) - Math.abs(b.d - 3.4))
    .slice(0, 5);
  const blueEdges = remoteTargets.map((item) => ({
    source: focusIndex,
    target: item.index,
    weight: item.d,
  }));

  return {
    nodes,
    faintEdges,
    majorEdges,
    blueEdges,
    focusIndex,
    labels: [],
  };
}
