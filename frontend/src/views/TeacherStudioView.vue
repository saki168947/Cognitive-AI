<template>
  <div class="teacher-studio-view">
    <!-- Top Hero Section replicating the avant-garde design -->
    <section class="studio-hero">
      <!-- Left side: Upload Form & Progress -->
      <div class="hero-left">
        <header class="hero-header">
          <span class="indicator mono">TEACHER STUDIO <span class="dot"></span></span>
        </header>

        <!-- Giant watermark percentage -->
        <div class="watermark-percent" aria-hidden="true">{{ uploading ? uploadProgress : '—' }}</div>

        <div class="upload-content">
          <div class="process-tag mono">PROCESS ID: 08-X21</div>
          <h1 class="upload-title display">Upload</h1>
          <p class="upload-desc">Drop your files here<br>and we'll take it from there.</p>

          <form v-if="!uploading" class="upload-form" @submit.prevent="submitUpload">
            <div class="form-row">
              <label class="custom-select mono">
                <select v-model="selectedCourseId">
                  <option v-if="courses.length === 0" value="ai-intro">人工智能导论 (AI INTRO)</option>
                  <option v-for="course in courses" :key="course.id" :value="course.id">
                    {{ course.title || course.name || course.id }}
                  </option>
                </select>
              </label>
            </div>

            <div class="file-drop-area mono" @click="triggerFileInput" :class="{ 'has-file': selectedFile }">
              <input ref="fileInput" type="file" class="hidden-input" @change="selectFile" />
              <span v-if="selectedFile">{{ selectedFile.name }}</span>
              <span v-else>SELECT OR DROP FILE</span>
            </div>

            <button type="submit" class="btn-upload mono" :disabled="uploadDisabled">UPLOAD →</button>
            <p v-if="message" class="status-msg success mono">{{ message }}</p>
            <p v-if="error" class="status-msg error mono">{{ error }}</p>
          </form>

          <div v-else class="upload-progress-container">
            <div class="file-info mono">
              <span class="dot"></span> {{ selectedFile?.name || 'LESSON_PLAN.pdf' }} <span class="size">{{ formatBytes(selectedFile?.size) || '12.4 MB' }}</span> <span class="status-label">UPLOADING</span>
            </div>
            <div class="big-percent display">{{ uploadProgress }}%</div>
            <div class="dashed-loader">
              <span class="dash"></span><span class="dash"></span><span class="dash"></span><span class="dash short"></span><span class="dash short"></span>
            </div>
            <div class="subtext mono">Preparing content analysis...</div>
          </div>
        </div>

        <footer class="hero-footer mono">
          <button v-if="uploading" type="button" class="btn-cancel" @click="cancelUpload">ESC &nbsp;&nbsp;CANCEL UPLOAD</button>
        </footer>
      </div>

      <!-- Right side: Live Processing Queue -->
      <div class="hero-right">
        <header class="hero-header-right">
          <span class="indicator mono"><span class="dot"></span> LIVE PROCESSING QUEUE</span>
        </header>

        <div class="network-container">
          <!-- Ambient instrument readouts -->
          <span class="ambient-readout ar-tl">SYS.OK / T+00:42:17</span>
          <span class="ambient-readout ar-tr">42.3611°N 71.0578°W</span>
          <span class="ambient-readout ar-bl">SCALE 1:2048 RES 0.01μm</span>
          <span class="ambient-readout ar-br">COGNITIVE.OS v4.2.1</span>

          <div class="network-stage" aria-hidden="true">
            <img src="/neural-network.jpg" alt="" class="network-image" />
          </div>

          <!-- Annotations (visible when uploading) -->
          <div class="annotations" :class="{ active: uploading }">
            <div class="annotation a-file mono">
              <div class="label">FILE</div>
              <div class="val">{{ selectedFile?.name || 'LESSON_PLAN.pdf' }}<br>{{ formatBytes(selectedFile?.size) || '12.4 MB' }}</div>
              <div class="pointer-line"></div>
              <div class="pointer-dot"></div>
            </div>

            <div class="annotation a-data mono">
              <div class="label">DATA CHUNK</div>
              <div class="val">{{ Math.floor(uploadProgress * 230) }} / 23,084</div>
              <div class="pointer-line"></div>
              <div class="pointer-dot"></div>
            </div>

            <div class="annotation a-status mono">
              <div class="label">STATUS</div>
              <div class="val">UPLOADING<br>{{ uploadProgress }}%</div>
              <div class="pointer-line"></div>
              <div class="pointer-dot"></div>
            </div>

            <div class="annotation a-eta mono">
              <div class="label">ETA</div>
              <div class="val">00:00:{{ String(Math.max(0, 18 - Math.floor(uploadProgress / 5))).padStart(2, '0') }}</div>
              <div class="pointer-line"></div>
              <div class="pointer-dot"></div>
            </div>

            <!-- Center glow is now rendered by Three.js sprite -->
          </div>
        </div>
      </div>
    </section>

    <!-- Review Queue Section -->
    <section class="review-section container">
      <div class="review-toolbar">
        <div>
          <p class="kicker mono">QUEUE</p>
          <h2>审核条目</h2>
        </div>
        <button type="button" class="btn btn-outline btn-sm" :disabled="itemsLoading" @click="loadReviewItems">
          刷新队列
        </button>
      </div>

      <div v-if="itemsLoading" class="panel">
        <p class="status-message mono">正在加载审核条目…</p>
      </div>
      <ReviewQueue
        v-else
        :items="reviewItems"
        :pending-ids="pendingReviewIds"
        @approve="approveItem"
        @reject="rejectItem"
        @publish="publishItem"
      />
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue';
import { listCourses } from '../api/courses';
import { uploadMaterial } from '../api/materials';
import {
  approveReviewItem,
  listReviewItems,
  publishReviewItem,
  rejectReviewItem
} from '../api/review';
import ReviewQueue from '../components/ReviewQueue.vue';
import { createReviewActionTracker, reviewItemCreatedMessage } from './teacherStudioState';

