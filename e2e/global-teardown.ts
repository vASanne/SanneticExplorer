import { FullConfig } from '@playwright/test'
import { exec } from 'child_process'
import { promisify } from 'util'

const execAsync = promisify(exec)

async function globalTeardown(config: FullConfig) {
  console.log('🧹 Starting global teardown...')

  // Stop Docker Compose services
  console.log('🛑 Stopping Docker Compose services...')
  try {
    await execAsync('docker-compose down')
    console.log('✅ Docker Compose services stopped')
  } catch (error) {
    console.error('❌ Failed to stop Docker Compose services:', error)
    // Don't throw error during teardown to avoid masking test failures
  }

  // Clean up test artifacts
  console.log('🗑️ Cleaning up test artifacts...')
  try {
    await execAsync('rm -rf test-results/')
    console.log('✅ Test artifacts cleaned up')
  } catch (error) {
    console.error('❌ Failed to clean up test artifacts:', error)
  }

  console.log('✅ Global teardown completed')
}

export default globalTeardown 