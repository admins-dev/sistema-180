import { defineConfig } from 'vite';

export default defineConfig({
    server: {
        proxy: {
            '/api/freepik': {
                target: 'https://api.freepik.com',
                changeOrigin: true,
                rewrite: (path) => path.replace(/^\/api\/freepik/, ''),
                secure: true,
            },
        },
    },
});
