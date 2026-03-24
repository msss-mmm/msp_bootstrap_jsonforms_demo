import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  // Load env file based on `mode` in the current working directory.
  // Set the third parameter to '' to load all envs regardless of the `VITE_` prefix.
  // First, we check the actual process.env for VITE_APP_TITLE to handle Docker build args
  const env = {
    ...process.env,
    ...loadEnv(mode, '../', '')
  }

  return {
    envDir: '../',
    plugins: [
      vue(),
      {
        name: 'html-transform',
        transformIndexHtml(html) {
          return html.replace(
            /%VITE_APP_TITLE%/g,
            env.VITE_APP_TITLE || 'App'
          )
        }
      }
    ],
    // Support for subpath via --base during build or VITE_BASE_URL env
    // Setting to './' for relative paths for portability
    base: './',
    server: {
      proxy: {
        '^(/.*)?/api': {
          target: 'http://localhost:8000',
          changeOrigin: true,
          rewrite: (path) => path.replace(/^.*\/api/, '/api')
        }
      }
    }
  }
})
