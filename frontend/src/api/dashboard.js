import { listActivities } from './activities';
import { listCourses } from './courses';
import { getGraph } from './graph';
import { listReviewItems } from './review';
import { draftActivities, publishedActivities } from '../views/activityState';

function safeArray(value) {
  return Array.isArray(value) ? value : [];
}

function countNodes(graph) {
  return safeArray(graph?.nodes).length;
}

function countEdges(graph) {
  if (!graph) return 0;
  return safeArray(graph.edges).length || safeArray(graph.links).length;
}

function isReviewPending(item) {
  const status = (item?.status || '').toLowerCase();
  return status === 'draft' || status === 'pending' || status === '';
}

function parseTimestamp(value) {
  if (!value) return 0;
  const ms = Date.parse(value);
  return Number.isFinite(ms) ? ms : 0;
}

function resultError(result, label) {
  if (result.status === 'fulfilled') {
    return '';
  }
  return `${label}加载失败：${result.reason?.message || '请稍后重试'}`;
}

export async function getDashboardSummary() {
  const [coursesResult, reviewItemsResult, activitiesResult] = await Promise.allSettled([
    listCourses(),
    listReviewItems(),
    listActivities()
  ]);

  const errors = [
    resultError(coursesResult, '课程'),
    resultError(reviewItemsResult, '审核队列'),
    resultError(activitiesResult, '学习活动')
  ].filter(Boolean);
  const courses = coursesResult.status === 'fulfilled' ? safeArray(coursesResult.value) : [];
  const reviewItems = reviewItemsResult.status === 'fulfilled' ? safeArray(reviewItemsResult.value) : [];
  const activities = activitiesResult.status === 'fulfilled' ? safeArray(activitiesResult.value) : [];
  const published = publishedActivities(activities);
  const drafts = draftActivities(activities);

  const graphResults = await Promise.allSettled(
    courses.map((course) => getGraph(course.id))
  );
  const graphErrors = graphResults
    .map((result, index) => resultError(result, `${courses[index]?.title || courses[index]?.id || '课程'}图谱`))
    .filter(Boolean);

  const enrichedCourses = courses.map((course, index) => {
    const graph = graphResults[index].status === 'fulfilled' ? graphResults[index].value : null;
    const graphUnavailable = graphResults[index].status === 'rejected';
    const courseActivities = activities.filter((activity) => activity.course_id === course.id || activity.courseId === course.id);
    return {
      id: course.id,
      title: course.title || course.name || 'Untitled course',
      summary: course.summary || course.description || '',
      graphNodeCount: countNodes(graph),
      graphEdgeCount: countEdges(graph),
      graphUnavailable,
      chapterCount: safeArray(course.chapters).length,
      activityCount: courseActivities.length,
      publishedActivityCount: published.filter((activity) => activity.course_id === course.id || activity.courseId === course.id).length,
      draftActivityCount: drafts.filter((activity) => activity.course_id === course.id || activity.courseId === course.id).length
    };
  });

  const graphNodes = enrichedCourses.reduce((acc, c) => acc + c.graphNodeCount, 0);
  const graphEdges = enrichedCourses.reduce((acc, c) => acc + c.graphEdgeCount, 0);
  const pendingReviews = reviewItems.filter(isReviewPending);
  const recentReviewItems = [...reviewItems]
    .sort((a, b) => parseTimestamp(b.created_at || b.createdAt) - parseTimestamp(a.created_at || a.createdAt))
    .slice(0, 6);

  return {
    courses: enrichedCourses,
    totals: {
      courseCount: enrichedCourses.length,
      chapterCount: enrichedCourses.reduce((acc, c) => acc + c.chapterCount, 0),
      graphNodes,
      graphEdges,
      pendingReviews: pendingReviews.length,
      recentUploads: recentReviewItems.length,
      activities: activities.length,
      publishedActivities: published.length,
      draftActivities: drafts.length
    },
    activities,
    nextActivities: published.slice(0, 6),
    draftActivities: drafts.slice(0, 6),
    errors: [...errors, ...graphErrors],
    pendingReviews,
    recentReviewItems
  };
}
