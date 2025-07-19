import { test, expect } from '@playwright/test'

test.describe('Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to dashboard
    await page.goto('/dashboard')
    
    // Wait for the page to load
    await page.waitForLoadState('networkidle')
  })

  test('should display dashboard with status cards', async ({ page }) => {
    // Wait for status cards to appear
    await expect(page.locator('text=System Dashboard')).toBeVisible()
    
    // Wait for loading to complete
    await expect(page.locator('text=Loading...')).not.toBeVisible({ timeout: 10000 })
    
    // Check that status cards are displayed
    await expect(page.locator('[data-testid="status-card"]')).toHaveCount(4)
    
    // Verify script names are present
    await expect(page.locator('text=update_critical.py')).toBeVisible()
    await expect(page.locator('text=update_data_optimized.py')).toBeVisible()
    await expect(page.locator('text=sync.py')).toBeVisible()
    await expect(page.locator('text=ai_health_check.py')).toBeVisible()
    
    // Check status indicators
    await expect(page.locator('text=OK')).toBeVisible()
    await expect(page.locator('text=FAIL')).toBeVisible()
    await expect(page.locator('text=UNKNOWN')).toBeVisible()
  })

  test('should display update logs table', async ({ page }) => {
    // Wait for table to load
    await expect(page.locator('text=Update Logs')).toBeVisible()
    
    // Check table headers
    await expect(page.locator('text=Timestamp')).toBeVisible()
    await expect(page.locator('text=Script')).toBeVisible()
    await expect(page.locator('text=Status')).toBeVisible()
    await expect(page.locator('text=Duration')).toBeVisible()
    await expect(page.locator('text=Message')).toBeVisible()
    
    // Check that table has data
    await expect(page.locator('table tbody tr')).toHaveCount(2)
  })

  test('should trigger script execution and show status changes', async ({ page }) => {
    // Wait for dashboard to load
    await expect(page.locator('text=System Dashboard')).toBeVisible()
    await expect(page.locator('text=Loading...')).not.toBeVisible({ timeout: 10000 })
    
    // Find the first "Run Now" button
    const runButton = page.locator('button:has-text("Run Now")').first()
    await expect(runButton).toBeVisible()
    
    // Click the "Run Now" button
    await runButton.click()
    
    // Wait for the button to show "Running..." state
    await expect(page.locator('button:has-text("Running...")')).toBeVisible({ timeout: 5000 })
    
    // Wait for the status to change back to "Run Now" (indicating completion)
    await expect(page.locator('button:has-text("Run Now")')).toBeVisible({ timeout: 15000 })
    
    // Verify that the script status was updated
    await expect(page.locator('text=OK')).toBeVisible()
  })

  test('should handle multiple script triggers', async ({ page }) => {
    // Wait for dashboard to load
    await expect(page.locator('text=System Dashboard')).toBeVisible()
    await expect(page.locator('text=Loading...')).not.toBeVisible({ timeout: 10000 })
    
    // Get all "Run Now" buttons
    const runButtons = page.locator('button:has-text("Run Now")')
    await expect(runButtons).toHaveCount(4)
    
    // Click multiple buttons in sequence
    for (let i = 0; i < 2; i++) {
      await runButtons.nth(i).click()
      
      // Wait for running state
      await expect(page.locator('button:has-text("Running...")')).toBeVisible({ timeout: 5000 })
      
      // Wait for completion
      await expect(page.locator('button:has-text("Run Now")')).toBeVisible({ timeout: 15000 })
    }
  })

  test('should auto-refresh data every 5 seconds', async ({ page }) => {
    // Wait for initial load
    await expect(page.locator('text=System Dashboard')).toBeVisible()
    await expect(page.locator('text=Loading...')).not.toBeVisible({ timeout: 10000 })
    
    // Get initial timestamp
    const initialTimestamp = await page.locator('[data-testid="last-updated"]').textContent()
    
    // Wait for auto-refresh (5 seconds + buffer)
    await page.waitForTimeout(6000)
    
    // Check that timestamp has updated
    const updatedTimestamp = await page.locator('[data-testid="last-updated"]').textContent()
    expect(updatedTimestamp).not.toBe(initialTimestamp)
  })

  test('should display error states gracefully', async ({ page }) => {
    // Mock API failure
    await page.route('**/updates/status', route => {
      route.fulfill({ status: 500, body: 'Internal Server Error' })
    })
    
    // Reload page to trigger error
    await page.reload()
    
    // Check that error message is displayed
    await expect(page.locator('text=Error loading dashboard data')).toBeVisible()
  })

  test('should handle empty data states', async ({ page }) => {
    // Mock empty response
    await page.route('**/updates/status', route => {
      route.fulfill({ 
        status: 200, 
        body: JSON.stringify([]),
        headers: { 'Content-Type': 'application/json' }
      })
    })
    
    await page.route('**/updates/latest', route => {
      route.fulfill({ 
        status: 200, 
        body: JSON.stringify([]),
        headers: { 'Content-Type': 'application/json' }
      })
    })
    
    // Reload page to trigger empty state
    await page.reload()
    
    // Check that empty state messages are displayed
    await expect(page.locator('text=No scripts found')).toBeVisible()
    await expect(page.locator('text=No update logs found')).toBeVisible()
  })

  test('should display performance metrics', async ({ page }) => {
    // Wait for dashboard to load
    await expect(page.locator('text=System Dashboard')).toBeVisible()
    await expect(page.locator('text=Loading...')).not.toBeVisible({ timeout: 10000 })
    
    // Check for performance indicators
    await expect(page.locator('text=Duration')).toBeVisible()
    await expect(page.locator('text=Last Run')).toBeVisible()
    
    // Verify duration formatting
    const durationElements = page.locator('text=/\\d+\\.\\d+s/')
    await expect(durationElements).toHaveCount(4)
  })

  test('should filter and sort update logs', async ({ page }) => {
    // Wait for table to load
    await expect(page.locator('text=Update Logs')).toBeVisible()
    
    // Check that logs are sorted by timestamp (newest first)
    const timestamps = await page.locator('table tbody tr td:first-child').allTextContents()
    expect(timestamps.length).toBeGreaterThan(1)
    
    // Verify timestamps are in descending order (newest first)
    for (let i = 0; i < timestamps.length - 1; i++) {
      const current = new Date(timestamps[i])
      const next = new Date(timestamps[i + 1])
      expect(current.getTime()).toBeGreaterThanOrEqual(next.getTime())
    }
  })

  test('should display relative timestamps', async ({ page }) => {
    // Wait for dashboard to load
    await expect(page.locator('text=System Dashboard')).toBeVisible()
    await expect(page.locator('text=Loading...')).not.toBeVisible({ timeout: 10000 })
    
    // Check for relative timestamp formatting
    const relativeTimeElements = page.locator('text=/ago|just now|minutes|hours/')
    await expect(relativeTimeElements).toHaveCount(4)
  })

  test('should show script details on hover', async ({ page }) => {
    // Wait for dashboard to load
    await expect(page.locator('text=System Dashboard')).toBeVisible()
    await expect(page.locator('text=Loading...')).not.toBeVisible({ timeout: 10000 })
    
    // Hover over a status card
    const statusCard = page.locator('[data-testid="status-card"]').first()
    await statusCard.hover()
    
    // Check for tooltip or additional details
    await expect(page.locator('[data-testid="tooltip"]')).toBeVisible({ timeout: 2000 })
  })
})