const fallbackCourseId = 'ai-intro';

const courses = ref([]);
const reviewItems = ref([]);
const selectedCourseId = ref(fallbackCourseId);
const selectedFile = ref(null);
const fileInput = ref(null);
const coursesLoading = ref(false);
const itemsLoading = ref(false);
const uploading = ref(false);
const uploadProgress = ref(0);
let progressInterval = null;
const error = ref('');
const message = ref('');
const pendingReviewIds = ref([]);
const reviewActionTracker = createReviewActionTracker();
let reviewRequestId = 0;

const uploadDisabled = computed(() => !selectedCourseId.value || !selectedFile.value || uploading.value);

onMounted(() => {
  loadCourses();
  loadReviewItems();
});

function formatBytes(bytes, decimals = 1) {
  if (!bytes) return '0 Bytes';
  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

async function loadCourses() {
  coursesLoading.value = true;
  error.value = '';

  try {
    const result = await listCourses();
    courses.value = Array.isArray(result) ? result : [];
    const selectedCourseExists = courses.value.some((course) => course.id === selectedCourseId.value);
    if (courses.value.length > 0 && (selectedCourseId.value === fallbackCourseId || !selectedCourseExists)) {
      selectedCourseId.value = courses.value[0].id;
    }
  } catch (caughtError) {
    courses.value = [];
    error.value = caughtError?.message || '无法加载课程。';
  } finally {
    coursesLoading.value = false;
  }
}

async function loadReviewItems() {
  const requestId = reviewRequestId + 1;
  reviewRequestId = requestId;
  itemsLoading.value = true;
  error.value = '';

  try {
    const result = await listReviewItems();
    if (requestId === reviewRequestId) {
      reviewItems.value = Array.isArray(result) ? result : [];
    }
  } catch (caughtError) {
    if (requestId === reviewRequestId) {
      reviewItems.value = [];
      error.value = caughtError?.message || '无法加载审核条目。';
    }
  } finally {
    if (requestId === reviewRequestId) {
      itemsLoading.value = false;
    }
  }
}

function triggerFileInput() {
  if (fileInput.value) {
    fileInput.value.click();
  }
}

function selectFile(event) {
  selectedFile.value = event.target.files?.[0] || null;
}

function cancelUpload() {
  // Simulate abort
  uploading.value = false;
  uploadProgress.value = 0;
  if (progressInterval) clearInterval(progressInterval);
}

async function submitUpload() {
  if (uploadDisabled.value) {
    return;
  }

  uploading.value = true;
  uploadProgress.value = 0;
  error.value = '';
  message.value = '';

  // Simulate upload progress
  progressInterval = setInterval(() => {
    if (uploadProgress.value < 90) {
      uploadProgress.value += Math.floor(Math.random() * 8) + 2;
    }
  }, 400);

  try {
    const created = await uploadMaterial(selectedCourseId.value, selectedFile.value);
    uploadProgress.value = 100;
    if (progressInterval) clearInterval(progressInterval);

    // Wait a brief moment at 100% before resetting
    await new Promise(r => setTimeout(r, 600));

    message.value = reviewItemCreatedMessage(created);
    selectedFile.value = null;
    if (fileInput.value) {
      fileInput.value.value = '';
    }
    uploading.value = false;
    uploadProgress.value = 0;

    await loadReviewItems();
  } catch (caughtError) {
    if (progressInterval) clearInterval(progressInterval);
    uploading.value = false;
    uploadProgress.value = 0;
    error.value = caughtError?.message || '无法上传材料。';
  }
}

async function approveItem(id) {
  await runReviewAction({ id, run: () => approveReviewItem(id) });
}

async function rejectItem(id) {
  await runReviewAction({ id, run: () => rejectReviewItem(id) });
}

async function publishItem(id) {
  await runReviewAction({ id, run: () => publishReviewItem(id) });
}

async function runReviewAction(action) {
  if (!reviewActionTracker.start(action.id)) {
    return;
  }
  pendingReviewIds.value = [...pendingReviewIds.value, action.id];
  error.value = '';
  message.value = '';

  try {
    await action.run();
    await loadReviewItems();
  } catch (caughtError) {
    error.value = caughtError?.message || '无法更新审核条目。';
  } finally {
    reviewActionTracker.finish(action.id);
    pendingReviewIds.value = pendingReviewIds.value.filter((id) => id !== action.id);
  }
}
</script>

<style scoped>
.teacher-studio-view {
  min-height: 100vh;
  background: var(--surface-0);
  color: var(--text-1);
  display: flex;
  flex-direction: column;
}

/* ══════ Hero Section (Split Layout) ══════ */
.studio-hero {
  display: grid;
  grid-template-columns: 30% 70%;
  grid-template-rows: 1fr;
  height: 100vh;
  padding-top: var(--nav-height);
  box-sizing: border-box;
}

.hero-left {
  padding: 40px 24px 40px clamp(32px, 3vw, 48px);
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
}

.hero-right {
  position: relative;
  display: flex;
  flex-direction: column;
  background: #ffffff;
  overflow: hidden;
  min-height: calc(92vh - var(--nav-height));
}

.hero-header-right {
  position: absolute;
  top: calc(var(--nav-height) + 16px);
  left: 50%;
  transform: translateX(-50%);
  z-index: 10;
  white-space: nowrap;
}

.indicator {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  font-size: 9px;
  font-weight: 700;
  letter-spacing: 0.2em;
  color: var(--text-1);
}

.indicator .dot {
  width: 5px;
  height: 5px;
  background: var(--text-1);
  border-radius: 50%;
}

/* ══════ Giant Watermark ══════ */
.watermark-percent {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: clamp(10rem, 20vw, 18rem);
  font-weight: 300;
  color: rgba(0, 0, 0, 0.03);
  line-height: 1;
  letter-spacing: -0.04em;
  pointer-events: none;
  user-select: none;
  z-index: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
}

/* ══════ Process tag (排版冲突) ══════ */
.process-tag {
  font-size: 8px;
  font-weight: 600;
  letter-spacing: 0.18em;
  color: var(--text-4);
  margin-bottom: 10px;
  opacity: 0.55;
}

/* ══════ Upload Content (Left) ══════ */
.upload-content {
  margin: auto 0;
  padding: 20px 0;
  position: relative;
  z-index: 1;
  max-width: 280px;
}

.upload-content > * {
  animation: fadeInUp 0.8s cubic-bezier(0.2, 0.8, 0.2, 1) both;
}
.upload-content .upload-title { animation-delay: 0.1s; }
.upload-content .upload-desc { animation-delay: 0.2s; }
.upload-content .upload-form { animation-delay: 0.3s; }
.upload-content .upload-progress-container { animation-delay: 0.2s; }

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(16px); }
  to { opacity: 1; transform: translateY(0); }
}

