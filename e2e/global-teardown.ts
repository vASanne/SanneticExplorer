import { FullConfig } from '@playwright/test'
import { exec } from 'child_process'
import { promisify } from 'util'
import fs from 'fs'
import path from 'path'

const execAsync = promisify(exec)

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

async function globalTeardown(config: FullConfig) {
  console.log('🧹 Starting global teardown...')

  // Stop Docker Compose services
  console.log('🛑 Stopping Docker Compose services...')
  try {
    await execAsync('docker compose -p sannetic-explorer down', {
      cwd: findRepoRoot(process.cwd()),
    })
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