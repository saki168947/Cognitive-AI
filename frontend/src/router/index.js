import { createRouter, createWebHistory } from 'vue-router';
import DashboardView from '../views/DashboardView.vue';
import CourseView from '../views/CourseView.vue';
import TeacherStudioView from '../views/TeacherStudioView.vue';

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
    path: '/teacher',
    name: 'teacher',
    component: TeacherStudioView
  }
];

export default createRouter({
  history: createWebHistory(),
  routes
});
