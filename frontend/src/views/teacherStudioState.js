export function reviewItemCreatedMessage(created) {
  return `Created review item ${created?.review_item_id || ''}`.trim();
}

export function createReviewActionTracker() {
  const pending = new Set();

  return {
    start(id) {
      if (!id || pending.has(id)) {
        return false;
      }
      pending.add(id);
      return true;
    },
    finish(id) {
      pending.delete(id);
    },
    isPending(id) {
      return pending.has(id);
    }
  };
}
