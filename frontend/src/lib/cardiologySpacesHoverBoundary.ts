/*
 * Cardiology Spaces — hover boundary compatibility.
 *
 * The portal preview is owned by React in CardiologySpacesHome. Its container
 * clears the preview on mouse leave, but a pointer can leave a portal and land
 * in an empty gap that still belongs to the container. In that case the native
 * container mouse-leave does not happen and the old preview can remain active.
 *
 * We normalize that browser boundary: when the pointer transitions from a
 * portal into a bare area of .spaces-doors, emit the same mouse-out boundary
 * React already handles. No product state is duplicated here.
 */

function closestPortal(node: EventTarget | null): Element | null {
  return node instanceof Element ? node.closest(".spaces-door") : null;
}

function installCardiologySpacesHoverBoundary() {
  if (typeof document === "undefined") return;

  document.addEventListener(
    "mouseover",
    (event) => {
      const target = event.target;
      if (!(target instanceof HTMLElement) || !target.classList.contains("spaces-doors")) return;
      if (!closestPortal(event.relatedTarget)) return;

      target.dispatchEvent(
        new MouseEvent("mouseout", {
          bubbles: true,
          cancelable: true,
          relatedTarget: document.body,
          clientX: event.clientX,
          clientY: event.clientY,
        }),
      );
    },
    true,
  );
}

installCardiologySpacesHoverBoundary();
