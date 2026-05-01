<script setup>
import { computed, onMounted, ref } from 'vue';
import { RouterLink } from 'vue-router';
import ActivityTimeline from '../components/ActivityTimeline.vue';
import { getDashboardSummary } from '../api/dashboard';

const summary = ref(null);
const loading = ref(true);
const error = ref('');

const courses = computed(() => summary.value?.courses ?? []);
const nextActivities = computed(() => summary.value?.nextActivities ?? []);
const draftActivities = computed(() => summary.value?.draftActivities ?? []);
const pendingReviews = computed(() => summary.value?.pendingReviews ?? []);
const totals = computed(() => summary.value?.totals ?? {
  courseCount: 0,
  activities: 0,
  publishedActivities: 0,
  draftActivities: 0,
  pendingReviews: 0,
  graphNodes: 0,
  graphEdges: 0
});

const primaryActivity = computed(() => nextActivities.value[0] || null);
const primaryCourse = computed(() => {
  if (primaryActivity.value) {
    return courses.value.find((course) =>
      course.id === primaryActivity.value.course_id || course.id === primaryActivity.value.courseId
    ) || null;
  }
  return courses.value[0] || null;
});
const primaryCoursePath = computed(() =>
  primaryCourse.value ? `/courses/${primaryCourse.value.id}` : '/'
);

onMounted(async () => {
  loading.value = true;
  error.value = '';
  try {
    summary.value = await getDashboardSummary();
  } catch (caughtError) {
    error.value = caughtError?.message || 'Unable to load dashboard.';
  } finally {
    loading.value = false;
  }
});
</script>

<template>
  <div class="dashboard-view">
    <section class="dashboard-header shell-container" aria-labelledby="dashboard-title">
      <div class="dashboard-title-block">
        <p class="kicker">课程运营</p>
        <h1 id="dashboard-title">课程工作台</h1>
        <p>
          查看已发布活动、课程覆盖和教师待处理事项，从当前最需要推进的课程进入工作区。
        </p>
      </div>

      <RouterLink :to="primaryCoursePath" class="dashboard-primary-action">
        <span>{{ primaryActivity ? '继续下一项活动' : '进入课程工作区' }}</span>
        <strong>{{ primaryActivity?.title || primaryCourse?.title || '暂无课程' }}</strong>
      </RouterLink>
    </section>

    <div v-if="error" class="shell-container">
      <p class="status-message error">{{ error }}</p>
    </div>

    <section class="shell-container dashboard-grid" aria-label="课程运营概览">
      <div class="stats-row">
        <article class="stat-panel">
          <span>课程</span>
          <strong>{{ totals.courseCount }}</strong>
        </article>
        <article class="stat-panel">
          <span>活动</span>
          <strong>{{ totals.activities }}</strong>
        </article>
        <article class="stat-panel">
          <span>待审核</span>
          <strong>{{ totals.pendingReviews }}</strong>
        </article>
        <article class="stat-panel">
          <span>图谱概念</span>
          <strong>{{ totals.graphNodes }}</strong>
        </article>
      </div>

      <section class="panel main-panel-block" aria-labelledby="next-activities-title">
        <div class="panel-header-row">
          <div>
            <p class="eyebrow">Published activities</p>
            <h2 id="next-activities-title">下一批学习活动</h2>
          </div>
          <span class="panel-count">{{ totals.publishedActivities }} 已发布</span>
        </div>
        <ActivityTimeline
          :activities="nextActivities"
          empty-text="暂无已发布活动。请到教师工作室发布课件、实验或代码训练。"
        />
      </section>

      <section class="panel" aria-labelledby="courses-title">
        <div class="panel-header-row">
          <div>
            <p class="eyebrow">Courses</p>
            <h2 id="courses-title">课程工作区</h2>
          </div>
          <span class="panel-count">{{ courses.length }} 门课程</span>
        </div>

        <div v-if="courses.length > 0" class="dashboard-course-list">
          <RouterLink
            v-for="course in courses"
            :key="course.id"
            :to="`/courses/${course.id}`"
            class="dashboard-course-card"
          >
            <span class="course-card-label">{{ course.chapterCount }} 章节</span>
            <h3>{{ course.title }}</h3>
            <p>{{ course.summary || '课程材料、活动和知识图谱已接入工作区。' }}</p>
            <dl>
              <div>
                <dt>活动</dt>
                <dd>{{ course.activityCount || 0 }}</dd>
              </div>
              <div>
                <dt>概念</dt>
                <dd>{{ course.graphNodeCount }}</dd>
              </div>
              <div>
                <dt>关系</dt>
                <dd>{{ course.graphEdgeCount }}</dd>
              </div>
            </dl>
          </RouterLink>
        </div>
        <p v-else-if="loading" class="status-message">正在加载课程...</p>
        <p v-else class="status-message">暂无可用课程。</p>
      </section>

      <section class="panel" aria-labelledby="teacher-queue-title">
        <div class="panel-header-row">
          <div>
            <p class="eyebrow">Teacher queue</p>
            <h2 id="teacher-queue-title">教师队列</h2>
          </div>
          <RouterLink to="/teacher" class="panel-link">打开教师工作室</RouterLink>
        </div>

        <div class="queue-summary">
          <article>
            <span>草稿活动</span>
            <strong>{{ totals.draftActivities }}</strong>
          </article>
          <article>
            <span>待审核材料</span>
            <strong>{{ totals.pendingReviews }}</strong>
          </article>
        </div>

        <div class="queue-list">
          <p class="queue-heading">近期草稿</p>
          <ul v-if="draftActivities.length > 0">
            <li v-for="activity in draftActivities" :key="activity.id">
              <span>{{ activity.title || activity.id }}</span>
              <small>{{ activity.status || 'draft' }}</small>
            </li>
          </ul>
          <p v-else class="status-message">暂无草稿活动。</p>
        </div>

        <div class="queue-list">
          <p class="queue-heading">审核事项</p>
          <ul v-if="pendingReviews.length > 0">
            <li v-for="item in pendingReviews.slice(0, 4)" :key="item.id">
              <span>{{ item.title || item.payload?.title || '未命名材料' }}</span>
              <small>{{ item.status || 'pending' }}</small>
            </li>
          </ul>
          <p v-else class="status-message">暂无待审核材料。</p>
        </div>
      </section>
    </section>
  </div>