.upload-title {
  font-size: clamp(3rem, 5vw, 4.5rem);
  font-weight: 500;
  letter-spacing: -0.02em;
  margin: 0 0 8px 0;
  color: var(--text-1);
  line-height: 1.1;
}

.upload-desc {
  font-size: 14px;
  line-height: 1.7;
  color: var(--text-3);
  margin-bottom: 36px;
  font-weight: 400;
}

/* Form Styles */
.upload-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.custom-select {
  position: relative;
  display: block;
}

.custom-select select {
  width: 100%;
  appearance: none;
  background: transparent;
  border: none;
  border-bottom: 0.5px solid #ddd;
  padding: 10px 0;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.12em;
  color: var(--text-1);
  outline: none;
  cursor: pointer;
  text-transform: uppercase;
}

.file-drop-area {
  border: none;
  border-bottom: 0.5px solid #ddd;
  padding: 16px 0;
  text-align: left;
  cursor: pointer;
  transition: color var(--dur-2) ease;
  font-size: 9px;
  font-weight: 700;
  letter-spacing: 0.12em;
  color: var(--text-4);
  background: transparent;
}

.file-drop-area:hover {
  color: var(--text-2);
}

.file-drop-area.has-file {
  color: var(--text-1);
}

.hidden-input { display: none; }

