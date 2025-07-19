import { test, expect } from '@playwright/test';

test.describe('Solar System Canvas', () => {
  test('renders canvas and at least one sphere', async ({ page }) => {
    await page.goto('/3d');
    // Check for canvas tag
    const canvas = await page.$('canvas');
    expect(canvas).not.toBeNull();
    // Check for at least one sphere mesh (data-testid="celestial-sphere")
    const spheres = await page.$$('[data-testid="celestial-sphere"]');
    expect(spheres.length).toBeGreaterThan(0);
  });
}); 