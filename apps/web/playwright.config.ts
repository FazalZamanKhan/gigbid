import { defineConfig } from '@playwright/test'

export default defineConfig({
  testDir: './tests/e2e',
  timeout: 90_000,
  expect: { timeout: 20_000 },
  fullyParallel: false,
  workers: 1,
  reporter: [['list'], ['html', { open: 'never' }]],
  use: {
    baseURL: 'http://127.0.0.1:8010',
    channel: process.env.CI ? undefined : 'chrome',
    trace: 'on-first-retry',
  },
  webServer: {
    command: `"${process.env.PYTHON || 'python'}" -m uvicorn apps.api.public:app --host 127.0.0.1 --port 8010`,
    cwd: '../..',
    url: 'http://127.0.0.1:8010/api/health',
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
  },
})
