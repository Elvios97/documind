import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";

export default defineConfig({
  clearScreen: false,
  plugins: [react()],
  test: {
    environment: "jsdom",
    setupFiles: "./src/test/setup.ts",
    clearMocks: true,
  },
  server: {
    host: "127.0.0.1",
    port: 5174,
    strictPort: true,
  },
});
