import type {Config} from 'tailwindcss'

const config: Config = {
    content: [
        './index.html',
        './src/**/*.{js,ts,jsx,tsx}',
        './src/pages/**/*.{js,ts,jsx,tsx}',
        './src/components/**/*.{js,ts,jsx,tsx}',
    ],
    plugins: [],
    theme: {
        extend: {
            colors: {
                "indigo-100-accent": "#8c9eff",
                "indigo-200-accent": "#536dfe",
                "indigo-400-accent": "#3d5afe",
                "indigo-700-accent": "#304ffe",
                "teal-100-accent": "#a7ffeb",
                "teal-200-accent": "#64ffda",
                "teal-400-accent": "#1de9b6",
                "teal-700-accent": "#00bfa5",
            }
        }
    }
}
export default config