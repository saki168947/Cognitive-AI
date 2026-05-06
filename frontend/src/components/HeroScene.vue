<script setup>
import { onMounted, onBeforeUnmount, ref } from 'vue';
import * as THREE from 'three';
import { useWindowScroll, useMouse, useWindowSize } from '@vueuse/core';

const props = defineProps({
  density: {
    type: Number,
    default: 1
  }
});

const canvas = ref(null);
const { y: scrollY } = useWindowScroll();
const { x: mouseX, y: mouseY } = useMouse({ touch: false });
const { width: winW, height: winH } = useWindowSize();

let renderer = null;
let scene = null;
let camera = null;
let raf = null;
let nodeGroup = null;
let edgeGroup = null;
let particles = null;
let ambient = null;
let cyanLight = null;
let violetLight = null;
let resizeObserver = null;
let prefersReducedMotion = false;

const targetCamZ = { value: 0 };
const targetRotX = { value: 0 };
const targetRotY = { value: 0 };

function buildScene() {
  scene = new THREE.Scene();
  scene.background = null; // Transparent to let the white page show through
  scene.fog = new THREE.FogExp2(0xffffff, 0.035);

  camera = new THREE.PerspectiveCamera(
    52,
    canvas.value.clientWidth / canvas.value.clientHeight,
    0.1,
    100
  );
  camera.position.set(0, 0, 18);

  ambient = new THREE.AmbientLight(0xffffff, 0.8);
  scene.add(ambient);

  cyanLight = new THREE.PointLight(0x0022ff, 50, 50, 1.6);
  cyanLight.position.set(-10, 6, 8);
  scene.add(cyanLight);

  violetLight = new THREE.PointLight(0x000000, 30, 50, 1.6);
  violetLight.position.set(10, -4, 6);
  scene.add(violetLight);

  const rim = new THREE.DirectionalLight(0xffffff, 0.18);
  rim.position.set(0, 10, -6);
  scene.add(rim);

  buildGraph();
  buildParticles();
}

function buildGraph() {
  nodeGroup = new THREE.Group();
  edgeGroup = new THREE.Group();

  const nodes = [];
  const NODE_COUNT = Math.round(18 * props.density);

  const nodeMaterial = new THREE.MeshStandardMaterial({
    color: 0xcccccc,
    metalness: 0.1,
    roughness: 0.8,
    flatShading: true
  });

  const accentMaterial = new THREE.MeshStandardMaterial({
    color: 0x0022ff,
    metalness: 0.2,
    roughness: 0.6,
    flatShading: true
  });

  const violetMaterial = new THREE.MeshStandardMaterial({
    color: 0x000000,
    metalness: 0.1,
    roughness: 0.9,
    flatShading: true
  });

  const goldenAngle = Math.PI * (3 - Math.sqrt(5));

  for (let i = 0; i < NODE_COUNT; i += 1) {
    const t = i / NODE_COUNT;
    const radius = 7.5 + Math.sin(i * 0.9) * 1.6;
    const phi = Math.acos(1 - 2 * t);
    const theta = goldenAngle * i;

    const x = radius * Math.sin(phi) * Math.cos(theta);
    const y = radius * Math.sin(phi) * Math.sin(theta) * 0.7;
    const z = radius * Math.cos(phi) * 0.6 - 2;

    const isAccent = i % 5 === 0;
    const isViolet = i % 5 === 2;
    const sizeBase = isAccent ? 0.55 : 0.32;
    const size = sizeBase + Math.random() * 0.12;

    const detail = isAccent ? 1 : 0;
    const geometry = new THREE.IcosahedronGeometry(size, detail);

    const material = isAccent
      ? accentMaterial
      : isViolet
        ? violetMaterial
        : nodeMaterial;

    const mesh = new THREE.Mesh(geometry, material);
    mesh.position.set(x, y, z);
    mesh.userData = {
      basePos: new THREE.Vector3(x, y, z),
      pulsePhase: Math.random() * Math.PI * 2,
      pulseSpeed: 0.4 + Math.random() * 0.6,
      rotateSpeed: (Math.random() - 0.5) * 0.4
    };
    nodeGroup.add(mesh);
    nodes.push(mesh);
  }

  const edgePositions = [];
  for (let i = 0; i < nodes.length; i += 1) {
    const candidates = [];
    for (let j = i + 1; j < nodes.length; j += 1) {
      const dist = nodes[i].position.distanceTo(nodes[j].position);
      if (dist < 4.6) {
        candidates.push({ j, dist });
      }
    }
    candidates.sort((a, b) => a.dist - b.dist);
    const keep = candidates.slice(0, 2);
    for (const { j } of keep) {
      const a = nodes[i].position;
      const b = nodes[j].position;
      edgePositions.push(a.x, a.y, a.z, b.x, b.y, b.z);
    }
  }

  const edgeGeometry = new THREE.BufferGeometry();
  edgeGeometry.setAttribute(
    'position',
    new THREE.Float32BufferAttribute(edgePositions, 3)
  );
  const edgeMaterial = new THREE.LineBasicMaterial({
    color: 0x000000,
    transparent: true,
    opacity: 0.1
  });
  const edges = new THREE.LineSegments(edgeGeometry, edgeMaterial);
  edgeGroup.add(edges);

  scene.add(edgeGroup);
  scene.add(nodeGroup);
}

