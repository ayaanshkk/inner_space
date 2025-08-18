import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    fs: {
      allow: [
        path.resolve(__dirname),                    // current frontend directory
        path.resolve(__dirname, '..'),              // parent directory (inner_space)
        path.resolve(__dirname, 'node_modules'),    // frontend node_modules if exists
        path.resolve(__dirname, '../node_modules')  // parent node_modules (where your deps are)
      ]
    }
  }
})