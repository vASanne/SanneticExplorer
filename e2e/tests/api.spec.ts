import { test, expect } from '@playwright/test'

test.describe('API Integration', () => {
  const baseURL = process.env.PUBLIC_API_URL || 'http://localhost:13800'

  test('should return health status', async ({ request }) => {
    const response = await request.get(`${baseURL}/health`)
    expect(response.ok()).toBeTruthy()
    
    const data = await response.json()
    expect(data.status).toBe('healthy')
  })

  test('should return update status', async ({ request }) => {
    const response = await request.get(`${baseURL}/updates/status`)
    expect(response.ok()).toBeTruthy()
    
    const data = await response.json()
    expect(Array.isArray(data)).toBeTruthy()
    
    if (data.length > 0) {
      const script = data[0]
      expect(script).toHaveProperty('script_name')
      expect(script).toHaveProperty('status')
      expect(script).toHaveProperty('last_run')
    }
  })

  test('should return latest update logs', async ({ request }) => {
    const response = await request.get(`${baseURL}/updates/latest`)
    expect(response.ok()).toBeTruthy()
    
    const data = await response.json()
    expect(Array.isArray(data)).toBeTruthy()
    
    if (data.length > 0) {
      const log = data[0]
      expect(log).toHaveProperty('timestamp')
      expect(log).toHaveProperty('script_name')
      expect(log).toHaveProperty('status')
      expect(log).toHaveProperty('duration')
      expect(log).toHaveProperty('message')
    }
  })

  test('should return celestial bodies', async ({ request }) => {
    const response = await request.get(`${baseURL}/bodies`)
    expect(response.ok()).toBeTruthy()
    
    const data = await response.json()
    expect(Array.isArray(data)).toBeTruthy()
    
    if (data.length > 0) {
      const body = data[0]
      expect(body).toHaveProperty('id')
      expect(body).toHaveProperty('name')
      expect(body).toHaveProperty('type')
    }
  })

  test('should return specific celestial body', async ({ request }) => {
    // First get all bodies to find a valid ID
    const bodiesResponse = await request.get(`${baseURL}/bodies`)
    const bodies = await bodiesResponse.json()
    
    if (bodies.length > 0) {
      const bodyId = bodies[0].id
      const response = await request.get(`${baseURL}/bodies/${bodyId}`)
      expect(response.ok()).toBeTruthy()
      
      const data = await response.json()
      expect(data.id).toBe(bodyId)
      expect(data).toHaveProperty('name')
      expect(data).toHaveProperty('type')
    }
  })

  test('should handle invalid body ID', async ({ request }) => {
    const response = await request.get(`${baseURL}/bodies/invalid-id`)
    expect(response.status()).toBe(404)
  })

  test('should return planets', async ({ request }) => {
    const response = await request.get(`${baseURL}/bodies/planets`)
    expect(response.ok()).toBeTruthy()
    
    const data = await response.json()
    expect(Array.isArray(data)).toBeTruthy()
    
    if (data.length > 0) {
      const planet = data[0]
      expect(planet.type).toBe('planet')
    }
  })

  test('should return moons', async ({ request }) => {
    const response = await request.get(`${baseURL}/bodies/moons`)
    expect(response.ok()).toBeTruthy()
    
    const data = await response.json()
    expect(Array.isArray(data)).toBeTruthy()
    
    if (data.length > 0) {
      const moon = data[0]
      expect(moon.type).toBe('moon')
    }
  })

  test('should return stars', async ({ request }) => {
    const response = await request.get(`${baseURL}/bodies/stars`)
    expect(response.ok()).toBeTruthy()
    
    const data = await response.json()
    expect(Array.isArray(data)).toBeTruthy()
    
    if (data.length > 0) {
      const star = data[0]
      expect(star.type).toBe('star')
    }
  })

  test('should handle CORS headers', async ({ request }) => {
    const response = await request.get(`${baseURL}/health`)
    expect(response.headers()['access-control-allow-origin']).toBeDefined()
  })

  test('should handle OPTIONS requests', async ({ request }) => {
    const response = await request.options(`${baseURL}/bodies`)
    expect(response.status()).toBe(200)
    expect(response.headers()['access-control-allow-methods']).toBeDefined()
  })

  test('should return proper content type', async ({ request }) => {
    const response = await request.get(`${baseURL}/bodies`)
    expect(response.headers()['content-type']).toContain('application/json')
  })

  test('should handle rate limiting', async ({ request }) => {
    // Make multiple rapid requests
    const promises = Array.from({ length: 10 }, () => 
      request.get(`${baseURL}/health`)
    )
    
    const responses = await Promise.all(promises)
    
    // All requests should succeed (no rate limiting implemented yet)
    responses.forEach(response => {
      expect(response.ok()).toBeTruthy()
    })
  })

  test('should handle concurrent requests', async ({ request }) => {
    // Make concurrent requests to different endpoints
    const promises = [
      request.get(`${baseURL}/health`),
      request.get(`${baseURL}/bodies`),
      request.get(`${baseURL}/updates/status`),
      request.get(`${baseURL}/updates/latest`)
    ]
    
    const responses = await Promise.all(promises)
    
    responses.forEach(response => {
      expect(response.ok()).toBeTruthy()
    })
  })

  test('should return error for invalid endpoints', async ({ request }) => {
    const response = await request.get(`${baseURL}/invalid-endpoint`)
    expect(response.status()).toBe(404)
  })

  test('should handle malformed requests gracefully', async ({ request }) => {
    // Test with invalid JSON in body
    const response = await request.post(`${baseURL}/bodies`, {
      data: 'invalid json'
    })
    expect(response.status()).toBe(422) // Unprocessable Entity
  })
})

test.describe('API Performance', () => {
  const baseURL = process.env.PUBLIC_API_URL || 'http://localhost:13800'

  test('should respond within reasonable time', async ({ request }) => {
    const startTime = Date.now()
    const response = await request.get(`${baseURL}/health`)
    const endTime = Date.now()
    
    expect(response.ok()).toBeTruthy()
    expect(endTime - startTime).toBeLessThan(1000) // Should respond within 1 second
  })

  test('should handle large datasets efficiently', async ({ request }) => {
    const startTime = Date.now()
    const response = await request.get(`${baseURL}/bodies`)
    const endTime = Date.now()
    
    expect(response.ok()).toBeTruthy()
    expect(endTime - startTime).toBeLessThan(2000) // Should respond within 2 seconds
    
    const data = await response.json()
    expect(data.length).toBeGreaterThan(0)
  })

  test('should maintain consistent response times', async ({ request }) => {
    const responseTimes: number[] = []
    
    // Make 5 requests and measure response times
    for (let i = 0; i < 5; i++) {
      const startTime = Date.now()
      const response = await request.get(`${baseURL}/health`)
      const endTime = Date.now()
      
      expect(response.ok()).toBeTruthy()
      responseTimes.push(endTime - startTime)
    }
    
    // Calculate average response time
    const avgResponseTime = responseTimes.reduce((a, b) => a + b, 0) / responseTimes.length
    expect(avgResponseTime).toBeLessThan(500) // Average should be under 500ms
  })
}) 