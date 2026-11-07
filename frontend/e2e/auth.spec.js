import { expect, test } from "@playwright/test";
import { attemptLogin, login, logout } from "./helpers";

test.describe("authentication and access control", () => {
  test("wrong password shows an error and stays on the login page", async ({ page }) => {
    await attemptLogin(page, "officer", "definitely-wrong");
    await expect(page.getByRole("alert").filter({ hasText: "Incorrect username or password" })).toBeVisible();
    await expect(page).toHaveURL("/");
  });

  test("protected pages redirect anonymous visitors to login", async ({ page }) => {
    await page.goto("/dashboard");
    await expect(page).toHaveURL("/");
    await expect(page.getByRole("heading", { name: "TaxWatch" })).toBeVisible();
  });

  test("officer sees the dashboard but not the audit trail", async ({ page }) => {
    await login(page, "officer");
    await expect(page.getByRole("heading", { name: "Dashboard" })).toBeVisible();
    await expect(page.getByText("Flagged for review")).toBeVisible();
    await expect(page.getByRole("link", { name: "Audit trail" })).toHaveCount(0);
  });

  test("auditor can open the audit trail", async ({ page }) => {
    await login(page, "auditor");
    await page.getByRole("link", { name: "Audit trail" }).click();
    await expect(page.getByRole("heading", { name: /Audit trail/ })).toBeVisible();
  });

  test("auditor is read-only on taxpayers and transactions", async ({ page }) => {
    await login(page, "auditor");
    await page.goto("/taxpayers");
    await expect(page.getByRole("heading", { name: /Taxpayers/ })).toBeVisible();
    await expect(page.getByRole("button", { name: "Add taxpayer" })).toHaveCount(0);
    await page.goto("/transactions");
    await expect(page.getByRole("heading", { name: /Transactions/ })).toBeVisible();
    await expect(page.getByRole("button", { name: "Record transaction" })).toHaveCount(0);
  });

  test("logout ends the session", async ({ page }) => {
    await login(page, "officer");
    await expect(page.getByRole("heading", { name: "Dashboard" })).toBeVisible();
    await logout(page);
    await expect(page).toHaveURL("/");
    await page.goto("/dashboard");
    await expect(page).toHaveURL("/");
  });

  test("layout fits a phone-sized screen without horizontal page scroll", async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 800 });
    await login(page, "officer");
    await expect(page.getByRole("heading", { name: "Dashboard" })).toBeVisible();
    const overflow = await page.evaluate(
      () => document.documentElement.scrollWidth - document.documentElement.clientWidth
    );
    expect(overflow).toBeLessThanOrEqual(1);
  });
});
