<script lang="ts">
	import SolarSystemCanvas from '$lib/components/SolarSystemCanvas.svelte';
	import SpeedControl from '$lib/components/SpeedControl.svelte';
	import OrbitSidePanel from '$lib/components/OrbitSidePanel.svelte';
	import PerformanceMonitor from '$lib/components/PerformanceMonitor.svelte';
	import type { PageData } from './$types';
	import type { CelestialBody } from '$lib/api';

	export let data: PageData;
	
	// Extract bodies from the loaded data
	$: bodies = data.bodies || [];
	$: error = data.error;
	
	// Side panel state
	let isSidePanelOpen = false;
	let showPerformanceMonitor = false;
	
	// Handle camera centering
	function handleCenterCamera(event: CustomEvent) {
		const { body } = event.detail;
		// The SolarSystemCanvas component will handle the centering
		console.log('Centering camera on:', body.name);
	}
	
	// Handle body updates
	function handleBodyUpdated(event: CustomEvent) {
		const { oldBody, newBody } = event.detail;
		console.log('Body updated:', oldBody.name, '->', newBody);
		
		// Update the local bodies array
		const index = bodies.findIndex(b => b.id === oldBody.id);
		if (index !== -1) {
			bodies[index] = newBody;
			bodies = [...bodies]; // Trigger reactivity
		}
	}
</script>

<svelte:head>
	<title>Sannetic Explorer</title>
	<meta name="description" content="Solar System Exploration Dashboard" />
</svelte:head>

<!-- Navigation Bar -->
<nav class="navbar bg-base-100 shadow-lg">
	<div class="navbar-start">
		<div class="dropdown">
			<label tabindex="0" class="btn btn-ghost lg:hidden">
				<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path>
				</svg>
			</label>
			<ul tabindex="0" class="menu menu-sm dropdown-content mt-3 z-[1] p-2 shadow bg-base-100 rounded-box w-52">
				<li><a href="/">Home</a></li>
				<li><a href="/3d">3D View</a></li>
				<li><a href="/dashboard">Dashboard</a></li>
			</ul>
		</div>
		<a href="/" class="btn btn-ghost text-xl">Sannetic Explorer</a>
	</div>
	<div class="navbar-center hidden lg:flex">
		<ul class="menu menu-horizontal px-1">
			<li><a href="/">Home</a></li>
			<li><a href="/3d">3D View</a></li>
			<li><a href="/dashboard">Dashboard</a></li>
		</ul>
	</div>
	<div class="navbar-end">
		<div class="dropdown dropdown-end">
			<label tabindex="0" class="btn btn-circle btn-ghost">
				<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zM21 5a2 2 0 00-2-2h-4a2 2 0 00-2 2v12a4 4 0 004 4h4a2 2 0 002-2V5z"></path>
				</svg>
			</label>
			<ul tabindex="0" class="dropdown-content menu p-2 shadow bg-base-100 rounded-box w-52">
				<li><a data-set-theme="light">Light</a></li>
				<li><a data-set-theme="dark">Dark</a></li>
				<li><a data-set-theme="cyberpunk">Cyberpunk</a></li>
				<li><a data-set-theme="synthwave">Synthwave</a></li>
			</ul>
		</div>
	</div>
</nav>

<!-- Performance Monitor -->
<PerformanceMonitor isVisible={showPerformanceMonitor} />

<div class="hero min-h-screen bg-gradient-to-br from-base-200 to-base-300">
	<div class="hero-content text-center">
		<div class="max-w-md">
			<h1 class="text-5xl font-bold text-primary">Sannetic Explorer</h1>
			<p class="py-6 text-base-content">
				Explore the solar system with real-time data and 3D visualizations
			</p>
			<div class="flex gap-4 justify-center">
				<a href="/3d" class="btn btn-primary">3D Solar System</a>
				<a href="/dashboard" class="btn btn-outline">System Dashboard</a>
			</div>
		</div>
	</div>
</div>

<!-- Solar System Canvas Section -->
<div class="container mx-auto px-4 py-8">
	<div class="grid grid-cols-1 lg:grid-cols-4 gap-6">
		<!-- 3D Canvas -->
		<div class="lg:col-span-3">
			<div class="card bg-base-100 shadow-xl">
				<div class="card-body">
					<div class="flex justify-between items-center mb-4">
						<h2 class="card-title text-2xl">Live Solar System View</h2>
						<div class="flex gap-2">
							<button 
								class="btn btn-ghost btn-sm"
								on:click={() => showPerformanceMonitor = !showPerformanceMonitor}
								title="Toggle performance monitor"
							>
								<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
								</svg>
							</button>
							<button 
								class="btn btn-outline btn-sm"
								on:click={() => isSidePanelOpen = !isSidePanelOpen}
							>
								<svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path>
								</svg>
								{isSidePanelOpen ? 'Hide' : 'Show'} Bodies
							</button>
						</div>
					</div>
					<p class="text-base-content/70 mb-6">
						Interactive 3D visualization of the solar system. Use your mouse to rotate, zoom, and explore.
					</p>
					
					{#if error}
						<div class="alert alert-error mb-4">
							<svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
							</svg>
							<span>Error loading celestial data: {error}</span>
						</div>
					{/if}
					
					<div class="w-full h-96 bg-base-300 rounded-lg overflow-hidden">
						<SolarSystemCanvas {bodies} width={800} height={400} />
					</div>
					
					{#if bodies.length > 0}
						<div class="mt-4 text-sm text-base-content/70">
							Loaded {bodies.length} celestial bodies from the database
						</div>
					{/if}
				</div>
			</div>
		</div>
		
		<!-- Controls Panel -->
		<div class="lg:col-span-1">
			<SpeedControl />
		</div>
	</div>
</div>

<!-- Orbit Side Panel -->
<OrbitSidePanel 
	{bodies} 
	isOpen={isSidePanelOpen}
	on:centerCamera={handleCenterCamera}
	on:bodyUpdated={handleBodyUpdated}
	on:close={() => isSidePanelOpen = false}
/>

<div class="container mx-auto px-4 py-8">
	<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
		<div class="card bg-base-100 shadow-xl">
			<div class="card-body">
				<h2 class="card-title">Planets</h2>
				<p>Explore the eight planets of our solar system</p>
				<div class="card-actions justify-end">
					<button class="btn btn-primary">View</button>
				</div>
			</div>
		</div>
		
		<div class="card bg-base-100 shadow-xl">
			<div class="card-body">
				<h2 class="card-title">Moons</h2>
				<p>Discover natural satellites and their characteristics</p>
				<div class="card-actions justify-end">
					<button class="btn btn-primary">View</button>
				</div>
			</div>
		</div>
		
		<div class="card bg-base-100 shadow-xl">
			<div class="card-body">
				<h2 class="card-title">Spacecraft</h2>
				<p>Track missions and exploration data</p>
				<div class="card-actions justify-end">
					<button class="btn btn-primary">View</button>
				</div>
			</div>
		</div>
	</div>
</div> 