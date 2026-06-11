import { expect, test } from "@playwright/test";

test.describe("RPG Platform MVP journeys — public routes (journey 1 auth shell)", () => {
  test("login page renders PT-BR", async ({ page }) => {
    await page.goto("/login");
    await expect(page.getByRole("heading", { name: "Entrar" })).toBeVisible();
    await expect(page.getByRole("button", { name: "Continuar com Google" })).toBeVisible();
    await expect(page.getByRole("link", { name: "Cadastre-se" })).toBeVisible();
  });

  test("register page renders PT-BR", async ({ page }) => {
    await page.goto("/register");
    await expect(page.getByRole("heading", { name: "Criar conta" })).toBeVisible();
  });

  test("reset password page renders", async ({ page }) => {
    await page.goto("/reset-password");
    await expect(page.getByRole("heading", { name: "Redefinir senha" })).toBeVisible();
  });

  test("unauthenticated /mesas redirects to login", async ({ page }) => {
    await page.goto("/mesas");
    await expect(page).toHaveURL(/\/login$/);
  });
});

test.describe("RPG Platform MVP journeys — invite shell (journey 3 partial)", () => {
  test("accept invite page prompts login without session", async ({ page }) => {
    await page.goto("/accept-invite");
    await expect(page.getByText("Faça login para aceitar o convite.")).toBeVisible();
  });
});
