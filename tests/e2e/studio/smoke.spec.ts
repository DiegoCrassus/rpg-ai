import { expect, test } from "@playwright/test";

test.describe("Studio Service critical routes", () => {
  test("dashboard renders", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByRole("heading", { name: "Dashboard", level: 1 })).toBeVisible();
    await expect(page.getByText("Enforcement (fail-closed)")).toBeVisible({
      timeout: 15_000,
    });
  });

  test("workflows canvas route renders", async ({ page }) => {
    await page.goto("/workflows");
    await expect(page.getByRole("heading", { name: "Workflow", level: 1 })).toBeVisible();
  });

  test("observability timeline route renders", async ({ page }) => {
    await page.goto("/observability");
    await expect(page.getByRole("heading", { name: "Observability", level: 1 })).toBeVisible();
  });
});
