<script lang="ts">
  import { onMount } from 'svelte';
  import Scene3D from '$lib/components/Scene3D.svelte';
  import { getBuildInfo, getAllBuildInfo, type BuildInfo } from '$lib/api';
  
  let showStars = false;
  let ambientLightIntensity = 0.4;
  let showOrbits = true;
  let showPlanetNames = true;
  let showSunName = true;
  let showControls = false;
  let currentTime = '';
  let buildTime = '';
  let buildTimeFromDB = '';
  let allBuildInfo: Record<string, BuildInfo> = {};
  let scene3DComponent: Scene3D;
  let selectedObject: any = null;
  let showInfoPanel = false;
  let isAnimationPlaying = true;
  let animationSpeed = 0.5; // 50% slower by default
  let showBuildInfo = false; // Build info panel hidden by default
  
  // Update time every second and load build info
  onMount(() => {
    const updateTime = () => {
      const now = new Date();
      currentTime = now.toLocaleTimeString('de-DE');
      // Update build time to current date and time (fallback)
      buildTime = now.toLocaleDateString('de-DE') + '-' + now.toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit' });
    };
    
    // Load build info from database
    const loadBuildInfo = async () => {
      try {
        // Load all build info for all components
        allBuildInfo = await getAllBuildInfo();
        buildTimeFromDB = allBuildInfo.frontend?.build_time || '';
        console.log('All build info loaded from DB:', allBuildInfo);
      } catch (error) {
        console.error('Failed to load build info from DB:', error);
        // Create fallback with current time as container start time
        const now = new Date();
        const fallbackTime = now.getFullYear().toString() + 
                            String(now.getMonth() + 1).padStart(2, '0') + 
                            String(now.getDate()).padStart(2, '0') + 
                            String(now.getHours()).padStart(2, '0') + 
                            String(now.getMinutes()).padStart(2, '0');
        
        allBuildInfo = {
          frontend: { build_time: fallbackTime, component: 'frontend', build_timestamp: now.toISOString() },
          backend: { build_time: fallbackTime, component: 'backend', build_timestamp: now.toISOString() },
          worker: { build_time: fallbackTime, component: 'worker', build_timestamp: now.toISOString() }
        };
        buildTimeFromDB = fallbackTime;
        console.log('Using fallback build info:', allBuildInfo);
      }
    };
    
    // Keyboard shortcuts
    const handleKeyDown = (event: KeyboardEvent) => {
      // Ctrl+I or Cmd+I to toggle build info
      if ((event.ctrlKey || event.metaKey) && event.key === 'i') {
        event.preventDefault();
        showBuildInfo = !showBuildInfo;
      }
      // Escape to close build info
      if (event.key === 'Escape' && showBuildInfo) {
        showBuildInfo = false;
      }
    };
    
    updateTime();
    loadBuildInfo();
    const interval = setInterval(updateTime, 1000);
    
    // Add keyboard event listener
    window.addEventListener('keydown', handleKeyDown);
    
    return () => {
      clearInterval(interval);
      window.removeEventListener('keydown', handleKeyDown);
    };
  });
  
  function toggleControls() {
    showControls = !showControls;
  }
  
  function handleObjectClick(objectData: any) {
    selectedObject = objectData;
    showInfoPanel = true;
    console.log('Object clicked:', objectData);
  }
  
  function closeInfoPanel() {
    showInfoPanel = false;
    selectedObject = null;
  }
  
  function resetAll() {
    // Reset all values to defaults
    showStars = false;
    ambientLightIntensity = 0.4;
    showOrbits = true;
    showPlanetNames = true;
    showSunName = true;
    isAnimationPlaying = true;
    animationSpeed = 0.5;
    showBuildInfo = false;
    
    // Reset the 3D scene (zoom, camera position, etc.)
    if (scene3DComponent) {
      scene3DComponent.resetScene();
    }
  }

  function focusOnObject(objectName: string) {
    if (scene3DComponent) {
      scene3DComponent.focusOnObject(objectName);
    }
  }

  // Define celestial objects for the menu
  const celestialObjects = [
    { name: 'Sonne', icon: '☀️', color: 'text-yellow-400' },
    { name: 'Mercury', icon: '☿', color: 'text-gray-400' },
    { name: 'Venus', icon: '♀', color: 'text-orange-300' },
    { name: 'Earth', icon: '🌍', color: 'text-blue-400' },
    { name: 'Mars', icon: '♂', color: 'text-red-400' },
    { name: 'Jupiter', icon: '♃', color: 'text-orange-500' },
    { name: 'Saturn', icon: '♄', color: 'text-yellow-300' },
    { name: 'Uranus', icon: '♅', color: 'text-cyan-400' },
    { name: 'Neptune', icon: '♆', color: 'text-blue-600' }
  ];
