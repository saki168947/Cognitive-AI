<script setup>
import { computed } from 'vue';
import { RouterLink, useRoute } from 'vue-router';
import { useWindowScroll } from '@vueuse/core';

const route = useRoute();
const { y: scrollY } = useWindowScroll({ behavior: 'smooth' });

const isElevated = computed(() => scrollY.value > 48);
const isAtTop = computed(() => scrollY.value < 12);

const navLinks = [
  { to: '/', label: '工作台', match: (r) => r.name === 'dashboard' },
  { to: '/courses/ai-intro', label: '课程工作区', match: (r) => r.name === 'course' },
  { to: '/teacher', label: '教师工作室', match: (r) => r.name === 'teacher' }
];

function isActive(link) {
  return link.match(route);
}
</script>

<template>
  <div class="shell-root" :data-scrolled="!isAtTop">
    <header
      class="nav"
      :data-elevated="isElevated"
      :data-translucent="!isAtTop"
    >
      <div class="shell-container nav-inner">
        <RouterLink to="/" class="brand-mark" aria-label="Cognitive AI home">
          <span class="brand-glyph" aria-hidden="true">
            <span class="brand-glyph-core"></span>
            <span class="brand-glyph-ring"></span>
          </span>
          <span class="brand-text">
            <span class="brand-name">认知智能教学平台</span>
            <span class="brand-suffix">Course Studio</span>
          </span>
        </RouterLink>

        <nav class="nav-links" aria-label="Primary">
          <RouterLink
            v-for="link in navLinks"
            :key="link.to"
            :to="link.to"
            class="nav-link"
            :data-active="isActive(link)"
          >
            <span class="nav-link-label">{{ link.label }}</span>
            <span class="nav-link-glow" aria-hidden="true"></span>
          </RouterLink>
        </nav>

        <div class="nav-trailing">
          <span class="workspace-pill mono">MVP</span>
          <span class="user-pill" aria-label="已登录">
            <span class="user-pill-avatar" aria-hidden="true">SH</span>
          </span>
        </div>
      </div>

      <span class="nav-edge" aria-hidden="true"></span>
    </header>

    <main class="shell-main">
      <slot />
    </main>
  </div>
</template>

<style scoped>
.shell-root {
  position: relative;
  min-height: 100vh;
}

.nav {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 50;
  height: var(--nav-height);
  display: flex;
  align-items: center;
  background: transparent;
  transition:
    background var(--dur-3) var(--ease-out-expo),
    backdrop-filter var(--dur-3) var(--ease-out-expo),
    border-color var(--dur-3) var(--ease-out-expo);
}

.nav[data-translucent="true"] {
  background: rgba(8, 8, 13, 0.55);
  backdrop-filter: var(--nav-blur);
  -webkit-backdrop-filter: var(--nav-blur);
}

.nav[data-elevated="true"] {
  background: rgba(8, 8, 13, 0.78);
}

.nav-edge {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  height: 1px;
  background: linear-gradient(
    90deg,
    transparent,
    var(--line-medium) 20%,
    var(--line-medium) 80%,
    transparent
  );
  opacity: 0;
  transition: opacity var(--dur-3) var(--ease-out-expo);
}

.nav[data-translucent="true"] .nav-edge {
  opacity: 1;
}

.nav-inner {
  display: flex;
  align-items: center;
  gap: var(--space-7);
  height: 100%;
}

.brand-mark {
  display: inline-flex;
  align-items: center;
  gap: 12px;
  color: var(--text-1);
  transition: opacity var(--dur-2) var(--ease-out-expo);
}

.brand-mark:hover {
  opacity: 0.85;
}

.brand-glyph {
  position: relative;
  width: 26px;
  height: 26px;
  display: inline-grid;
  place-items: center;
}

.brand-glyph-core {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--accent-cyan), var(--accent-violet));
  box-shadow: 0 0 18px var(--accent-cyan-glow);
  z-index: 2;
}

.brand-glyph-ring {
  position: absolute;
  inset: 0;
  border-radius: 50%;
  border: 1px solid var(--line-strong);
  background:
    conic-gradient(
      from 0deg,
      var(--accent-cyan),
      var(--accent-violet),
      var(--accent-cyan)
    );
  -webkit-mask:
    radial-gradient(circle, transparent 9px, black 10px);
          mask:
    radial-gradient(circle, transparent 9px, black 10px);
  animation: brand-spin 14s linear infinite;
}

@keyframes brand-spin {
  to { transform: rotate(360deg); }
}

.brand-text {
  display: inline-flex;
  align-items: baseline;
  gap: 8px;
  font-family: var(--font-display);
  font-weight: 700;
  font-size: 14px;
  letter-spacing: 0;
}

.brand-suffix {
  font-family: var(--font-mono);
  font-weight: 400;
  font-size: 12px;
  color: var(--text-3);
  letter-spacing: 0;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-left: auto;
  margin-right: auto;
}

.nav-link {
  position: relative;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  height: 36px;
  padding: 0 14px;
  border-radius: var(--radius-full);
  color: var(--text-2);
  font-size: 13.5px;
  font-weight: 500;
  letter-spacing: 0;
  transition:
    color var(--dur-2) var(--ease-out-expo),
    background var(--dur-2) var(--ease-out-expo),
    transform var(--dur-2) var(--ease-out-expo);
  cursor: pointer;
}

.nav-link:hover {
  color: var(--text-1);
  background: rgba(255, 255, 255, 0.04);
}

