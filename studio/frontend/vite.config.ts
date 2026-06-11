import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

const apiTarget = process.env.VITE_STUDIO_API_URL ?? "http://127.0.0.1:8100";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5174,
    strictPort: true,
    proxy: {
      "/studio": {
        target: apiTarget,
        changeOrigin: true,
      },
    },
  },
});
