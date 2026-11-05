import { chromium, FullConfig } from '@playwright/test'
import { exec } from 'child_process'
import { promisify } from 'util'
import fs from 'fs'
import path from 'path'

const execAsync = promisify(exec)
const frontendUrl = process.env.FRONTEND_URL || 'http://localhost:13300'
const backendUrl = process.env.PUBLIC_API_URL || 'http://localhost:13800'

function findRepoRoot(start: string): string {
  let dir = start
  for (let i = 0; i < 4; i++) {
    if (fs.existsSync(path.join(dir, 'docker-compose.yml'))) {
      return dir
    }
    const parent = path.dirname(dir)
    if (parent === dir) break
    dir = parent
  }
  return start
}

async function globalSetup(config: FullConfig) {
  console.log('🚀 Starting global setup...')

  // Start Docker Compose services
  console.log('📦 Starting Docker Compose services...')
  try {
    await execAsync('docker compose -p sannetic-explorer up -d', {
      cwd: findRepoRoot(process.cwd()),
    })
    console.log('✅ Docker Compose services started')
  } catch (error) {
    console.error('❌ Failed to start Docker Compose services:', error)
    throw error
  }

  // Wait for services to be ready
  console.log('⏳ Waiting for services to be ready...')
  await waitForServices()

  // Verify the application is accessible
  console.log('🔍 Verifying application accessibility...')
  const browser = await chromium.launch()
  const page = await browser.newPage()
  
  try {
    await page.goto(frontendUrl, { waitUntil: 'networkidle' })
    console.log('✅ Frontend is accessible')
    
    // Test backend health
    const response = await page.request.get(`${backendUrl}/health`)
    if (response.ok()) {
      console.log('✅ Backend is healthy')
    } else {
      throw new Error('Backend health check failed')
    }
  } catch (error) {
    console.error('❌ Application verification failed:', error)
    await browser.close()
    throw error
  }

  await browser.close()
  console.log('✅ Global setup completed successfully')
}

async function waitForServices(): Promise<void> {
  const maxAttempts = 30
  const delay = 2000 // 2 seconds

  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    console.log(`⏳ Service readiness check ${attempt}/${maxAttempts}...`)
    
    try {
      // Check if frontend is responding
      const frontendResponse = await fetch(frontendUrl)
      if (!frontendResponse.ok) {
        throw new Error('Frontend not ready')
      }

      // Check if backend is responding
      const backendResponse = await fetch(`${backendUrl}/health`)
      if (!backendResponse.ok) {
        throw new Error('Backend not ready')
      }

      console.log('✅ All services are ready!')
      return
    } catch (error) {
      if (attempt === maxAttempts) {
        console.error('❌ Services failed to become ready after maximum attempts')
        throw error
      }
      
      console.log(`⏳ Services not ready yet, waiting ${delay}ms...`)
      await new Promise(resolve => setTimeout(resolve, delay))
    }
  }
}

export default globalSetup 