.nav-link[data-active="true"],
.nav-link .course-switcher-trigger[data-active="true"] {
  color: var(--text-1);
}

.nav-link[data-active="true"]::after {
  content: "";
  position: absolute;
  left: 50%;
  bottom: -10px;
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: var(--accent-cyan);
  box-shadow: 0 0 12px var(--accent-cyan-glow);
  transform: translateX(-50%);
}

.nav-link-label {
  position: relative;
  z-index: 1;
}

.nav-link-glow {
  position: absolute;
  inset: 0;
  border-radius: inherit;
  pointer-events: none;
  opacity: 0;
  background: radial-gradient(
    120px 60px at var(--mx, 50%) var(--my, 50%),
    var(--accent-cyan-soft),
    transparent 70%
  );
  transition: opacity var(--dur-2) var(--ease-out-expo);
}

.nav-link:hover .nav-link-glow {
  opacity: 1;
}

.course-switcher {
  position: relative;
  padding: 0;
}

.course-switcher-trigger {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  height: 36px;
  padding: 0 14px;
  border-radius: var(--radius-full);
  color: inherit;
  font: inherit;
  letter-spacing: inherit;
  cursor: pointer;
  position: relative;
}

.course-switcher-trigger .caret {
  width: 10px;
  height: 10px;
  color: var(--text-3);
  transition: transform var(--dur-2) var(--ease-out-expo);
}

.course-switcher-trigger[aria-expanded="true"] .caret {
  transform: rotate(180deg);
  color: var(--text-1);
}

.course-menu {
  position: absolute;
  top: calc(100% + 12px);
  left: 50%;
  transform: translateX(-50%);
  min-width: 280px;
  padding: 12px;
  border-radius: var(--radius-md);
  background: linear-gradient(180deg, rgba(28, 28, 43, 0.96), rgba(13, 13, 21, 0.96));
  box-shadow:
    var(--shadow-lg),
    var(--inner-edge),
    var(--inner-gloss);
  backdrop-filter: var(--nav-blur);
  -webkit-backdrop-filter: var(--nav-blur);
}

.course-menu::before {
  content: "";
  position: absolute;
  top: -6px;
  left: 50%;
  width: 12px;
  height: 12px;
  background: rgba(28, 28, 43, 0.96);
  border-left: 1px solid var(--line-medium);
  border-top: 1px solid var(--line-medium);
  transform: translateX(-50%) rotate(45deg);
}

.course-menu-kicker {
  margin: 4px 8px 8px;
  display: block;
}

.course-menu-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 2px;
}

.course-menu-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 10px;
  border-radius: var(--radius-sm);
  color: var(--text-2);
  font-size: 13.5px;
  transition:
    background var(--dur-1) var(--ease-out-expo),
    color var(--dur-1) var(--ease-out-expo),
    transform var(--dur-2) var(--ease-out-expo);
}

.course-menu-item:hover {
  background: rgba(255, 255, 255, 0.04);
  color: var(--text-1);
  transform: translateX(2px);
}

.course-menu-item[data-active="true"] {
  background: var(--accent-cyan-soft);
  color: var(--accent-cyan);
}

.course-menu-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--accent-cyan), var(--accent-violet));
  flex: 0 0 auto;
  box-shadow: 0 0 8px var(--accent-cyan-glow);
}

.course-menu-title {
  flex: 1 1 auto;
  font-weight: 500;
}

.course-menu-arrow {
  color: var(--text-4);
  font-family: var(--font-mono);
  font-size: 12px;
  transition: transform var(--dur-2) var(--ease-out-expo), color var(--dur-2) var(--ease-out-expo);
}

.course-menu-item:hover .course-menu-arrow {
  color: var(--accent-cyan);
  transform: translateX(3px);
}

.course-menu-empty {
  padding: 12px 10px;
  color: var(--text-4);
  font-size: 13px;
  text-align: center;
}

.menu-enter-active,
.menu-leave-active {
  transition:
    opacity var(--dur-2) var(--ease-out-expo),
    transform var(--dur-3) var(--ease-spring);
  transform-origin: top center;
}

.menu-enter-from,
.menu-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(-6px) scale(0.96);
}

.nav-trailing {
  display: flex;
  align-items: center;
  gap: 12px;
}

.workspace-pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  height: 36px;
  min-width: 54px;
  padding: 0 12px;
  border-radius: var(--radius-full);
  background: rgba(94, 234, 212, 0.08);
  box-shadow: inset 0 0 0 1px rgba(94, 234, 212, 0.18);
  color: var(--accent-cyan);
  font-size: 11px;
  font-weight: 600;
}

.user-pill {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--ink-5), var(--ink-3));
  box-shadow: var(--inner-edge), var(--shadow-sm);
  display: inline-grid;
  place-items: center;
  cursor: pointer;
  transition: transform var(--dur-2) var(--ease-out-expo);
}

.user-pill:hover {
  transform: translateY(-1px) scale(1.05);
}

.user-pill-avatar {
  font-family: var(--font-mono);
  font-size: 11px;
  font-weight: 600;
  color: var(--text-2);
  letter-spacing: 0.04em;
}

.shell-main {
  min-height: 100vh;
}

@media (max-width: 880px) {
  .nav-link:not(.course-switcher),
  .brand-suffix {
    display: none;
  }

  .nav-inner {
    gap: var(--space-3);
  }
}

@media (max-width: 560px) {
  .course-switcher {
    display: none;
  }
}
</style>
