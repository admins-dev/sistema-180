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
            }
        }
    }
});
