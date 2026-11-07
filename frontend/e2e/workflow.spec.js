import { expect, test } from "@playwright/test";
import { login, logout, uniqueNpwpd } from "./helpers";

test("officer registers a taxpayer and records a large transaction; auditor clears the flag", async ({ page }) => {
  const npwpd = uniqueNpwpd();
  const name = `E2E Hotel ${npwpd}`;
  const row = () => page.getByRole("row", { name: new RegExp(name) });

  await test.step("officer registers a taxpayer", async () => {
    await login(page, "officer");
    await page.goto("/taxpayers");
    await page.getByPlaceholder("NPWPD (e.g. HTL000009)").fill(npwpd);
    await page.getByPlaceholder("Name", { exact: true }).fill(name);
    await page.getByRole("button", { name: "Add taxpayer" }).click();
    await expect(row()).toBeVisible();
  });

  await test.step("duplicate NPWPD is rejected", async () => {
    await page.getByPlaceholder("NPWPD (e.g. HTL000009)").fill(npwpd);
    await page.getByPlaceholder("Name", { exact: true }).fill(`${name} copy`);
    await page.getByRole("button", { name: "Add taxpayer" }).click();
    await expect(page.getByRole("alert").filter({ hasText: "NPWPD already registered" })).toBeVisible();
  });

  await test.step("officer records a transaction above the threshold", async () => {
    await page.goto("/transactions");
    await page.getByRole("combobox").first().selectOption({ label: name });
    await page.getByPlaceholder("Amount (IDR)").fill("60000000");
    await page.getByRole("button", { name: "Record transaction" }).click();
    await expect(row()).toContainText("above_threshold");
    await expect(row()).toContainText(/6\.000\.000/); // 10% hotel tax
    await expect(page.getByRole("button", { name: "Clear flag" })).toHaveCount(0); // officers cannot review
  });

  await test.step("auditor reviews and clears the flag", async () => {
    await logout(page);
    await login(page, "auditor");
    await page.goto("/transactions");
    await page.getByLabel("Show flagged only").check();
    await expect(row()).toBeVisible();
    await row().getByRole("button", { name: "Clear flag" }).click();
    await expect(row()).toHaveCount(0);
  });

  await test.step("the audit trail records the review", async () => {
    await page.goto("/audit");
    await expect(page.getByRole("row", { name: /clear_flag/ }).first()).toBeVisible();
    await expect(page.getByRole("row", { name: /auditor.*clear_flag/ }).first()).toBeVisible();
  });
});