.btn-upload {
  background: transparent;
  border: none;
  border-bottom: 0.5px solid var(--text-3);
  padding: 0 0 4px 0;
  font-size: 9px;
  font-weight: 700;
  letter-spacing: 0.2em;
  color: var(--text-1);
  cursor: pointer;
  display: inline-block;
  width: fit-content;
  transition: color var(--dur-2) ease, border-color var(--dur-2) ease;
  margin-top: 8px;
}

.btn-upload:hover:not(:disabled) {
  color: var(--primary);
  border-color: var(--primary);
}

.btn-upload:disabled {
  opacity: 0.25;
  cursor: not-allowed;
}

/* Progress UI */
.upload-progress-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.file-info {
  display: flex;
  align-items: center;
  gap: 16px;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.08em;
  color: var(--text-1);
  text-transform: uppercase;
}

.file-info .dot {
  width: 6px;
  height: 6px;
  background: var(--text-1);
  border-radius: 50%;
}

.file-info .size {
  color: var(--text-4);
}

.file-info .status-label {
  color: var(--text-4);
  margin-left: auto;
}

.big-percent {
  font-size: clamp(5rem, 10vw, 8rem);
  font-weight: 400; /* Medium-light for the number */
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  line-height: 0.9;
  letter-spacing: -0.04em;
  color: var(--text-1);
  margin: 16px 0;
}

.dashed-loader {
  display: flex;
  gap: 8px;
  align-items: center;
  margin-bottom: 24px;
}

.dashed-loader .dash {
  height: 2px;
  background: var(--text-1);
  width: 24px;
  opacity: 0.2;
  animation: loadPulse 1.5s infinite;
}

.dashed-loader .dash.short {
  width: 8px;
}

.dashed-loader .dash:nth-child(1) { opacity: 1; }
.dashed-loader .dash:nth-child(2) { animation-delay: 0.2s; }
.dashed-loader .dash:nth-child(3) { animation-delay: 0.4s; }
.dashed-loader .dash:nth-child(4) { animation-delay: 0.6s; }
.dashed-loader .dash:nth-child(5) { animation-delay: 0.8s; }

@keyframes loadPulse {
  0%, 100% { opacity: 0.2; }
  50% { opacity: 1; }
}

.subtext {
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 0.1em;
  color: var(--text-4);
}

/* Footer */
.hero-footer {
  position: absolute;
  bottom: 40px;
  left: clamp(40px, 4vw, 60px);
}

.btn-cancel {
  background: transparent;
  border: none;
  font-size: 9px; /* Small monospace */
  font-weight: 700;
  letter-spacing: 0.15em;
  color: var(--text-1);
  cursor: pointer;
  padding: 0;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
}

