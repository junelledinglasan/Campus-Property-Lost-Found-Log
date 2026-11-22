import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// Kapag handa na ang Django backend, tatakbo ito sa port 8000.
// Ipapasa ng proxy na ito ang lahat ng /api requests papunta roon.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': 'http://localhost:8000',
    },
  },
});
