<template>
  <section class="view">
    <header class="view-header">
      <p class="view-kicker">Teacher studio</p>
      <h1 class="view-title">Review and publish</h1>
      <p class="view-copy">Upload course material, inspect generated review items, and publish approved content.</p>
    </header>

    <div class="teacher-studio-layout">
      <section class="panel teacher-upload-panel">
        <header class="panel-header">
          <p class="eyebrow">Materials</p>
          <h2>Upload course material</h2>
        </header>

        <form class="teacher-upload-form" @submit.prevent="submitUpload">
          <label class="form-field">
            <span class="field-label">Course</span>
            <select v-model="selectedCourseId" class="form-control">
              <option v-if="courses.length === 0" value="ai-intro">AI Intro</option>
              <option v-for="course in courses" :key="course.id" :value="course.id">
                {{ course.title || course.name || course.id }}
              </option>
            </select>
          </label>

          <label class="form-field">
            <span class="field-label">Material file</span>
            <input ref="fileInput" class="form-control" type="file" @change="selectFile" />
          </label>

          <button type="submit" class="button" :disabled="uploadDisabled">
            {{ uploading ? 'Uploading...' : 'Upload material' }}
          </button>
        </form>

        <p v-if="coursesLoading" class="status-message">Loading courses...</p>
        <p v-if="message" class="status-message success">{{ message }}</p>
        <p v-if="error" class="status-message error">{{ error }}</p>
      </section>

      <section class="teacher-review-section">
        <div class="review-toolbar">
          <div>
            <p class="eyebrow">Queue</p>
            <h2>Review items</h2>
          </div>
          <button type="button" class="button secondary compact" :disabled="itemsLoading" @click="loadReviewItems">
            Refresh
          </button>
        </div>

        <div v-if="itemsLoading" class="panel">
          <p class="status-message">Loading review items...</p>
        </div>
        <ReviewQueue
          v-else
          :items="reviewItems"
          @approve="approveItem"
          @reject="rejectItem"
          @publish="publishItem"
        />
      </section>
    </div>
  </section>
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

const fallbackCourseId = 'ai-intro';

const courses = ref([]);
const reviewItems = ref([]);
const selectedCourseId = ref(fallbackCourseId);
const selectedFile = ref(null);
const fileInput = ref(null);
const coursesLoading = ref(false);
const itemsLoading = ref(false);
const uploading = ref(false);
const error = ref('');
const message = ref('');
let reviewRequestId = 0;

const uploadDisabled = computed(() => !selectedCourseId.value || !selectedFile.value || uploading.value);

onMounted(() => {
  loadCourses();
  loadReviewItems();
});

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
    error.value = caughtError?.message || 'Unable to load courses.';
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
      error.value = caughtError?.message || 'Unable to load review items.';
    }
  } finally {
    if (requestId === reviewRequestId) {
      itemsLoading.value = false;
    }
  }
}

function selectFile(event) {
  selectedFile.value = event.target.files?.[0] || null;
}

async function submitUpload() {
  if (uploadDisabled.value) {
    return;
  }

  uploading.value = true;
  error.value = '';
  message.value = '';

  try {
    const created = await uploadMaterial(selectedCourseId.value, selectedFile.value);
    message.value = `Created review item ${created?.id || ''}`.trim();
    selectedFile.value = null;
    if (fileInput.value) {
      fileInput.value.value = '';
    }
    await loadReviewItems();
  } catch (caughtError) {
    error.value = caughtError?.message || 'Unable to upload material.';
  } finally {
    uploading.value = false;
  }
}

async function approveItem(id) {
  await runReviewAction(() => approveReviewItem(id));
}

async function rejectItem(id) {
  await runReviewAction(() => rejectReviewItem(id));
}

async function publishItem(id) {
  await runReviewAction(() => publishReviewItem(id));
}

async function runReviewAction(action) {
  error.value = '';
  message.value = '';

  try {
    await action();
    await loadReviewItems();
  } catch (caughtError) {
    error.value = caughtError?.message || 'Unable to update review item.';
  }
}
</script>
