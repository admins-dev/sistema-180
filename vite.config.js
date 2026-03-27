import { defineConfig } from 'vite';

export default defineConfig({
    server: {
        port: 5173,
        proxy: {
            '/api/freepik': {
                target: 'https://api.freepik.com',
                changeOrigin: true,
                rewrite: (path) => path.replace(/^\/api\/freepik/, ''),
                headers: { Origin: 'https://api.freepik.com' }
            },
            '/api': { target: 'http://localhost:3000', changeOrigin: true },
            '/webhook': { target: 'http://localhost:3000', changeOrigin: true },
            '/admin': { target: 'http://localhost:3000', changeOrigin: true },
            '/create-checkout-session': { target: 'http://localhost:3000', changeOrigin: true }
        }
    }
});
