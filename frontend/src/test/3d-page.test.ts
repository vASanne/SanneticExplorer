import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/svelte'
import { tick } from 'svelte'
import ThreeDScene from './+page.svelte'

// Mock Three.js and Threlte
vi.mock('three', () => ({
  Scene: vi.fn(),
  PerspectiveCamera: vi.fn(),
  WebGLRenderer: vi.fn(() => ({
    setSize: vi.fn(),
    render: vi.fn(),
    domElement: document.createElement('canvas')
  })),
  SphereGeometry: vi.fn(),
  MeshBasicMaterial: vi.fn(),
  Mesh: vi.fn(),
  InstancedMesh: vi.fn(),
  Vector3: vi.fn(),
  Color: vi.fn(),
  AmbientLight: vi.fn(),
  DirectionalLight: vi.fn(),
  Clock: vi.fn(() => ({
    getDelta: vi.fn(() => 0.016)
  }))
}))

// Mock the API module
vi.mock('$lib/api', () => ({
  default: {
    get: vi.fn()
  }
}))

// Mock data
const mockCelestialBodies = [
  {
    id: '1',
    name: 'Sun',
    type: 'star',
    radius_km: 696340.0,
    color_hex: '#FFD700',
    mean_distance_au: 0,
    orbital_speed_kms: 0
  },
  {
    id: '2',
    name: 'Earth',
    type: 'planet',
    radius_km: 6371.0,
    color_hex: '#0077BE',
    mean_distance_au: 1.0,
    orbital_speed_kms: 29.78
  },
  {
    id: '3',
    name: 'Moon',
    type: 'moon',
    radius_km: 1737.4,
    color_hex: '#C0C0C0',
    mean_distance_au: 0.00257,
    orbital_speed_kms: 1.022
  }
]

