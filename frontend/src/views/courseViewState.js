export function chapterDisplayTitle(chapter = {}) {
  return chapter.title || chapter.name || chapter.id || '未命名章节';
}

export function chapterSubtopics(chapter = {}) {
  const source = Array.isArray(chapter.sections)
    ? chapter.sections
    : Array.isArray(chapter.objectives)
      ? chapter.objectives
      : Array.isArray(chapter.topics)
        ? chapter.topics
        : [];

  const topics = source
    .filter((item) => typeof item === 'string' && item.trim().length > 0)
    .map((item) => item.trim())
    .slice(0, 4);

  return topics.length > 0 ? topics : ['进入章节工作台'];
}

export function chapterNodeClass(index) {
  return `course-path-node path-node-${(index % 5) + 1}`;
}
