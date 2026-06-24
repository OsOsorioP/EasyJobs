import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import federation from '@originjs/vite-plugin-federation'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(), 
    tailwindcss(),
    federation({
      name: 'intelligence',
      filename: 'remoteEntry.js',
      exposes: {
        './SearchContainer': './src/SearchContainer.tsx',
      },
      shared: ['react', 'react-dom']
    })
  ],
  build: {
    target: 'esnext',
    minify: false,
    cssCodeSplit: false
  },
  server: {
    port: 5001,
    strictPort: true
  },
  preview: {
    port: 5001,
    strictPort: true
  }
})
