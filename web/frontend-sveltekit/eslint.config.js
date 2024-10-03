import eslint from '@eslint/js';
import prettier from 'eslint-config-prettier';
import svelte from 'eslint-plugin-svelte';
import globals from 'globals';
import tseslint from 'typescript-eslint';

export default tseslint.config(
	eslint.configs.recommended,
	...tseslint.configs.recommended,
	...svelte.configs['flat/recommended'],
	prettier,
	...svelte.configs['flat/prettier'],
	{
		languageOptions: {
			globals: {
				...globals.browser,
				...globals.node
			}
		}
	},
	{
		files: ['**/*.svelte'],
		languageOptions: {
			parserOptions: {
				parser: tseslint.parser
			}
		}
	},
	{
		ignores: ['build/', '.svelte-kit/', 'dist/']
	},
	{
		// Disable all A11y (Accessibility) warnings
		rules: {
			'svelte/a11y-alt-text': 'off',
			'svelte/a11y-aria-label': 'off',
			'svelte/a11y-controls': 'off',
			'svelte/a11y-click-events-have-key-events': 'off',
			'svelte/a11y-form-has-submit': 'off',
			'svelte/a11y-hidden': 'off',
			'svelte/a11y-img-redundant-alt': 'off',
			'svelte/a11y-interactive-supports-focus': 'off',
			'svelte/a11y-label-has-associated-control': 'off',
			'svelte/a11y-media-has-caption': 'off',
			'svelte/a11y-missing-content': 'off',
			'svelte/a11y-mouse-events-have-key-events': 'off',
			'svelte/a11y-no-onchange': 'off',
			'svelte/a11y-role-has-required-aria-props': 'off',
			'svelte/a11y-role-supports-aria-props': 'off',
			'svelte/a11y-scope': 'off',
			'svelte/a11y-tabindex-no-positive': 'off'
		}
	}
);
