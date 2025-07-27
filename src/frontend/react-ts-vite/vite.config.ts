import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  css: {
    postcss: {
      plugins: [],
    },
  },
  define: {
    // Flight Tracker theme variables accessible in JS
    __THEME_COLORS__: {
      primary: '#007bff',
      success: '#28a745',
      warning: '#ffc107',
      danger: '#dc3545',
      info: '#17a2b8',
    },
  },
  server: {
    port: 5173,
    host: true, // Allow external connections
    strictPort: false,
  },
  preview: {
    port: 5173,
    host: true,
  },
  build: {
    cssCodeSplit: false, // Bundle all CSS into one file
    rollupOptions: {
      output: {
        assetFileNames: (assetInfo) => {
          if (assetInfo.name?.endsWith('.css')) {
            return 'assets/flight-tracker.[hash].css';
          }
          return 'assets/[name].[hash].[ext]';
        },
      },
    },
  },
})
