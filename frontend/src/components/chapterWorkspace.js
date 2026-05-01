export function normalizeObjectives(objectives) {
  if (Array.isArray(objectives)) {
    return objectives.filter((objective) => typeof objective === 'string' && objective.trim().length > 0);
  }

  if (typeof objectives === 'string' && objectives.trim().length > 0) {
    return [objectives.trim()];
  }

  return [];
}
