import { test, expect } from '@playwright/test'

test.describe('Live data', () => {
  test('shows the browser API and a way back to the orrery', async ({ page }) => {
    await page.goto('/dashboard')
    await expect(page.getByRole('heading', { name: 'System status' })).toBeVisible()
    await expect(page.getByText('Browser API')).toBeVisible()
    await expect(page.getByRole('link', { name: 'Open the solar system' })).toBeVisible()
  })
})
