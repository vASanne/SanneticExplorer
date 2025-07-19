<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	
	// Props
	export let isVisible = false;
	
	// Performance metrics
	let fps = 0;
	let frameCount = 0;
	let lastTime = 0;
	let animationId: number;
	
	onMount(() => {
		updateFPS();
	});
	
	onDestroy(() => {
		if (animationId) {
			cancelAnimationFrame(animationId);
		}
	});
	
	function updateFPS() {
		const now = performance.now();
		frameCount++;
		
		if (now >= lastTime + 1000) {
			fps = Math.round((frameCount * 1000) / (now - lastTime));
			frameCount = 0;
			lastTime = now;
		}
		
		animationId = requestAnimationFrame(updateFPS);
	}
</script>

{#if isVisible}
	<div class="fixed top-4 left-4 bg-base-200 p-3 rounded-lg shadow-lg z-50">
		<div class="text-sm font-mono">
			<div class="flex items-center space-x-2">
				<span class="text-base-content/70">FPS:</span>
				<span class="font-bold {fps >= 55 ? 'text-success' : fps >= 30 ? 'text-warning' : 'text-error'}">
					{fps}
				</span>
			</div>
			<div class="text-xs text-base-content/50 mt-1">
				Target: 60 FPS
			</div>
		</div>
	</div>
{/if} 