test.describe('Dashboard Visual Regression', () => {
  test('dashboard baseline screenshot', async ({ page }) => {
    await page.goto('/dashboard')
    await page.waitForLoadState('networkidle')
    
    // Wait for loading to complete
    await expect(page.locator('text=Loading...')).not.toBeVisible({ timeout: 10000 })
    
    // Take screenshot of the entire dashboard
    await expect(page).toHaveScreenshot('dashboard-baseline.png', {
      fullPage: true,
      animations: 'disabled'
    })
  })

  test('dashboard status cards screenshot', async ({ page }) => {
    await page.goto('/dashboard')
    await page.waitForLoadState('networkidle')
    
    // Wait for loading to complete
    await expect(page.locator('text=Loading...')).not.toBeVisible({ timeout: 10000 })
    
    // Take screenshot of status cards section
    const statusCardsSection = page.locator('[data-testid="status-cards-section"]')
    await expect(statusCardsSection).toHaveScreenshot('dashboard-status-cards.png', {
      animations: 'disabled'
    })
  })

  test('dashboard table screenshot', async ({ page }) => {
    await page.goto('/dashboard')
    await page.waitForLoadState('networkidle')
    
    // Wait for loading to complete
    await expect(page.locator('text=Loading...')).not.toBeVisible({ timeout: 10000 })
    
    // Take screenshot of update logs table
    const tableSection = page.locator('[data-testid="update-logs-table"]')
    await expect(tableSection).toHaveScreenshot('dashboard-table.png', {
      animations: 'disabled'
    })
  })

  test('dashboard running state screenshot', async ({ page }) => {
    await page.goto('/dashboard')
    await page.waitForLoadState('networkidle')
    
    // Wait for loading to complete
    await expect(page.locator('text=Loading...')).not.toBeVisible({ timeout: 10000 })
    
    // Click a "Run Now" button
    const runButton = page.locator('button:has-text("Run Now")').first()
    await runButton.click()
    
    // Wait for running state
    await expect(page.locator('button:has-text("Running...")')).toBeVisible({ timeout: 5000 })
    
    // Take screenshot of running state
    await expect(page).toHaveScreenshot('dashboard-running-state.png', {
      fullPage: true,
      animations: 'disabled'
    })
  })

  test('dashboard error state screenshot', async ({ page }) => {
    // Mock API failure
    await page.route('**/updates/status', route => {
      route.fulfill({ status: 500, body: 'Internal Server Error' })
    })
    
    await page.goto('/dashboard')
    await page.waitForLoadState('networkidle')
    
    // Wait for error to appear
    await expect(page.locator('text=Error loading dashboard data')).toBeVisible()
    
    // Take screenshot of error state
    await expect(page).toHaveScreenshot('dashboard-error-state.png', {
      fullPage: true,
      animations: 'disabled'
    })
  })

  test('dashboard empty state screenshot', async ({ page }) => {
    // Mock empty response
    await page.route('**/updates/status', route => {
      route.fulfill({ 
        status: 200, 
        body: JSON.stringify([]),
        headers: { 'Content-Type': 'application/json' }
      })
    })
    
    await page.route('**/updates/latest', route => {
      route.fulfill({ 
        status: 200, 
        body: JSON.stringify([]),
        headers: { 'Content-Type': 'application/json' }
      })
    })
    
    await page.goto('/dashboard')
    await page.waitForLoadState('networkidle')
    
    // Wait for empty state
    await expect(page.locator('text=No scripts found')).toBeVisible()
    
    // Take screenshot of empty state
    await expect(page).toHaveScreenshot('dashboard-empty-state.png', {
      fullPage: true,
      animations: 'disabled'
    })
  })
}) 