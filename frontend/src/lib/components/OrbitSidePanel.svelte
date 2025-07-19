<script lang="ts">
	import { createEventDispatcher } from 'svelte';
	import type { CelestialBody } from '$lib/api';
	import { writable } from 'svelte/store';
	
	// Props
	export let bodies: CelestialBody[] = [];
	export let isOpen = false;
	
	// Events
	const dispatch = createEventDispatcher();
	
	// Local state
	let editingBody: CelestialBody | null = null;
	let editForm = {
		radius_km: 0,
		orbital_radius_km: 0,
		orbital_speed_kms: 0,
		color_hex: '#aaaaaa'
	};
	
	// API base URL
	const API_BASE_URL = import.meta.env.PUBLIC_API_URL || 'http://localhost:8000';
	
	// Group bodies by type
	$: groupedBodies = bodies.reduce((groups, body) => {
		const type = body.body_type || 'Unknown';
		if (!groups[type]) {
			groups[type] = [];
		}
		groups[type].push(body);
		return groups;
	}, {} as Record<string, CelestialBody[]>);
	
	// Handle body click - center camera
	function centerOnBody(body: CelestialBody) {
		dispatch('centerCamera', { body });
	}
	
	// Handle edit button click
	function startEditing(body: CelestialBody) {
		editingBody = body;
		editForm = {
			radius_km: body.radius_km || 0,
			orbital_radius_km: (body.mean_distance_au || 0) * 149597870.7, // Convert AU to km
			orbital_speed_kms: body.orbital_speed_kms || 0,
			color_hex: getBodyColor(body)
		};
	}
	
	// Handle save button click
	async function saveChanges() {
		if (!editingBody) return;
		
		try {
			// Prepare update data
			const updateData = {
				...editingBody,
				radius_km: editForm.radius_km,
				mean_distance_au: editForm.orbital_radius_km / 149597870.7, // Convert km to AU
				orbital_speed_kms: editForm.orbital_speed_kms
			};
			
			// Call API
			const response = await fetch(`${API_BASE_URL}/bodies/${editingBody.id}`, {
				method: 'PUT',
				headers: {
					'Content-Type': 'application/json',
				},
				body: JSON.stringify(updateData)
			});
			
			if (!response.ok) {
				throw new Error(`HTTP error! status: ${response.status}`);
			}
			
			const updatedBody = await response.json();
			
			// Optimistically update local store
			dispatch('bodyUpdated', { 
				oldBody: editingBody, 
				newBody: updatedBody.data || updatedBody 
			});
			
			// Close edit mode
			editingBody = null;
			
		} catch (error) {
			console.error('Error updating body:', error);
			// You could add a toast notification here
		}
	}
	
	// Handle cancel button click
	function cancelEdit() {
		editingBody = null;
	}
	
	// Get body color (same logic as SolarSystemCanvas)
	function getBodyColor(body: CelestialBody): string {
		switch (body.body_type?.toLowerCase()) {
			case 'star':
				return '#ffff00';
			case 'planet':
				switch (body.name?.toLowerCase()) {
					case 'mercury': return '#8c7853';
					case 'venus': return '#e7cdcd';
					case 'earth': return '#6b93d6';
					case 'mars': return '#c1440e';
					case 'jupiter': return '#d8ca9d';
					case 'saturn': return '#fad5a5';
					case 'uranus': return '#d1e7e7';
					case 'neptune': return '#5b5ddf';
					default: return '#aaaaaa';
				}
			case 'moon':
				return '#c0c0c0';
			case 'satellite':
				return '#ff6b35';
			default:
				return '#aaaaaa';
		}
	}
	
	// Format distance for display
	function formatDistance(km: number): string {
		if (km >= 1000000) {
			return `${(km / 1000000).toFixed(2)}M km`;
		} else if (km >= 1000) {
			return `${(km / 1000).toFixed(2)}k km`;
		}
		return `${km.toFixed(2)} km`;
	}
</script>

