import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    // e2e/ holds Playwright specs (real browser, real dev server) — a
    // completely different runner and `test`/`expect` API. Vitest must
    // never try to collect them.
    exclude: ["**/node_modules/**", "**/dist/**", "e2e/**"],
  },
});
