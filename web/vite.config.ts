import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      // Dev: forward /api/* to the chat_bff process running on :8002.
      // In production the BFF and the static bundle ship together so
      // /api is same-origin and no proxy is needed.
      "/api": {
        target: "http://localhost:8002",
        changeOrigin: true,
      },
    },
  },
});
