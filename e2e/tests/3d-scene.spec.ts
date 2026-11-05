import { test, expect } from "@playwright/test";

test.describe("Showcase", () => {
  test("draws the orrery and opens a planet from the rail", async ({
    page,
  }) => {
    await page.goto("/3d");
    await expect(page.getByText("Sannetic Explorer").first()).toBeVisible();
    await expect(page.locator("canvas")).toBeVisible();
    await page.getByRole("button", { name: "Erde" }).click();
    await expect(page.getByTestId("info-panel")).toContainText("Erde");
    await expect(
      page.getByRole("button", { name: "Umlaufbahn abspielen" })
    ).toBeVisible();
    await page.getByRole("button", { name: "Umlaufbahn abspielen" }).click();
    await expect(
      page.getByRole("button", { name: "Animation anhalten" })
    ).toBeVisible();
    await page.getByRole("button", { name: "Animation anhalten" }).click();
    await page.getByTestId("view-system").click();
  });

  test("uses the same orrery on the home page", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByRole("button", { name: "Jupiter" })).toBeVisible();
    await expect(page.locator("canvas")).toBeVisible();
  });
});
