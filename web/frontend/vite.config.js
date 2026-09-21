import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// The API's address. run_web.py sets this so a non-default backend port still
// works; started by hand, it falls back to the documented port 8000.
const apiTarget = process.env.ENVISTRA_API_TARGET || 'http://localhost:8000'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: apiTarget,
        changeOrigin: true
      },
      '/ws': {
        target: apiTarget.replace(/^http/, 'ws'),
        ws: true
      }
    }
  }
})