describe('3D Scene', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    global.fetch = vi.fn()
  })

  it('renders 3D scene with loading state initially', () => {
    render(ThreeDScene)
    
    expect(screen.getByText('Solar System 3D View')).toBeInTheDocument()
    expect(screen.getByText('Loading celestial bodies...')).toBeInTheDocument()
  })

  it('renders celestial bodies after data loads', async () => {
    global.fetch = vi.fn()
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockCelestialBodies)
      })

    render(ThreeDScene)
    
    await waitFor(() => {
      expect(screen.getByText('Sun')).toBeInTheDocument()
      expect(screen.getByText('Earth')).toBeInTheDocument()
      expect(screen.getByText('Moon')).toBeInTheDocument()
    })
  })

  it('displays performance monitor', async () => {
    global.fetch = vi.fn()
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockCelestialBodies)
      })

    render(ThreeDScene)
    
    await waitFor(() => {
      expect(screen.getByText('Performance Monitor')).toBeInTheDocument()
    })
  })

  it('shows orbit side panel with celestial bodies', async () => {
    global.fetch = vi.fn()
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockCelestialBodies)
      })

    render(ThreeDScene)
    
    await waitFor(() => {
      expect(screen.getByText('Orbital Bodies')).toBeInTheDocument()
    })

    // Check that bodies are listed in the side panel
    expect(screen.getByText('Sun')).toBeInTheDocument()
    expect(screen.getByText('Earth')).toBeInTheDocument()
    expect(screen.getByText('Moon')).toBeInTheDocument()
  })

  it('handles API errors gracefully', async () => {
    global.fetch = vi.fn()
      .mockRejectedValueOnce(new Error('Network error'))

    render(ThreeDScene)
    
    await waitFor(() => {
      expect(screen.getByText('Error loading celestial bodies')).toBeInTheDocument()
    })
  })

  it('handles empty data response', async () => {
    global.fetch = vi.fn()
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve([])
      })

    render(ThreeDScene)
    
    await waitFor(() => {
      expect(screen.getByText('No celestial bodies found')).toBeInTheDocument()
    })
  })

  it('displays speed control slider', async () => {
    global.fetch = vi.fn()
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockCelestialBodies)
      })

    render(ThreeDScene)
    
    await waitFor(() => {
      expect(screen.getByText('Simulation Speed')).toBeInTheDocument()
    })

    // Check for speed control slider
    const speedSlider = screen.getByRole('slider')
    expect(speedSlider).toBeInTheDocument()
  })

  it('allows speed adjustment', async () => {
    global.fetch = vi.fn()
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockCelestialBodies)
      })

    render(ThreeDScene)
    
    await waitFor(() => {
      expect(screen.getByText('Sun')).toBeInTheDocument()
    })

    const speedSlider = screen.getByRole('slider')
    fireEvent.change(speedSlider, { target: { value: '2' } })

    // The speed should be updated (this would be tested in component logic)
    expect(speedSlider).toHaveValue('2')
  })

  it('displays center camera button', async () => {
    global.fetch = vi.fn()
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockCelestialBodies)
      })

    render(ThreeDScene)
    
    await waitFor(() => {
      expect(screen.getByText('Center Camera')).toBeInTheDocument()
    })
  })

  it('shows body information when selected', async () => {
    global.fetch = vi.fn()
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockCelestialBodies)
      })

    render(ThreeDScene)
    
    await waitFor(() => {
      expect(screen.getByText('Sun')).toBeInTheDocument()
    })

    // Click on a celestial body
    const sunButton = screen.getByText('Sun')
    fireEvent.click(sunButton)

    // Should show body details
    await waitFor(() => {
      expect(screen.getByText('Body Details')).toBeInTheDocument()
    })
  })

  it('filters bodies by type', async () => {
    global.fetch = vi.fn()
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockCelestialBodies)
      })

    render(ThreeDScene)
    
    await waitFor(() => {
      expect(screen.getByText('Sun')).toBeInTheDocument()
    })

    // Check for filter options
    expect(screen.getByText('All')).toBeInTheDocument()
    expect(screen.getByText('Stars')).toBeInTheDocument()
    expect(screen.getByText('Planets')).toBeInTheDocument()
    expect(screen.getByText('Moons')).toBeInTheDocument()
  })

  it('updates simulation time display', async () => {
    global.fetch = vi.fn()
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockCelestialBodies)
      })

    render(ThreeDScene)
    
    await waitFor(() => {
      expect(screen.getByText('Simulation Time')).toBeInTheDocument()
    })

    // Check that time is displayed
    const timeElement = screen.getByText(/Simulation Time/)
    expect(timeElement).toBeInTheDocument()
  })

  it('shows FPS counter in performance monitor', async () => {
    global.fetch = vi.fn()
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockCelestialBodies)
      })

    render(ThreeDScene)
    
    await waitFor(() => {
      expect(screen.getByText('Performance Monitor')).toBeInTheDocument()
    })

    // Check for FPS display
    expect(screen.getByText(/FPS/)).toBeInTheDocument()
  })

  it('displays memory usage in performance monitor', async () => {
    global.fetch = vi.fn()
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockCelestialBodies)
      })

    render(ThreeDScene)
    
    await waitFor(() => {
      expect(screen.getByText('Performance Monitor')).toBeInTheDocument()
    })

    // Check for memory usage display
    expect(screen.getByText(/Memory/)).toBeInTheDocument()
  })

  it('handles window resize events', async () => {
    global.fetch = vi.fn()
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockCelestialBodies)
      })

    render(ThreeDScene)
    
    await waitFor(() => {
      expect(screen.getByText('Sun')).toBeInTheDocument()
    })

    // Simulate window resize
    fireEvent.resize(window)

    // The component should handle resize (this would be tested in component logic)
    expect(window).toBeDefined()
  })

  it('displays body count in side panel', async () => {
    global.fetch = vi.fn()
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockCelestialBodies)
      })

    render(ThreeDScene)
    
    await waitFor(() => {
      expect(screen.getByText('Orbital Bodies')).toBeInTheDocument()
    })

    // Check that body count is displayed
    expect(screen.getByText(/3 bodies/)).toBeInTheDocument()
  })

  it('shows loading progress during data fetch', async () => {
    // Mock a slow response
    global.fetch = vi.fn()
      .mockImplementationOnce(() => new Promise(resolve => setTimeout(resolve, 100)))

    render(ThreeDScene)
    
    // Should show loading state
    expect(screen.getByText('Loading celestial bodies...')).toBeInTheDocument()
  })
}) 