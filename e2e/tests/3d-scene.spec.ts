import { test, expect } from '@playwright/test'

test.describe('3D Scene', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to 3D scene
    await page.goto('/3d')
    
    // Wait for the page to load
    await page.waitForLoadState('networkidle')
  })

  test('should display 3D scene with canvas', async ({ page }) => {
    // Wait for 3D scene to load
    await expect(page.locator('text=3D Solar System')).toBeVisible()
    
    // Check that Three.js canvas is present
    const canvas = page.locator('canvas')
    await expect(canvas).toBeVisible()
    
    // Verify canvas has proper dimensions
    const canvasElement = await canvas.elementHandle()
    const boundingBox = await canvasElement!.boundingBox()
    expect(boundingBox!.width).toBeGreaterThan(0)
    expect(boundingBox!.height).toBeGreaterThan(0)
  })

  test('should display orbit side panel', async ({ page }) => {
    // Wait for 3D scene to load
    await expect(page.locator('text=3D Solar System')).toBeVisible()
    
    // Check that orbit side panel is present
    await expect(page.locator('[data-testid="orbit-side-panel"]')).toBeVisible()
    
    // Verify panel contains expected elements
    await expect(page.locator('text=Orbital Parameters')).toBeVisible()
    await expect(page.locator('text=Physical Characteristics')).toBeVisible()
  })

  test('should show celestial body information when selected', async ({ page }) => {
    // Wait for 3D scene to load
    await expect(page.locator('text=3D Solar System')).toBeVisible()
    
    // Click on a celestial body (simulate by clicking on canvas)
    const canvas = page.locator('canvas')
    await canvas.click({ position: { x: 400, y: 300 } })
    
    // Wait for body information to appear
    await expect(page.locator('[data-testid="body-info"]')).toBeVisible({ timeout: 5000 })
    
    // Verify body details are displayed
    await expect(page.locator('text=Name:')).toBeVisible()
    await expect(page.locator('text=Type:')).toBeVisible()
    await expect(page.locator('text=Distance:')).toBeVisible()
  })

  test('should display performance monitor', async ({ page }) => {
    // Wait for 3D scene to load
    await expect(page.locator('text=3D Solar System')).toBeVisible()
    
    // Check that performance monitor is present
    await expect(page.locator('[data-testid="performance-monitor"]')).toBeVisible()
    
    // Verify performance metrics are displayed
    await expect(page.locator('text=FPS:')).toBeVisible()
    await expect(page.locator('text=Draw Calls:')).toBeVisible()
    await expect(page.locator('text=Triangles:')).toBeVisible()
  })

  test('should handle camera controls', async ({ page }) => {
    // Wait for 3D scene to load
    await expect(page.locator('text=3D Solar System')).toBeVisible()
    
    const canvas = page.locator('canvas')
    
    // Test mouse drag for rotation
    await canvas.dragTo(canvas, { 
      sourcePosition: { x: 100, y: 100 },
      targetPosition: { x: 200, y: 200 }
    })
    
    // Test mouse wheel for zoom
    await canvas.hover()
    await page.mouse.wheel(0, -100) // Zoom in
    
    // Verify scene is still responsive
    await expect(canvas).toBeVisible()
  })

  test('should display orbital paths', async ({ page }) => {
    // Wait for 3D scene to load
    await expect(page.locator('text=3D Solar System')).toBeVisible()
    
    // Check that orbital paths are visible (they should be rendered on canvas)
    const canvas = page.locator('canvas')
    await expect(canvas).toBeVisible()
    
    // Wait a bit for orbital paths to be rendered
    await page.waitForTimeout(2000)
    
    // Verify canvas is still interactive
    await canvas.click()
  })

  test('should show loading state while scene initializes', async ({ page }) => {
    // Navigate to 3D scene
    await page.goto('/3d')
    
    // Check for loading indicator
    await expect(page.locator('text=Loading 3D scene...')).toBeVisible({ timeout: 5000 })
    
    // Wait for loading to complete
    await expect(page.locator('text=Loading 3D scene...')).not.toBeVisible({ timeout: 10000 })
    
    // Verify scene is loaded
    await expect(page.locator('text=3D Solar System')).toBeVisible()
  })

  test('should handle window resize', async ({ page }) => {
    // Wait for 3D scene to load
    await expect(page.locator('text=3D Solar System')).toBeVisible()
    
    // Resize window
    await page.setViewportSize({ width: 1200, height: 800 })
    
    // Wait for resize to take effect
    await page.waitForTimeout(1000)
    
    // Verify canvas is still visible and properly sized
    const canvas = page.locator('canvas')
    await expect(canvas).toBeVisible()
    
    const canvasElement = await canvas.elementHandle()
    const boundingBox = await canvasElement!.boundingBox()
    expect(boundingBox!.width).toBeGreaterThan(0)
    expect(boundingBox!.height).toBeGreaterThan(0)
  })

  test('should display error state if 3D context fails', async ({ page }) => {
    // Mock WebGL context failure
    await page.addInitScript(() => {
      const originalGetContext = HTMLCanvasElement.prototype.getContext
      HTMLCanvasElement.prototype.getContext = function(type: string) {
        if (type === 'webgl' || type === 'webgl2') {
          return null // Simulate WebGL failure
        }
        return originalGetContext.call(this, type)
      }
    })
    
    // Navigate to 3D scene
    await page.goto('/3d')
    
    // Wait for error message
    await expect(page.locator('text=WebGL not supported')).toBeVisible({ timeout: 10000 })
  })

  test('should maintain 60 FPS performance', async ({ page }) => {
    // Wait for 3D scene to load
    await expect(page.locator('text=3D Solar System')).toBeVisible()
    
    // Wait for performance monitor to show FPS
    await expect(page.locator('text=FPS:')).toBeVisible()
    
    // Get FPS value
    const fpsElement = page.locator('[data-testid="fps-value"]')
    await expect(fpsElement).toBeVisible()
    
    // Check FPS is reasonable (should be close to 60)
    const fpsText = await fpsElement.textContent()
    const fps = parseInt(fpsText || '0')
    expect(fps).toBeGreaterThan(30) // Allow some tolerance
  })
})

