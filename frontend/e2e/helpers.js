export const PASSWORD = process.env.E2E_PASSWORD || "Demo#12345";

/** Submit the login form without waiting for the outcome (use for negative tests). */
export async function attemptLogin(page, username, password = PASSWORD) {
  await page.goto("/");
  await page.getByLabel("Username").fill(username);
  await page.getByLabel("Password").fill(password);
  await page.getByRole("button", { name: "Sign in" }).click();
}

/** Log in and wait until the dashboard is shown (so the session is stored before navigating on). */
export async function login(page, username, password = PASSWORD) {
  await attemptLogin(page, username, password);
  await page.waitForURL("**/dashboard");
}

export async function logout(page) {
  await page.getByRole("button", { name: "Log out" }).click();
  await page.waitForURL("/");
}

/** Valid NPWPD (^[A-Z0-9]{6,20}$) that is unique per run. */
export const uniqueNpwpd = () => `E2E${Date.now().toString().slice(-9)}`;
