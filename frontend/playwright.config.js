// @ts-check
const { defineConfig, devices } = require("@playwright/test");

const PYTHON = process.env.E2E_PYTHON || "python";
const CHROMIUM = process.env.PW_CHROMIUM_PATH; // optional: use a custom/system Chromium binary
const CI = !!process.env.CI;

/**
 * End-to-end tests drive the real UI against the real API:
 *   - backend: migrates + seeds a dedicated SQLite file (backend/e2e.db), then serves on :8000
 *   - frontend: Next.js dev server on :3000
 * Delete backend/e2e.db to reset the data between local runs.
 */
module.exports = defineConfig({
  testDir: "./e2e",
  timeout: 45_000,
  expect: { timeout: 10_000 },
  fullyParallel: false,
  workers: 1, // tests share one database
  retries: CI ? 1 : 0,
  reporter: CI ? [["github"], ["html", { open: "never" }]] : [["list"], ["html", { open: "never" }]],
  use: {
    baseURL: "http://localhost:3000",
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
    launchOptions: CHROMIUM
      ? { executablePath: CHROMIUM, args: ["--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage"] }
      : {},
  },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
  webServer: [
    {
      command: `${PYTHON} -m alembic upgrade head && ${PYTHON} -m app.seed && ${PYTHON} -m uvicorn app.main:app --port 8000`,
      cwd: "../backend",
      env: {
        DATABASE_URL: "sqlite:///./e2e.db",
        SECRET_KEY: "e2e-secret-key-that-is-long-enough-for-hs256",
        CORS_ORIGINS: "http://localhost:3000",
      },
      url: "http://localhost:8000/health",
      reuseExistingServer: !CI,
      timeout: 120_000,
    },
    {
      command: "npm run dev",
      url: "http://localhost:3000",
      reuseExistingServer: !CI,
      timeout: 120_000,
    },
  ],
});