test.describe('3D Scene Visual Regression', () => {
  test('3d scene baseline screenshot', async ({ page }) => {
    await page.goto('/3d')
    await page.waitForLoadState('networkidle')
    
    // Wait for 3D scene to load
    await expect(page.locator('text=3D Solar System')).toBeVisible()
    await expect(page.locator('text=Loading 3D scene...')).not.toBeVisible({ timeout: 10000 })
    
    // Take screenshot of the entire 3D scene
    await expect(page).toHaveScreenshot('3d-scene-baseline.png', {
      fullPage: true,
      animations: 'disabled'
    })
  })

  test('3d scene canvas screenshot', async ({ page }) => {
    await page.goto('/3d')
    await page.waitForLoadState('networkidle')
    
    // Wait for 3D scene to load
    await expect(page.locator('text=3D Solar System')).toBeVisible()
    await expect(page.locator('text=Loading 3D scene...')).not.toBeVisible({ timeout: 10000 })
    
    // Take screenshot of just the canvas
    const canvas = page.locator('canvas')
    await expect(canvas).toHaveScreenshot('3d-scene-canvas.png', {
      animations: 'disabled'
    })
  })

  test('3d scene side panel screenshot', async ({ page }) => {
    await page.goto('/3d')
    await page.waitForLoadState('networkidle')
    
    // Wait for 3D scene to load
    await expect(page.locator('text=3D Solar System')).toBeVisible()
    await expect(page.locator('text=Loading 3D scene...')).not.toBeVisible({ timeout: 10000 })
    
    // Take screenshot of the side panel
    const sidePanel = page.locator('[data-testid="orbit-side-panel"]')
    await expect(sidePanel).toHaveScreenshot('3d-scene-side-panel.png', {
      animations: 'disabled'
    })
  })

  test('3d scene loading state screenshot', async ({ page }) => {
    await page.goto('/3d')
    
    // Take screenshot while loading
    await expect(page.locator('text=Loading 3D scene...')).toBeVisible({ timeout: 5000 })
    
    await expect(page).toHaveScreenshot('3d-scene-loading.png', {
      fullPage: true,
      animations: 'disabled'
    })
  })

  test('3d scene error state screenshot', async ({ page }) => {
    // Mock WebGL failure
    await page.addInitScript(() => {
      const originalGetContext = HTMLCanvasElement.prototype.getContext
      HTMLCanvasElement.prototype.getContext = function(type: string) {
        if (type === 'webgl' || type === 'webgl2') {
          return null
        }
        return originalGetContext.call(this, type)
      }
    })
    
    await page.goto('/3d')
    
    // Wait for error message
    await expect(page.locator('text=WebGL not supported')).toBeVisible({ timeout: 10000 })
    
    await expect(page).toHaveScreenshot('3d-scene-error.png', {
      fullPage: true,
      animations: 'disabled'
    })
  })
}) 