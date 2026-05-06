const CHAPTER_I18N = {
  'ai-foundations': { en: 'Foundations', zh: '基础' },
  'ai-search': { en: 'Search and Problem Solving', zh: '搜索与问题求解' },
  'ai-learning': { en: 'Learning and Neural Networks', zh: '学习与神经网络' },
  'ai-language-vision': { en: 'Language, Vision and Knowledge', zh: '语言、视觉与知识' },
  'ai-future': { en: 'Applications and Future Directions', zh: '应用与未来方向' },
};

const SUBTOPICS_I18N = {
  'ai-foundations': [
    { en: 'What is AI?', zh: '什么是人工智能？' },
    { en: 'Agents and environments', zh: '智能体与环境' },
  ],
  'ai-search': [
    { en: 'Problem-Solving Agents', zh: '问题求解智能体' },
    { en: 'Uninformed Search', zh: '无信息搜索' },
    { en: 'Informed Search', zh: '有信息搜索' },
    { en: 'Heuristics and Optimization', zh: '启发式与优化' },
  ],
  'ai-learning': [
    { en: 'Machine Learning Basics', zh: '机器学习基础' },
    { en: 'Neural Network Foundations', zh: '神经网络基础' },
    { en: 'Deep Learning', zh: '深度学习' },
    { en: 'Training and Generalization', zh: '训练与泛化' },
  ],
  'ai-language-vision': [
    { en: 'Language Models', zh: '语言模型' },
    { en: 'Computer Vision', zh: '计算机视觉' },
    { en: 'Knowledge Graphs', zh: '知识图谱' },
    { en: 'Reasoning Systems', zh: '推理系统' },
  ],
  'ai-future': [
    { en: 'AI in Neuroscience', zh: '人工智能与神经科学' },
    { en: 'Brain-Inspired AI', zh: '类脑人工智能' },
    { en: 'Ethical Considerations', zh: '伦理思考' },
    { en: 'The Road Ahead', zh: '未来展望' },
  ],
};

export function chapterDisplayTitle(chapter = {}) {
  const id = chapter.id || '';
  const i18n = CHAPTER_I18N[id];
  if (i18n) {
    return { en: i18n.en, zh: i18n.zh };
  }
  const raw = chapter.title || chapter.name || id || '未命名章节';
  return { en: raw, zh: raw };
}

export function chapterSubtopics(chapter = {}) {
  const id = chapter.id || '';
  const i18n = SUBTOPICS_I18N[id];
  if (i18n) {
    return i18n;
  }

  const source = Array.isArray(chapter.sections)
    ? chapter.sections
    : Array.isArray(chapter.objectives)
      ? chapter.objectives
      : Array.isArray(chapter.topics)
        ? chapter.topics
        : [];

  const topics = source
    .filter((item) => typeof item === 'string' && item.trim().length > 0)
    .map((item) => ({ en: item.trim(), zh: item.trim() }))
    .slice(0, 4);

  return topics.length > 0 ? topics : [{ en: 'Enter chapter workspace', zh: '进入章节工作台' }];
}

export function chapterNodeClass(index) {
  return `course-path-node path-node-${(index % 5) + 1}`;
}
