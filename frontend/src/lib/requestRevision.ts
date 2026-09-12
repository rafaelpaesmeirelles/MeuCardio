/** A response may update the UI only while its request and input revision match. */
export function createRequestRevision() {
  let revision = 0;
  return {
    invalidate() { revision += 1; },
    begin() {
      const requestRevision = ++revision;
      return () => requestRevision === revision;
    },
  };
}
