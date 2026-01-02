import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0', // Allow access from all network interfaces
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://141.11.0.80:8000',
        changeOrigin: true,
      },
      '/ws': {
        target: 'ws://141.11.0.80:8000',
        ws: true,
      }
    }
  }
})