</template>

<style scoped>
.dashboard-view {
  min-height: 100vh;
  padding: calc(var(--nav-height) + 28px) 0 48px;
  background: var(--ink-0);
}

.dashboard-header {
  display: flex;
  align-items: end;
  justify-content: space-between;
  gap: 24px;
  margin-bottom: 22px;
}

.dashboard-title-block {
  display: grid;
  gap: 8px;
  max-width: 720px;
}

.dashboard-title-block h1 {
  margin: 0;
  color: var(--text-1);
  font-size: clamp(2rem, 4vw, 3.6rem);
  line-height: 1.05;
}

.dashboard-title-block p {
  margin: 0;
  color: var(--text-3);
  line-height: 1.6;
}

.dashboard-primary-action,
.panel-link {
  display: inline-grid;
  gap: 4px;
  min-width: 220px;
  padding: 12px 14px;
  border: 1px solid rgba(94, 234, 212, 0.28);
  border-radius: 8px;
  background: rgba(94, 234, 212, 0.08);
  color: var(--text-1);
}

.dashboard-primary-action span,
.panel-link {
  color: var(--accent-cyan);
  font-size: 0.82rem;
  font-weight: 750;
}

.dashboard-primary-action strong {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.4fr) minmax(300px, 0.8fr);
  gap: 16px;
}

.stats-row {
  grid-column: 1 / -1;
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
}

.stat-panel {
  display: grid;
  gap: 6px;
  min-height: 104px;
  padding: 16px;
  border: 1px solid var(--line-medium);
  border-radius: 8px;
  background: rgba(17, 21, 26, 0.82);
}

.stat-panel span,
.panel-count,
.course-card-label {
  color: var(--text-4);
  font-size: 0.78rem;
  font-weight: 750;
}

.stat-panel strong {
  color: var(--text-1);
  font-size: 2rem;
  line-height: 1;
}

.main-panel-block {
  grid-row: span 2;
}

.panel {
  display: grid;
  gap: 16px;
}

.panel-header-row {
  display: flex;
  align-items: start;
  justify-content: space-between;
  gap: 12px;
}

.panel-header-row h2 {
  margin: 0;
  color: var(--text-1);
  font-size: 1.05rem;
}

.panel-link {
  min-width: auto;
  padding: 8px 10px;
}

.dashboard-course-list,
.queue-list ul {
  display: grid;
  gap: 10px;
}

.dashboard-course-card {
  display: grid;
  gap: 10px;
  padding: 14px;
  border: 1px solid var(--line-soft);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.03);
}

.dashboard-course-card:hover {
  border-color: rgba(94, 234, 212, 0.35);
}

.dashboard-course-card h3 {
  margin: 0;
  color: var(--text-1);
  font-size: 1rem;
}

.dashboard-course-card p {
  margin: 0;
  color: var(--text-3);
  line-height: 1.5;
}

.dashboard-course-card dl {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 8px;
  margin: 0;
}

.dashboard-course-card div {
  display: grid;
  gap: 2px;
}

.dashboard-course-card dt {
  color: var(--text-4);
  font-size: 0.72rem;
}

.dashboard-course-card dd {
  margin: 0;
  color: var(--text-1);
  font-weight: 750;
}

.queue-summary {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.queue-summary article {
  display: grid;
  gap: 4px;
  padding: 12px;
  border: 1px solid var(--line-soft);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.03);
}

.queue-summary span,
.queue-list small {
  color: var(--text-4);
  font-size: 0.78rem;
}

.queue-summary strong {
  color: var(--text-1);
  font-size: 1.45rem;
}

.queue-heading {
  margin: 0 0 8px;
  color: var(--text-2);
  font-weight: 750;
}

.queue-list ul {
  margin: 0;
  padding: 0;
  list-style: none;
}

.queue-list li {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  min-height: 36px;
  padding: 8px 10px;
  border: 1px solid var(--line-soft);
  border-radius: 8px;
  color: var(--text-2);
}

.queue-list li span {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

@media (max-width: 900px) {
  .dashboard-header {
    align-items: stretch;
    flex-direction: column;
  }

  .dashboard-grid,
  .stats-row {
    grid-template-columns: 1fr;
  }

  .main-panel-block {
    grid-row: auto;
  }
}
</style>
