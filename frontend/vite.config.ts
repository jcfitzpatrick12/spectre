import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

const BACKEND = process.env.SPECTRE_BACKEND_URL ?? 'http://localhost:5001';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    strictPort: true,
    proxy: {
      '/api': {
        target: BACKEND,
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
});
