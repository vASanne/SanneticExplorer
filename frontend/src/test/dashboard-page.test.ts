import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/svelte'
import { tick } from 'svelte'
import Dashboard from './+page.svelte'

// Mock the API module
vi.mock('$lib/api', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn()
  }
}))

// Mock data
const mockScriptStatus = [
  {
    script_name: 'update_critical.py',
    last_run: '2024-01-15T10:30:00Z',
    status: 'OK',
    duration_sec: 45.2,
    message: 'Successfully updated 5 critical satellites'
  },
  {
    script_name: 'update_data_optimized.py',
    last_run: '2024-01-15T09:15:00Z',
    status: 'FAIL',
    duration_sec: 12.8,
    message: 'API rate limit exceeded'
  },
  {
    script_name: 'sync.py',
    last_run: '2024-01-15T08:00:00Z',
    status: 'OK',
    duration_sec: 120.5,
    message: 'Data synchronization completed'
  },
  {
    script_name: 'ai_health_check.py',
    last_run: '2024-01-15T07:45:00Z',
    status: 'UNKNOWN',
    duration_sec: 30.1,
    message: 'Some data quality issues detected'
  }
]

const mockUpdateLogs = [
  {
    id: '1',
    timestamp: '2024-01-15T10:30:00Z',
    script_name: 'update_critical.py',
    status: 'success',
    message: 'Successfully updated 5 critical satellites',
    duration_sec: 45.2,
    log_level: 'INFO',
    source_file: '/var/log/update.log'
  },
  {
    id: '2',
    timestamp: '2024-01-15T09:15:00Z',
    script_name: 'update_data_optimized.py',
    status: 'error',
    message: 'API rate limit exceeded',
    duration_sec: 12.8,
    log_level: 'ERROR',
    source_file: '/var/log/update.log'
  }
]

