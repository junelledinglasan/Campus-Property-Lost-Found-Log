import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// Tumatakbo ang Django backend sa port 8000.
// Ipinapasa ng proxy na ito ang /api (data) at /media (mga larawan ng item) papunta roon.
// Ginagamit din ito ng `npm run preview`.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': 'http://127.0.0.1:8000',
      '/media': 'http://127.0.0.1:8000',
    },
  },
});
