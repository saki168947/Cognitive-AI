import { createRouter, createWebHistory } from 'vue-router';
import DashboardView from '../views/DashboardView.vue';
import CourseView from '../views/CourseView.vue';
import ChapterActivityFlowView from '../views/ChapterActivityFlowView.vue';
import TeacherStudioView from '../views/TeacherStudioView.vue';
import TutorView from '../views/TutorView.vue';
import UploadView from '../views/UploadView.vue';

const routes = [
  {
    path: '/',
    name: 'dashboard',
    component: DashboardView
  },
  {
    path: '/courses/:courseId',
    name: 'course',
    component: CourseView,
    props: true
  },
  {
    path: '/courses/:courseId/chapters/:chapterId',
    name: 'chapter-activity-flow',
    component: ChapterActivityFlowView,
    props: true
  },
  {
    path: '/teacher',
    name: 'teacher',
    component: TeacherStudioView
  },
  {
    path: '/tutor',
    name: 'tutor',
    component: TutorView
  },
  {
    path: '/upload',
    name: 'upload',
    component: UploadView
  }
];

export default createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) return savedPosition;
    return { top: 0 };
  }
});
