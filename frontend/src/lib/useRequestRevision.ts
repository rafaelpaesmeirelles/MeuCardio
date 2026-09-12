import { useEffect, useRef } from "react";
import { createRequestRevision } from "./requestRevision";

/** Invalidate on input/route changes before an obsolete response can be painted. */
export function useRequestRevision(identity: string = "") {
  const state = useRef({ identity, requests: createRequestRevision() });
  if (state.current.identity !== identity) {
    state.current.identity = identity;
    state.current.requests.invalidate();
  }
  const requests = state.current.requests;
  useEffect(() => () => requests.invalidate(), [requests]);
  return requests;
}
