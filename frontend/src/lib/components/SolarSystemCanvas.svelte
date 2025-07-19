<script lang="ts">
	// Placeholder for Solar System Canvas - will be implemented later with proper 3D libraries
	export let celestialBodies = [];
	export let showOrbits = true;
	export let showLabels = true;
	export let autoRotate = false;
	export let cameraSpeed = 1.0;
</script>

<div class="w-full h-full bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-900 flex items-center justify-center rounded-lg relative overflow-hidden">
	<!-- Stars background -->
	<div class="absolute inset-0 opacity-30">
		{#each Array(50) as _, i}
			<div 
				class="absolute w-1 h-1 bg-white rounded-full animate-pulse"
				style="
					left: {Math.random() * 100}%; 
					top: {Math.random() * 100}%;
					animation-delay: {Math.random() * 3}s
				"
			></div>
		{/each}
	</div>
	
	<div class="text-center text-white z-10">
		<div class="text-6xl mb-4">🌌</div>
		<h2 class="text-3xl font-bold mb-4">Solar System Explorer</h2>
		<p class="text-lg mb-6 text-white/80">Interactive 3D visualization coming soon...</p>
		
		<div class="grid grid-cols-2 gap-4 mb-6 text-sm">
			<div class="bg-white/10 rounded-lg p-3">
				<div class="font-bold">Show Orbits</div>
				<div class="text-white/70">{showOrbits ? 'Enabled' : 'Disabled'}</div>
			</div>
			<div class="bg-white/10 rounded-lg p-3">
				<div class="font-bold">Show Labels</div>
				<div class="text-white/70">{showLabels ? 'Enabled' : 'Disabled'}</div>
			</div>
			<div class="bg-white/10 rounded-lg p-3">
				<div class="font-bold">Auto Rotate</div>
				<div class="text-white/70">{autoRotate ? 'Enabled' : 'Disabled'}</div>
			</div>
			<div class="bg-white/10 rounded-lg p-3">
				<div class="font-bold">Camera Speed</div>
				<div class="text-white/70">{cameraSpeed}x</div>
			</div>
		</div>
		
		<div class="loading loading-spinner loading-lg"></div>
	</div>
</div> 