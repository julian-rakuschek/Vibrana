import tailwindcss from '@tailwindcss/vite';
import {sveltekit} from '@sveltejs/kit/vite';
import {defineConfig} from 'vite';
import path from 'path';

export default defineConfig({
    plugins: [tailwindcss(), sveltekit()],
    resolve: {
        alias: {
            '@components': path.resolve('./src/components'),
            '@lib': path.resolve('./src/lib'),
        }
    },
    server: {
        proxy: {
            '/api': {
                target: 'http://127.0.0.1:5000'
            },
        },
    },
    preview: {
        proxy: {
            '/api': {
                target: 'http://127.0.0.1:5000',
            },
        }
    }
});
