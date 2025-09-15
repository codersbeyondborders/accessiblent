import adapter from '@sveltejs/adapter-auto';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

const config = {
  // tailwind/postcss works via vitePreprocess
  preprocess: vitePreprocess(),

  kit: {
    adapter: adapter()
    // If you need a base path behind a subdir, add: paths: { base: '/subdir' }
  }
};

export default config;
