import { beforeAll } from "vitest";

// Avoid jsdom style parsing errors from Vuetify test runs by no-op-ing style insertions.
beforeAll(() => {
  const originalAppendChild = document.head.appendChild.bind(document.head);
  document.head.appendChild = (node: Node) => {
    if ((node as HTMLElement).tagName === "STYLE") {
      return node;
    }
    return originalAppendChild(node);
  };

  // Polyfill ResizeObserver for Vuetify in tests
  if (typeof (globalThis as any).ResizeObserver === "undefined") {
    (globalThis as any).ResizeObserver = class {
      observe() {}
      unobserve() {}
      disconnect() {}
    };
  }

  if (typeof (globalThis as any).visualViewport === "undefined") {
    (globalThis as any).visualViewport = {
      addEventListener() {},
      removeEventListener() {},
      height: 0,
      width: 0,
      scale: 1,
      offsetTop: 0,
      offsetLeft: 0
    };
  }
});
