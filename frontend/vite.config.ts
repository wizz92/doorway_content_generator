import { defineConfig, loadEnv } from 'vite'
import path from 'path'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  // Load environment variables (e.g., from .env)
  // NOTE: load from project root so a single .env at repo root is used
  const env = loadEnv(mode, path.resolve(__dirname, '..'), '')
  // Ports and backend URL are controlled via .env
  const frontendPort = Number(env.VITE_PORT || env.PORT || 3021)
  const backendUrl = env.BACKEND_URL

  return {
    plugins: [react()],
    server: {
      port: frontendPort,
      proxy: {
        '/api': {
          target: backendUrl,
          changeOrigin: true,
          secure: false,
        },
      },
    },
  }
})
