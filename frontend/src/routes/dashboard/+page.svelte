<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { browser } from '$app/environment';
  import type { PageData } from './$types';

  export let data: PageData;

  interface ScriptStatus {
    script_name: string;
    last_run: string | null;
    status: 'OK' | 'FAIL' | 'UNKNOWN';
    duration_sec: number | null;
    message: string | null;
  }

  interface UpdateLog {
    id: string;
    timestamp: string;
    script_name: string;
    status: string;
    message: string | null;
    duration_sec: number | null;
    log_level: string | null;
    source_file: string | null;
  }

  let scriptStatuses: ScriptStatus[] = [];
  let latestUpdates: UpdateLog[] = [];
  let loading = true;
  let error = '';
  let refreshInterval: number;
  let lastRefresh = new Date();

  const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  async function fetchScriptStatus() {
    try {
      const response = await fetch(`${API_BASE}/updates/status`);
      if (!response.ok) throw new Error('Failed to fetch script status');
      scriptStatuses = await response.json();
    } catch (err) {
      console.error('Error fetching script status:', err);
      error = 'Failed to load script status';
    }
  }

  async function fetchLatestUpdates() {
    try {
      const response = await fetch(`${API_BASE}/updates/latest?limit=50`);
      if (!response.ok) throw new Error('Failed to fetch latest updates');
      latestUpdates = await response.json();
    } catch (err) {
      console.error('Error fetching latest updates:', err);
      error = 'Failed to load latest updates';
    }
  }

  async function triggerScript(scriptName: string) {
    try {
      const button = event?.target as HTMLButtonElement;
      if (button) {
        button.disabled = true;
        button.textContent = 'Running...';
      }

      const response = await fetch(`${API_BASE}/updates/trigger/${scriptName}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ parameters: {} }),
      });

      if (!response.ok) throw new Error('Failed to trigger script');
      
      const result = await response.json();
      console.log(`Script ${scriptName} triggered:`, result);
      
      // Show success message
      error = '';
      
      // Refresh status after a short delay
      setTimeout(() => {
        fetchScriptStatus();
        fetchLatestUpdates();
        lastRefresh = new Date();
      }, 2000);
      
    } catch (err) {
      console.error(`Error triggering script ${scriptName}:`, err);
      error = `Failed to trigger ${scriptName}`;
    } finally {
      const button = event?.target as HTMLButtonElement;
      if (button) {
        button.disabled = false;
        button.textContent = 'Run Now';
      }
    }
  }

  function getStatusIcon(status: string) {
    switch (status) {
      case 'OK': return '🟢';
      case 'FAIL': return '🔴';
      default: return '🟡';
    }
  }

  function getStatusBadgeClass(status: string) {
    switch (status) {
      case 'OK': return 'badge-success';
      case 'FAIL': return 'badge-error';
      default: return 'badge-warning';
    }
  }

  function formatDuration(seconds: number | null) {
    if (!seconds) return 'N/A';
    if (seconds < 60) return `${seconds.toFixed(1)}s`;
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}m ${remainingSeconds.toFixed(0)}s`;
  }

  function formatTimestamp(timestamp: string) {
    return new Date(timestamp).toLocaleString();
  }

  function getTimeAgo(timestamp: string) {
    const now = new Date();
    const time = new Date(timestamp);
    const diffMs = now.getTime() - time.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);
    
    if (diffDays > 0) return `${diffDays}d ago`;
    if (diffHours > 0) return `${diffHours}h ago`;
    if (diffMins > 0) return `${diffMins}m ago`;
    return 'Just now';
  }

  async function loadData() {
    loading = true;
    error = '';
    await Promise.all([fetchScriptStatus(), fetchLatestUpdates()]);
    loading = false;
    lastRefresh = new Date();
  }

  onMount(() => {
    loadData();
    
    // Set up auto-refresh every 5 seconds
    if (browser) {
      refreshInterval = setInterval(() => {
        fetchScriptStatus();
        fetchLatestUpdates();
        lastRefresh = new Date();
      }, 5000);
    }
  });

  onDestroy(() => {
    if (refreshInterval) {
      clearInterval(refreshInterval);
    }
  });
</script>

<svelte:head>
  <title>Dashboard - Sannetic Explorer</title>
</svelte:head>

<div class="container mx-auto p-4">
  <div class="flex justify-between items-center mb-6">
    <div>
      <h1 class="text-3xl font-bold">System Dashboard</h1>
      <p class="text-base-content/70">Monitor script execution and system updates</p>
    </div>
    <div class="flex items-center gap-4">
      <div class="text-sm text-base-content/70">
        Last refresh: {lastRefresh.toLocaleTimeString()}
      </div>
      <button 
        class="btn btn-primary" 
        on:click={loadData}
        disabled={loading}
      >
        {#if loading}
          <span class="loading loading-spinner loading-sm"></span>
          Loading...
        {:else}
          Refresh
        {/if}
      </button>
    </div>
  </div>

  {#if error}
    <div class="alert alert-error mb-4">
      <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      <span>{error}</span>
    </div>
  {/if}

  <!-- System Stats -->
  <div class="stats shadow mb-8">
    <div class="stat">
      <div class="stat-title">Total Scripts</div>
      <div class="stat-value">{scriptStatuses.length}</div>
    </div>
    
    <div class="stat">
      <div class="stat-title">Successful</div>
      <div class="stat-value text-success">
        {scriptStatuses.filter(s => s.status === 'OK').length}
      </div>
    </div>
    
    <div class="stat">
      <div class="stat-title">Failed</div>
      <div class="stat-value text-error">
        {scriptStatuses.filter(s => s.status === 'FAIL').length}
      </div>
    </div>
    
    <div class="stat">
      <div class="stat-title">Total Updates</div>
      <div class="stat-value">{latestUpdates.length}</div>
    </div>
  </div>

  <!-- Script Status Cards -->
  <div class="mb-8">
    <h2 class="text-2xl font-semibold mb-4">Script Status</h2>
    {#if loading && scriptStatuses.length === 0}
      <div class="flex justify-center items-center h-32">
        <span class="loading loading-spinner loading-lg"></span>
      </div>
    {:else}
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {#each scriptStatuses as script}
          <div class="card bg-base-100 shadow-xl">
            <div class="card-body">
              <div class="flex justify-between items-start">
                <div>
                  <h3 class="card-title text-lg">{script.script_name}</h3>
                  <div class="flex items-center gap-2 mt-2">
                    <span class="text-2xl">{getStatusIcon(script.status)}</span>
                    <span class="badge {getStatusBadgeClass(script.status)}">
                      {script.status}
                    </span>
                  </div>
                </div>
                <button 
                  class="btn btn-sm btn-outline"
                  on:click={() => triggerScript(script.script_name)}
                >
                  Run Now
                </button>
              </div>
              
              {#if script.last_run}
                <p class="text-sm text-base-content/70 mt-2">
                  Last run: {getTimeAgo(script.last_run)}
                </p>
              {/if}
              
              {#if script.duration_sec}
                <p class="text-sm text-base-content/70">
                  Duration: {formatDuration(script.duration_sec)}
                </p>
              {/if}
              
              {#if script.message}
                <p class="text-sm text-base-content/70 mt-2">
                  {script.message}
                </p>
              {/if}
            </div>
          </div>
        {/each}
      </div>
    {/if}
  </div>

  <!-- Latest Updates Table -->
  <div class="mb-8">
    <h2 class="text-2xl font-semibold mb-4">Latest Updates</h2>
    {#if loading && latestUpdates.length === 0}
      <div class="flex justify-center items-center h-32">
        <span class="loading loading-spinner loading-lg"></span>
      </div>
    {:else}
      <div class="overflow-x-auto">
        <table class="table table-zebra w-full">
          <thead>
            <tr>
              <th>Timestamp</th>
              <th>Script</th>
              <th>Status</th>
              <th>Duration</th>
              <th>Message</th>
            </tr>
          </thead>
          <tbody>
            {#each latestUpdates as update}
              <tr>
                <td class="text-sm">
                  <div>{formatTimestamp(update.timestamp)}</div>
                  <div class="text-xs text-base-content/50">{getTimeAgo(update.timestamp)}</div>
                </td>
                <td>
                  <span class="font-mono text-sm">{update.script_name}</span>
                </td>
                <td>
                  <span class="badge {getStatusBadgeClass(update.status)}">
                    {update.status}
                  </span>
                </td>
                <td>{formatDuration(update.duration_sec)}</td>
                <td class="max-w-xs">
                  {#if update.message}
                    <div class="tooltip" data-tip={update.message}>
                      <span class="truncate block">{update.message}</span>
                    </div>
                  {:else}
                    <span class="text-base-content/50">-</span>
                  {/if}
                </td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    {/if}
  </div>
</div>

<style>
  .tooltip {
    @apply cursor-help;
  }
</style> 