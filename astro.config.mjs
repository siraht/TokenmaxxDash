import { defineConfig } from 'astro/config';

export default defineConfig({
  output: 'static',
  site: process.env.SITE_URL || 'https://coding-plan-index.pages.dev',
  trailingSlash: 'never',
  build: {
    format: 'directory'
  }
});
