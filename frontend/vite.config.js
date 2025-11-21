import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    react({
      // Enable Fast Refresh
      fastRefresh: true,
      // Babel configuration
      babel: {
        plugins: [
          // Add any Babel plugins here if needed
        ],
      },
    }),
  ],

  // Path resolution
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@components': path.resolve(__dirname, './src/components'),
      '@pages': path.resolve(__dirname, './src/pages'),
      '@hooks': path.resolve(__dirname, './src/hooks'),
      '@utils': path.resolve(__dirname, './src/utils'),
      '@services': path.resolve(__dirname, './src/services'),
      '@store': path.resolve(__dirname, './src/store'),
      '@assets': path.resolve(__dirname, './src/assets'),
      '@styles': path.resolve(__dirname, './src/styles'),
    },
  },

  // Development server configuration
  server: {
    port: 3000,
    host: true, // Listen on all addresses
    open: true, // Automatically open browser
    strictPort: false, // Try next port if 3000 is busy
    
    // Proxy API requests to backend
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        secure: false,
        ws: true, // WebSocket support
        configure: (proxy, _options) => {
          proxy.on('error', (err, _req, _res) => {
            console.log('proxy error', err);
          });
          proxy.on('proxyReq', (proxyReq, req, _res) => {
            console.log('Sending Request to the Target:', req.method, req.url);
          });
          proxy.on('proxyRes', (proxyRes, req, _res) => {
            console.log('Received Response from the Target:', proxyRes.statusCode, req.url);
          });
        },
      },
    },

    // CORS configuration
    cors: true,

    // HMR (Hot Module Replacement) configuration
    hmr: {
      overlay: true,
    },
  },

  // Preview server configuration (for production build preview)
  preview: {
    port: 3001,
    host: true,
    open: true,
    strictPort: false,
  },

  // Build configuration
  build: {
    // Output directory
    outDir: 'dist',
    
    // Assets directory
    assetsDir: 'assets',
    
    // Generate sourcemaps for debugging
    sourcemap: true,
    
    // Minification
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true, // Remove console.log in production
        drop_debugger: true,
      },
    },
    
    // Rollup options
    rollupOptions: {
      output: {
        // Manual chunks for better code splitting
        manualChunks: {
          // React and related libraries
          'react-vendor': ['react', 'react-dom', 'react-router-dom'],
          
          // Three.js and 3D rendering
          'three-vendor': ['three', '@react-three/fiber', '@react-three/drei'],
          
          // Chart libraries
          'chart-vendor': ['recharts'],
          
          // Utility libraries
          'utils-vendor': [
            'axios', 
            'date-fns', 
            'file-saver', 
            'clsx',
            'zustand'
          ],
          
          // Form handling
          'form-vendor': [
            'react-hook-form',
            '@hookform/resolvers',
            'zod'
          ],
        },
        
        // Asset file names
        assetFileNames: (assetInfo) => {
          const info = assetInfo.name.split('.');
          const ext = info[info.length - 1];
          
          if (/png|jpe?g|svg|gif|tiff|bmp|ico/i.test(ext)) {
            return `assets/images/[name]-[hash][extname]`;
          } else if (/woff2?|ttf|otf|eot/i.test(ext)) {
            return `assets/fonts/[name]-[hash][extname]`;
          }
          
          return `assets/[name]-[hash][extname]`;
        },
        
        // Chunk file names
        chunkFileNames: 'assets/js/[name]-[hash].js',
        
        // Entry file names
        entryFileNames: 'assets/js/[name]-[hash].js',
      },
    },
    
    // Chunk size warning limit (in KB)
    chunkSizeWarningLimit: 1000,
    
    // Enable/disable CSS code splitting
    cssCodeSplit: true,
    
    // Target browsers
    target: 'es2015',
    
    // Report compressed size
    reportCompressedSize: true,
    
    // CommonJS options
    commonjsOptions: {
      transformMixedEsModules: true,
    },
  },

  // Optimization configuration
  optimizeDeps: {
    include: [
      'react',
      'react-dom',
      'react-router-dom',
      'axios',
      'three',
      '@react-three/fiber',
      '@react-three/drei',
      'zustand',
      'recharts',
      'date-fns',
    ],
    exclude: ['@testing-library/react'],
  },

  // CSS configuration
  css: {
    // CSS modules configuration
    modules: {
      localsConvention: 'camelCase',
    },
    
    // PostCSS configuration
    postcss: {
      plugins: [
        // Plugins will be loaded from postcss.config.js
      ],
    },
    
    // Preprocessor options
    preprocessorOptions: {
      scss: {
        additionalData: `@import "@/styles/variables.scss";`,
      },
    },
  },

  // Test configuration (for Vitest)
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/test/setup.js',
    css: true,
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'src/test/',
      ],
    },
  },

  // Environment variables prefix
  envPrefix: 'VITE_',

  // Base public path
  base: '/',

  // Define global constants
  define: {
    __APP_VERSION__: JSON.stringify(process.env.npm_package_version),
    __BUILD_TIME__: JSON.stringify(new Date().toISOString()),
  },

  // ESBuild configuration
  esbuild: {
    logOverride: { 'this-is-undefined-in-esm': 'silent' },
  },

  // Worker configuration
  worker: {
    format: 'es',
  },

  // JSON configuration
  json: {
    namedExports: true,
    stringify: false,
  },
})