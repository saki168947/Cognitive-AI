export const ACTIVITY_TYPE_LABELS = {
  reading: '阅读',
  lecture_deck: '课件',
  h5p_activity: '互动内容',
  code_lab: '代码实验',
  notebook_lab: 'Notebook 实验',
  cognitive_experiment: '认知实验',
  bci_dataset_lab: '脑机数据实验',
  graph_task: '图谱任务',
  quiz: '测验',
  assignment: '作业',
  reflection: '反思'
};

export function activityTypeLabel(type) {
  return ACTIVITY_TYPE_LABELS[type] || '活动';
}

export function safeActivities(value) {
  return Array.isArray(value) ? value : [];
}

export function groupActivitiesByType(activities) {
  return safeActivities(activities).reduce((groups, activity) => {
    const type = activity?.type || 'reading';
    return {
      ...groups,
      [type]: [...(groups[type] || []), activity]
    };
  }, {});
}

export function publishedActivities(activities) {
  return safeActivities(activities).filter((activity) => activity.status === 'published');
}

export function draftActivities(activities) {
  return safeActivities(activities).filter((activity) =>
    activity.status === 'draft' || activity.status === 'scheduled'
  );
}

export function nextPublishedActivity(activities) {
  return publishedActivities(activities)[0] || null;
}