function buildParticles() {
  const COUNT = 220;
  const positions = new Float32Array(COUNT * 3);
  for (let i = 0; i < COUNT; i += 1) {
    positions[i * 3 + 0] = (Math.random() - 0.5) * 60;
    positions[i * 3 + 1] = (Math.random() - 0.5) * 36;
    positions[i * 3 + 2] = (Math.random() - 0.5) * 30 - 6;
  }

  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));

  const material = new THREE.PointsMaterial({
    color: 0xc9cad6,
    size: 0.04,
    transparent: true,
    opacity: 0.35,
    blending: THREE.AdditiveBlending,
    depthWrite: false
  });
  particles = new THREE.Points(geometry, material);
  scene.add(particles);
}

function setSize() {
  if (!canvas.value || !renderer || !camera) return;
  const w = canvas.value.clientWidth;
  const h = canvas.value.clientHeight;
  renderer.setSize(w, h, false);
  camera.aspect = w / h;
  camera.updateProjectionMatrix();
}

function tick(now) {
  raf = requestAnimationFrame(tick);
  if (!scene || !renderer || !camera) return;

  const t = now * 0.001;

  const scrollProgress = Math.min(1, scrollY.value / Math.max(winH.value * 0.9, 1));
  targetCamZ.value = 18 - scrollProgress * 9;

  const mxN = (mouseX.value / Math.max(winW.value, 1) - 0.5) * 2;
  const myN = (mouseY.value / Math.max(winH.value, 1) - 0.5) * 2;
  targetRotY.value = mxN * 0.18;
  targetRotX.value = -myN * 0.12;

  camera.position.z += (targetCamZ.value - camera.position.z) * 0.06;

  if (nodeGroup && edgeGroup) {
    const damp = prefersReducedMotion ? 0 : 0.05;
    nodeGroup.rotation.y += (targetRotY.value + t * 0.04 - nodeGroup.rotation.y) * damp;
    nodeGroup.rotation.x += (targetRotX.value - nodeGroup.rotation.x) * damp;
    edgeGroup.rotation.copy(nodeGroup.rotation);

    if (!prefersReducedMotion) {
      for (const node of nodeGroup.children) {
        const data = node.userData;
        const pulse = 1 + Math.sin(t * data.pulseSpeed + data.pulsePhase) * 0.06;
        node.scale.setScalar(pulse);
        node.rotation.x += data.rotateSpeed * 0.005;
        node.rotation.y += data.rotateSpeed * 0.004;
        node.position.y = data.basePos.y + Math.sin(t * 0.6 + data.pulsePhase) * 0.12;
      }
    }
  }

  if (particles && !prefersReducedMotion) {
    particles.rotation.y = t * 0.02;
  }

  if (cyanLight) {
    cyanLight.position.x = Math.cos(t * 0.3) * 12;
    cyanLight.position.z = Math.sin(t * 0.3) * 8 + 4;
  }
  if (violetLight) {
    violetLight.position.x = Math.cos(t * 0.3 + Math.PI) * 12;
    violetLight.position.z = Math.sin(t * 0.3 + Math.PI) * 8 + 4;
  }

  renderer.render(scene, camera);
}

onMounted(() => {
  prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  renderer = new THREE.WebGLRenderer({
    canvas: canvas.value,
    alpha: true,
    antialias: true,
    powerPreference: 'high-performance'
  });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.05;

  buildScene();
  setSize();

  resizeObserver = new ResizeObserver(setSize);
  resizeObserver.observe(canvas.value);

  raf = requestAnimationFrame(tick);
});

onBeforeUnmount(() => {
  if (raf) cancelAnimationFrame(raf);
  if (resizeObserver) resizeObserver.disconnect();
  if (renderer) {
    renderer.dispose();
  }
  if (scene) {
    scene.traverse((obj) => {
      if (obj.geometry) obj.geometry.dispose();
      if (obj.material) {
        if (Array.isArray(obj.material)) {
          obj.material.forEach((m) => m.dispose());
        } else {
          obj.material.dispose();
        }
      }
    });
  }
});
</script>

<template>
  <canvas ref="canvas" class="hero-scene" aria-hidden="true"></canvas>
</template>

<style scoped>
.hero-scene {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  display: block;
  pointer-events: none;
}
</style>
