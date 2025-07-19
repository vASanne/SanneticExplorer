<script lang="ts">
	import { writable } from 'svelte/store';
	
	// Create local speedFactor store
	export const speedFactor = writable(1.0);
	
	// Speed control options
	const speedOptions = [
		{ label: 'Pause', value: 0 },
		{ label: '0.1x', value: 0.1 },
		{ label: '0.5x', value: 0.5 },
		{ label: '1x', value: 1.0 },
		{ label: '2x', value: 2.0 },
		{ label: '5x', value: 5.0 },
		{ label: '10x', value: 10.0 }
	];
	
	// Current speed factor
	$: currentSpeed = $speedFactor;
</script>

<div class="speed-control bg-base-200 p-4 rounded-lg">
	<h3 class="text-lg font-semibold mb-3">Simulation Speed</h3>
	
	<!-- Speed buttons -->
	<div class="flex flex-wrap gap-2 mb-3">
		{#each speedOptions as option}
			<button
				class="btn btn-sm {currentSpeed === option.value ? 'btn-primary' : 'btn-outline'}"
				on:click={() => speedFactor.set(option.value)}
			>
				{option.label}
			</button>
		{/each}
	</div>
	
	<!-- Custom speed slider -->
	<div class="form-control">
		<label class="label">
			<span class="label-text">Custom Speed: {currentSpeed.toFixed(1)}x</span>
		</label>
		<input
			type="range"
			min="0"
			max="20"
			step="0.1"
			bind:value={currentSpeed}
			class="range range-primary"
			on:input={() => speedFactor.set(currentSpeed)}
		/>
		<div class="flex justify-between text-xs text-base-content/70">
			<span>0x</span>
			<span>10x</span>
			<span>20x</span>
		</div>
	</div>
	
	<!-- Current status -->
	<div class="text-sm text-base-content/70 mt-2">
		{#if currentSpeed === 0}
			<span class="text-warning">Simulation paused</span>
		{:else if currentSpeed < 1}
			<span class="text-info">Slow motion</span>
		{:else if currentSpeed > 1}
			<span class="text-success">Fast forward</span>
		{:else}
			<span class="text-success">Normal speed</span>
		{/if}
	</div>
</div> 