describe('Dashboard', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    // Reset fetch mock
    global.fetch = vi.fn()
  })

  it('renders dashboard with loading state initially', () => {
    render(Dashboard)
    
    expect(screen.getByText('System Dashboard')).toBeInTheDocument()
    expect(screen.getByText('Loading...')).toBeInTheDocument()
  })

  it('renders script status cards with correct data', async () => {
    // Mock successful API responses
    global.fetch = vi.fn()
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockScriptStatus)
      })
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockUpdateLogs)
      })

    render(Dashboard)
    
    // Wait for data to load
    await waitFor(() => {
      expect(screen.getByText('update_critical.py')).toBeInTheDocument()
    })

    // Check status cards are rendered
    expect(screen.getByText('update_critical.py')).toBeInTheDocument()
    expect(screen.getByText('update_data_optimized.py')).toBeInTheDocument()
    expect(screen.getByText('sync.py')).toBeInTheDocument()
    expect(screen.getByText('ai_health_check.py')).toBeInTheDocument()

    // Check status indicators
    expect(screen.getByText('OK')).toBeInTheDocument()
    expect(screen.getByText('FAIL')).toBeInTheDocument()
    expect(screen.getByText('UNKNOWN')).toBeInTheDocument()
  })

  it('renders update logs table with correct data', async () => {
    global.fetch = vi.fn()
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockScriptStatus)
      })
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockUpdateLogs)
      })

    render(Dashboard)
    
    await waitFor(() => {
      expect(screen.getByText('update_critical.py')).toBeInTheDocument()
    })

    // Check table headers
    expect(screen.getByText('Timestamp')).toBeInTheDocument()
    expect(screen.getByText('Script')).toBeInTheDocument()
    expect(screen.getByText('Status')).toBeInTheDocument()
    expect(screen.getByText('Duration')).toBeInTheDocument()
    expect(screen.getByText('Message')).toBeInTheDocument()

    // Check table data
    expect(screen.getByText('Successfully updated 5 critical satellites')).toBeInTheDocument()
    expect(screen.getByText('API rate limit exceeded')).toBeInTheDocument()
  })

  it('displays correct status colors and icons', async () => {
    global.fetch = vi.fn()
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockScriptStatus)
      })
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockUpdateLogs)
      })

    render(Dashboard)
    
    await waitFor(() => {
      expect(screen.getByText('update_critical.py')).toBeInTheDocument()
    })

    // Check for status-specific elements
    const okStatus = screen.getByText('OK')
    const failStatus = screen.getByText('FAIL')
    const unknownStatus = screen.getByText('UNKNOWN')

    expect(okStatus).toBeInTheDocument()
    expect(failStatus).toBeInTheDocument()
    expect(unknownStatus).toBeInTheDocument()
  })

  it('triggers script execution when Run Now button is clicked', async () => {
    global.fetch = vi.fn()
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockScriptStatus)
      })
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockUpdateLogs)
      })
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({
          job_id: 'test-job-123',
          script_name: 'update_critical.py',
          status: 'queued',
          message: 'Script update_critical.py has been queued for execution'
        })
      })

    render(Dashboard)
    
    await waitFor(() => {
      expect(screen.getByText('update_critical.py')).toBeInTheDocument()
    })

    // Find and click the first "Run Now" button
    const runButtons = screen.getAllByText('Run Now')
    expect(runButtons.length).toBeGreaterThan(0)
    
    fireEvent.click(runButtons[0])

    // Wait for the API call to be made
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/updates/trigger/update_critical.py'),
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'Content-Type': 'application/json'
          }),
          body: JSON.stringify({ parameters: {} })
        })
      )
    })
  })

  it('handles API errors gracefully', async () => {
    global.fetch = vi.fn()
      .mockRejectedValueOnce(new Error('Network error'))

    render(Dashboard)
    
    await waitFor(() => {
      expect(screen.getByText('Error loading dashboard data')).toBeInTheDocument()
    })
  })

  it('handles empty data responses', async () => {
    global.fetch = vi.fn()
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve([])
      })
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve([])
      })

    render(Dashboard)
    
    await waitFor(() => {
      expect(screen.getByText('No scripts found')).toBeInTheDocument()
      expect(screen.getByText('No update logs found')).toBeInTheDocument()
    })
  })

  it('formats duration correctly', async () => {
    global.fetch = vi.fn()
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockScriptStatus)
      })
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockUpdateLogs)
      })

    render(Dashboard)
    
    await waitFor(() => {
      expect(screen.getByText('update_critical.py')).toBeInTheDocument()
    })

    // Check duration formatting
    expect(screen.getByText('45.2s')).toBeInTheDocument()
    expect(screen.getByText('12.8s')).toBeInTheDocument()
    expect(screen.getByText('120.5s')).toBeInTheDocument()
    expect(screen.getByText('30.1s')).toBeInTheDocument()
  })

  it('auto-refreshes data every 5 seconds', async () => {
    vi.useFakeTimers()
    
    global.fetch = vi.fn()
      .mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockScriptStatus)
      })

    render(Dashboard)
    
    // Initial fetch
    expect(global.fetch).toHaveBeenCalledTimes(1)
    
    // Advance timer by 5 seconds
    vi.advanceTimersByTime(5000)
    await tick()
    
    // Should have made another fetch
    expect(global.fetch).toHaveBeenCalledTimes(2)
    
    vi.useRealTimers()
  })

  it('displays relative timestamps', async () => {
    global.fetch = vi.fn()
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockScriptStatus)
      })
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockUpdateLogs)
      })

    render(Dashboard)
    
    await waitFor(() => {
      expect(screen.getByText('update_critical.py')).toBeInTheDocument()
    })

    // Check that relative timestamps are displayed
    // The exact text will depend on the current time, but should contain time-related text
    const timestampElements = screen.getAllByText(/ago|just now|minutes|hours/)
    expect(timestampElements.length).toBeGreaterThan(0)
  })

  it('shows loading state during script execution', async () => {
    global.fetch = vi.fn()
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockScriptStatus)
      })
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockUpdateLogs)
      })
      .mockImplementationOnce(() => new Promise(resolve => setTimeout(resolve, 100)))

    render(Dashboard)
    
    await waitFor(() => {
      expect(screen.getByText('update_critical.py')).toBeInTheDocument()
    })

    const runButtons = screen.getAllByText('Run Now')
    fireEvent.click(runButtons[0])

    // Should show loading state
    await waitFor(() => {
      expect(screen.getByText('Running...')).toBeInTheDocument()
    })
  })

  it('handles multiple script triggers correctly', async () => {
    global.fetch = vi.fn()
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockScriptStatus)
      })
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockUpdateLogs)
      })
      .mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({
          job_id: 'test-job',
          script_name: 'test-script',
          status: 'queued'
        })
      })

    render(Dashboard)
    
    await waitFor(() => {
      expect(screen.getByText('update_critical.py')).toBeInTheDocument()
    })

    const runButtons = screen.getAllByText('Run Now')
    
    // Click multiple buttons
    fireEvent.click(runButtons[0])
    fireEvent.click(runButtons[1])

    await waitFor(() => {
      // Should have made multiple API calls
      expect(global.fetch).toHaveBeenCalledTimes(4) // 2 initial + 2 triggers
    })
  })
}) 