<!-- Side Panel Container -->
<div class="fixed top-0 right-0 h-full w-80 bg-base-100 shadow-xl transform transition-transform duration-300 ease-in-out {isOpen ? 'translate-x-0' : 'translate-x-full'} z-50">
	<div class="h-full flex flex-col">
		<!-- Header -->
		<div class="p-4 border-b border-base-300">
			<div class="flex justify-between items-center">
				<h2 class="text-xl font-bold">Celestial Bodies</h2>
				<button 
					class="btn btn-ghost btn-sm"
					on:click={() => dispatch('close')}
				>
					<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
					</svg>
				</button>
			</div>
			<p class="text-sm text-base-content/70 mt-1">
				{bodies.length} bodies loaded
			</p>
		</div>
		
		<!-- Body List -->
		<div class="flex-1 overflow-y-auto p-4 space-y-4">
			{#each Object.entries(groupedBodies) as [type, typeBodies]}
				<div class="card bg-base-200 shadow-sm">
					<div class="card-body p-4">
						<h3 class="card-title text-lg capitalize">{type}</h3>
						<div class="space-y-2">
							{#each typeBodies as body}
								<div class="flex items-center justify-between p-2 bg-base-100 rounded-lg hover:bg-base-300 transition-colors">
									<div class="flex items-center space-x-3 flex-1">
										<!-- Color indicator -->
										<div 
											class="w-4 h-4 rounded-full border border-base-300"
											style="background-color: {getBodyColor(body)}"
										></div>
										
										<!-- Body info -->
										<div class="flex-1 min-w-0">
											<div class="font-medium truncate">{body.name}</div>
											<div class="text-xs text-base-content/70">
												{formatDistance(body.radius_km || 0)} • {formatDistance((body.mean_distance_au || 0) * 149597870.7)}
											</div>
										</div>
									</div>
									
									<!-- Action buttons -->
									<div class="flex space-x-1">
										<button 
											class="btn btn-ghost btn-xs"
											on:click={() => centerOnBody(body)}
											title="Center camera"
										>
											<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>
											</svg>
										</button>
										<button 
											class="btn btn-ghost btn-xs"
											on:click={() => startEditing(body)}
											title="Edit properties"
										>
											<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
											</svg>
										</button>
									</div>
								</div>
							{/each}
						</div>
					</div>
				</div>
			{/each}
		</div>
		
		<!-- Edit Form Modal -->
		{#if editingBody}
			<div class="p-4 border-t border-base-300 bg-base-200">
				<div class="card bg-base-100 shadow-lg">
					<div class="card-body p-4">
						<h3 class="card-title text-lg">Edit {editingBody.name}</h3>
						
						<div class="space-y-4">
							<!-- Radius -->
							<div class="form-control">
								<label class="label">
									<span class="label-text">Radius (km)</span>
								</label>
								<input 
									type="number" 
									bind:value={editForm.radius_km}
									class="input input-bordered input-sm"
									min="0"
									step="100"
								/>
							</div>
							
							<!-- Orbital Radius -->
							<div class="form-control">
								<label class="label">
									<span class="label-text">Orbital Radius (km)</span>
								</label>
								<input 
									type="number" 
									bind:value={editForm.orbital_radius_km}
									class="input input-bordered input-sm"
									min="0"
									step="1000000"
								/>
							</div>
							
							<!-- Orbital Speed -->
							<div class="form-control">
								<label class="label">
									<span class="label-text">Orbital Speed (km/s)</span>
								</label>
								<input 
									type="number" 
									bind:value={editForm.orbital_speed_kms}
									class="input input-bordered input-sm"
									min="0"
									step="0.1"
								/>
							</div>
							
							<!-- Color -->
							<div class="form-control">
								<label class="label">
									<span class="label-text">Color</span>
								</label>
								<input 
									type="color" 
									bind:value={editForm.color_hex}
									class="input input-bordered input-sm h-10"
								/>
							</div>
						</div>
						
						<!-- Action buttons -->
						<div class="card-actions justify-end mt-4">
							<button 
								class="btn btn-ghost btn-sm"
								on:click={cancelEdit}
							>
								Cancel
							</button>
							<button 
								class="btn btn-primary btn-sm"
								on:click={saveChanges}
							>
								Save
							</button>
						</div>
					</div>
				</div>
			</div>
		{/if}
	</div>
</div>

<!-- Backdrop -->
{#if isOpen}
	<div 
		class="fixed inset-0 bg-black bg-opacity-50 z-40"
		on:click={() => dispatch('close')}
	></div>
{/if} 