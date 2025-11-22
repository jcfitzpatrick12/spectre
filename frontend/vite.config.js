import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 3000,
    proxy: {
      '/recordings': 'http://spectre-dev-server:5001',
      '/spectre-data': 'http://spectre-dev-server:5001'
    }
  },
  preview: {
    host: '0.0.0.0',
    port: 3000,
    proxy: {
      '/recordings': 'http://spectre-dev-server:5001',
      '/spectre-data': 'http://spectre-dev-server:5001'
    }
  }
})