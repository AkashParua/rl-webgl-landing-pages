import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: '/tests',
  timeout: 30_000,
  use: {
    baseURL: process.env.BASE_URL || 'http://page:80',
    headless: true,
    viewport: { width: 1280, height: 720 },
  },
  projects: [
    { name: 'chromium', use: { browserName: 'chromium' } },
  ],
});