.btn-cancel:hover {
  color: var(--primary);
}

/* ══════ Ambient Readouts ══════ */
.ambient-readout {
  position: absolute;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  font-size: 7px;
  font-weight: 500;
  letter-spacing: 0.18em;
  color: rgba(0, 0, 0, 0.11);
  z-index: 8;
  pointer-events: none;
  user-select: none;
  text-transform: uppercase;
  white-space: nowrap;
}
.ar-tl { top: 16px; left: 16px; }
.ar-tr { top: 16px; right: 16px; }
.ar-bl { bottom: 16px; left: 16px; }
.ar-br { bottom: 16px; right: 16px; }

/* ══════ Network Container (Right) ══════ */
.network-container {
  position: absolute;
  inset: 0;
  z-index: 1;
}

.network-stage {
  position: absolute;
  top: 50%;
  left: 50%;
  width: min(78%, 760px);
  aspect-ratio: 4 / 3;
  transform: translate(-50%, -50%);
  pointer-events: none;
  animation: networkBreath 9s ease-in-out infinite;
}

.network-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
  display: block;
  user-select: none;
  -webkit-user-drag: none;
}

@keyframes networkBreath {
  0%, 100% { transform: translate(-50%, -50%) scale(1); }
  50%      { transform: translate(-50%, -50%) scale(1.012); }
}

@media (prefers-reduced-motion: reduce) {
  .network-stage { animation: none; }
}

.annotations {
  position: absolute;
  inset: 0;
  pointer-events: none;
  opacity: 0;
  transition: opacity 1s ease;
  z-index: 5;
}

.annotations.active {
  opacity: 1;
}

.annotation {
  position: absolute;
  font-size: 8px;
  font-weight: 700;
  letter-spacing: 0.12em;
  color: var(--text-1);
  line-height: 1.6;
}

.annotation .label {
  color: var(--text-4);
  margin-bottom: 4px;
}

.annotation .pointer-line {
  position: absolute;
  background: var(--text-4);
  height: 1px;
  opacity: 0.3;
}

.annotation .pointer-dot {
  position: absolute;
  width: 3px;
  height: 3px;
  background: var(--text-1);
  border-radius: 50%;
}

/* Specific annotation positions to match design */
.a-file {
  top: 25%;
  left: 10%;
}
.a-file .pointer-line {
  top: 24px;
  left: 100%;
  width: 80px;
  transform: rotate(30deg);
  transform-origin: left;
}
.a-file .pointer-dot { top: 43px; left: calc(100% + 67px); }

.a-data {
  bottom: 25%;
  left: 20%;
}
.a-data .pointer-line {
  top: 10px;
  left: 100%;
  width: 60px;
  transform: rotate(-15deg);
  transform-origin: left;
}
.a-data .pointer-dot { top: -6px; left: calc(100% + 56px); }

.a-status {
  top: 30%;
  right: 10%;
  text-align: right;
}
.a-status .pointer-line {
  top: 24px;
  right: 100%;
  width: 70px;
  transform: rotate(-30deg);
  transform-origin: right;
}
.a-status .pointer-dot { top: 41px; right: calc(100% + 59px); }

.a-eta {
  bottom: 20%;
  right: 15%;
  text-align: right;
}
.a-eta .pointer-line {
  top: 10px;
  right: 100%;
  width: 50px;
  transform: rotate(15deg);
  transform-origin: right;
}
.a-eta .pointer-dot { top: -2px; right: calc(100% + 46px); }

/* center-glow removed — now rendered via Three.js sprite */


@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

/* ══════ Review Section (Bottom) ══════ */
.review-section {
  padding: 60px 0 100px;
}

.review-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 40px;
}

.kicker {
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 0.16em;
  color: var(--text-4);
  margin-bottom: 8px;
}

.review-toolbar h2 {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-1);
}

/* ══════ Responsive ══════ */
@media (max-width: 960px) {
  .studio-hero {
    grid-template-columns: 1fr;
    grid-template-rows: auto 1fr;
    height: auto;
    min-height: 100vh;
  }
  .hero-left {
    padding: 40px 24px;
  }
  .hero-right {
    min-height: 60vh;
  }
  .watermark-percent {
    font-size: 8rem;
  }
}
</style>