</script>

<svelte:head>
	<title>3D Solar System - Sannetic Explorer</title>
	<meta name="description" content="3D visualization of the solar system" />
</svelte:head>

<!-- Full screen container -->
<div class="fixed inset-0 bg-black">
	<!-- Header bar -->
	<div class="absolute top-0 left-0 right-0 z-50 bg-black/50 backdrop-blur-sm border-b border-gray-700">
		<div class="flex items-center justify-between px-4 py-3">
			<!-- Left: Back button -->
			<a href="/" class="btn btn-ghost btn-sm text-white hover:bg-white/10">
				<svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path>
				</svg>
				Zurück
			</a>
			
			<!-- Center: Time and title -->
			<div class="text-center text-white">
				<h1 class="text-lg font-bold">Sannetic Explorer</h1>
				<div class="text-sm opacity-75">{currentTime}</div>
			</div>
			
			<!-- Right: Controls button -->
			<button 
				class="btn btn-ghost btn-sm text-white hover:bg-white/10 {showControls ? 'bg-white/20' : ''}"
				on:click={toggleControls}
			>
				<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path>
				</svg>
			</button>
		</div>
	</div>

	<!-- Info Panel -->
	{#if showInfoPanel && selectedObject}
		<div class="absolute top-20 left-4 z-50 bg-gray-900/95 backdrop-blur-md border border-gray-700 rounded-lg shadow-2xl max-w-sm w-80">
			<!-- Header -->
			<div class="flex items-center justify-between p-4 border-b border-gray-700">
				<h3 class="text-lg font-bold text-white flex items-center gap-2">
					{#if selectedObject.type === 'star'}
						<svg class="w-5 h-5 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
							<path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"></path>
						</svg>
					{:else}
						<svg class="w-5 h-5 text-blue-400" fill="currentColor" viewBox="0 0 20 20">
							<path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path>
						</svg>
					{/if}
					{selectedObject.name}
				</h3>
				<button 
					class="btn btn-ghost btn-sm text-white hover:bg-white/10"
					on:click={closeInfoPanel}
				>
					<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
					</svg>
				</button>
			</div>

			<!-- Content -->
			<div class="p-4 space-y-3 text-white text-sm max-h-96 overflow-y-auto">
				{#if selectedObject.type === 'star'}
					<div class="grid grid-cols-2 gap-2">
						<div class="text-gray-400">Typ:</div>
						<div>Stern (G2V)</div>
						
						<div class="text-gray-400">Radius:</div>
						<div>{selectedObject.radius.toLocaleString()} km</div>
						
						<div class="text-gray-400">Masse:</div>
						<div>{selectedObject.mass}</div>
						
						<div class="text-gray-400">Temperatur:</div>
						<div>{selectedObject.temperature}</div>
						
						<div class="text-gray-400">Alter:</div>
						<div>{selectedObject.age}</div>
						
						<div class="text-gray-400">Leuchtkraft:</div>
						<div>{selectedObject.luminosity}</div>
					</div>
					
					<div class="pt-2 border-t border-gray-700">
						<div class="text-gray-400 mb-1">Zusammensetzung:</div>
						<div>{selectedObject.composition}</div>
					</div>
				{:else}
					<div class="grid grid-cols-2 gap-2">
						<div class="text-gray-400">Typ:</div>
						<div>Planet</div>
						
						<div class="text-gray-400">Durchmesser:</div>
						<div>{selectedObject.diameter}</div>
						
						<div class="text-gray-400">Radius:</div>
						<div>{selectedObject.radius}</div>
						
						<div class="text-gray-400">Entfernung:</div>
						<div>{selectedObject.distanceFromSun}</div>
						
						<div class="text-gray-400">Umlaufzeit:</div>
						<div>{selectedObject.orbitalPeriod}</div>
						
						<div class="text-gray-400">Geschwindigkeit:</div>
						<div>{selectedObject.orbitalSpeed}</div>
						
						<div class="text-gray-400">Aktueller Winkel:</div>
						<div>{selectedObject.currentAngle}</div>
						
						<div class="text-gray-400">Masse:</div>
						<div>{selectedObject.mass}</div>
						
						<div class="text-gray-400">Schwerkraft:</div>
						<div>{selectedObject.gravity}</div>
						
						<div class="text-gray-400">Temperatur:</div>
						<div>{selectedObject.temperature}</div>
						
						<div class="text-gray-400">Monde:</div>
						<div>{selectedObject.moons}</div>
					</div>
					
					<div class="pt-2 border-t border-gray-700">
						<div class="text-gray-400 mb-1">Atmosphäre:</div>
						<div>{selectedObject.atmosphere}</div>
					</div>
				{/if}
			</div>
		</div>
	{/if}

	  <!-- 3D Scene - Full screen -->
  <div class="absolute inset-0 pt-16">
    <Scene3D 
      bind:this={scene3DComponent}
      {showStars}
      {ambientLightIntensity}
      {showOrbits}
      {showPlanetNames}
      {showSunName}
      {isAnimationPlaying}
      {animationSpeed}
      onReset={() => {}}
      onObjectClick={handleObjectClick}
    />
  </div>

	<!-- Navigation Offcanvas -->
	<div 
		class="fixed top-16 right-0 h-[calc(100vh-4rem)] w-80 bg-gray-900/95 backdrop-blur-md border-l border-gray-700 transform transition-transform duration-300 z-60 {showControls ? 'translate-x-0' : 'translate-x-full'}"
	>
		<!-- Navigation Header -->
		<div class="flex items-center justify-between p-4 border-b border-gray-700">
			<h2 class="text-lg font-bold text-white">🚀 Sonnensystem Navigation</h2>
			<button 
				class="btn btn-ghost btn-sm text-white hover:bg-white/10"
				on:click={toggleControls}
			>
				<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
				</svg>
			</button>
		</div>

		<!-- Navigation Content -->
		<div class="p-4 space-y-6 text-white overflow-y-auto h-full pb-20">
			<!-- Celestial Objects -->
			<div class="space-y-4">
				<h3 class="text-md font-semibold text-gray-300 flex items-center gap-2">
					<svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
						<path fill-rule="evenodd" d="M10 2L13.09 8.26L20 9L14 14.74L15.18 21.02L10 18L4.82 21.02L6 14.74L0 9L6.91 8.26L10 2Z" clip-rule="evenodd"></path>
					</svg>
					Himmelskörper
				</h3>
				
				<div class="grid grid-cols-1 gap-2">
					{#each celestialObjects as object}
						<button 
							on:click={() => focusOnObject(object.name)}
							class="btn btn-outline btn-sm text-white border-gray-600 hover:bg-white/10 justify-start transition-all duration-200 hover:scale-105"
						>
							<span class="text-lg mr-2">{object.icon}</span>
							<span class="{object.color} font-medium">{object.name}</span>
						</button>
					{/each}
				</div>
			</div>

			<!-- Quick Actions -->
			<div class="space-y-4">
				<h3 class="text-md font-semibold text-gray-300 flex items-center gap-2">
					<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
					</svg>
					Schnellaktionen
				</h3>
				
				<div class="space-y-2">
					<button 
						on:click={resetAll}
						class="w-full btn btn-outline btn-sm text-white border-gray-600 hover:bg-white/10 justify-start"
					>
						<svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
						</svg>
						Ansicht zurücksetzen
					</button>
				</div>
			</div>

			<!-- Info Panel -->
			<div class="space-y-4">
				<h3 class="text-md font-semibold text-gray-300 flex items-center gap-2">
					<svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
						<path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"></path>
					</svg>
					Information
				</h3>
				
				<div class="bg-gray-800/50 rounded-lg p-3 space-y-2 text-xs">
					<div class="flex justify-between">
						<span class="text-gray-400">Planeten:</span>
						<span>8</span>
					</div>
					<div class="flex justify-between">
						<span class="text-gray-400">Sterne:</span>
						<span>1</span>
					</div>
					<div class="flex justify-between">
						<span class="text-gray-400">Animation:</span>
						<span class="{isAnimationPlaying ? 'text-green-400' : 'text-red-400'}">
							{isAnimationPlaying ? 'Läuft' : 'Pausiert'}
						</span>
					</div>
				</div>
			</div>

			<!-- Help -->
			<div class="space-y-2">
				<h3 class="text-md font-semibold text-gray-300 flex items-center gap-2">
					<svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
						<path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-8-3a1 1 0 00-.867.5 1 1 0 11-1.731-1A3 3 0 0113 8a3.001 3.001 0 01-2 2.83V11a1 1 0 11-2 0v-1a1 1 0 011-1 1 1 0 100-2zm0 8a1 1 0 100-2 1 1 0 000 2z" clip-rule="evenodd"></path>
					</svg>
					Steuerung
				</h3>
				<div class="text-xs text-gray-400 space-y-1">
					<div>🖱️ <strong>Mausrad:</strong> Zoomen</div>
					<div>🖱️ <strong>Ziehen:</strong> Kamera bewegen</div>
					<div>🎯 <strong>Button:</strong> Objekt fokussieren</div>
					<div>⏯️ <strong>Unten:</strong> Animation pausieren/starten</div>
				</div>
			</div>
		</div>
	</div>

	<!-- Overlay backdrop when controls are open -->
	{#if showControls}
		<div 
			class="fixed inset-0 bg-black/30 z-50"
			on:click={toggleControls}
			role="button"
			tabindex="0"
			on:keydown={(e) => e.key === 'Escape' && toggleControls()}
		></div>
	{/if}
	
	<!-- Build Info Panel -->
	{#if showBuildInfo}
		<div class="fixed bottom-4 right-4 z-50 bg-black/80 backdrop-blur-md text-white text-xs rounded-lg border border-gray-600 shadow-2xl min-w-64">
			<!-- Header with close button -->
			<div class="flex items-center justify-between p-3 border-b border-gray-600">
				<div class="flex items-center gap-2">
					<svg class="w-4 h-4 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
					</svg>
					<span class="font-semibold">System Info</span>
				</div>
				<button 
					class="btn btn-ghost btn-xs text-white hover:bg-white/10"
					on:click={() => showBuildInfo = false}
					title="Schließen (Escape)"
				>
					<svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
					</svg>
				</button>
			</div>
			
			<!-- Content -->
			<div class="p-3 space-y-4">
				<!-- System Status -->
				<div class="space-y-2">
					<h4 class="text-sm font-semibold text-gray-300">System Status</h4>
					<div class="grid grid-cols-2 gap-2 text-xs">
						<div class="text-gray-400">Render:</div>
						<div class="font-mono">{currentTime}</div>
						
						<div class="text-gray-400">Status:</div>
						<div class="font-mono">{showControls ? 'Controls ON' : 'Live'}</div>
						
						<div class="text-gray-400">Animation:</div>
						<div class="font-mono">{isAnimationPlaying ? 'Playing' : 'Paused'} ({(animationSpeed * 100).toFixed(0)}%)</div>
						
						<div class="text-gray-400">Labels:</div>
						<div class="font-mono">P:{showPlanetNames ? 'ON' : 'OFF'} S:{showSunName ? 'ON' : 'OFF'}</div>
						
						<div class="text-gray-400">Info:</div>
						<div class="font-mono">{showInfoPanel ? selectedObject?.name || 'Unknown' : 'None'}</div>
					</div>
				</div>
				
				<!-- Container Start Times -->
				<div class="space-y-2">
					<h4 class="text-sm font-semibold text-gray-300">Container Start Times</h4>
					<div class="space-y-1 text-xs">
						{#each Object.entries(allBuildInfo) as [component, info]}
							<div class="flex justify-between items-center py-1 px-2 bg-gray-800/50 rounded">
								<div class="flex items-center gap-2">
									{#if component === 'frontend'}
										<div class="w-2 h-2 bg-blue-400 rounded-full"></div>
									{:else if component === 'backend'}
										<div class="w-2 h-2 bg-green-400 rounded-full"></div>
									{:else if component === 'worker'}
										<div class="w-2 h-2 bg-yellow-400 rounded-full"></div>
									{/if}
									<span class="text-gray-300 capitalize">{component}</span>
								</div>
								<span class="font-mono text-gray-400">{info.build_time || 'N/A'}</span>
							</div>
						{/each}
						
						{#if Object.keys(allBuildInfo).length === 0}
							<div class="text-gray-500 text-center py-2">Keine Container-Informationen verfügbar</div>
						{/if}
					</div>
				</div>
			</div>
			
			<!-- Footer with shortcut hint -->
			<div class="px-3 py-2 border-t border-gray-600 text-gray-400 text-xs">
				<kbd class="kbd kbd-xs">Ctrl</kbd> + <kbd class="kbd kbd-xs">I</kbd> zum Ein-/Ausblenden
			</div>
		</div>
	{/if}
</div> 