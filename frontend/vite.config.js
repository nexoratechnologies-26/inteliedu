import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@threejs': path.resolve(__dirname, '../threejs'),
    },
  },
  server: {
    port: 5173,
  },
});
