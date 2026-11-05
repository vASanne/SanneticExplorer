<script lang="ts">
	import type { StatusLoad } from '$lib/solar/loads';
	import './chrome.css';

	export let data: StatusLoad;

	$: planetNames = data.planets.map((planet) => planet.name);
	$: typeEntries = Object.entries(data.stats?.by_type ?? {}).filter(([, count]) => count > 0);
</script>

<svelte:head>
	<title>Live data · Sannetic Explorer</title>
</svelte:head>

<main class="sx-status">
	<a class="sx-brand" href="/">
		<div class="sx-wordmark">Sannetic <span>Explorer</span></div>
		<p class="sx-eyebrow">Live data</p>
	</a>

	<section class="sx-status-card">
		<p class="sx-kicker">Backend</p>
		<h1>System status</h1>
		<p class="sx-note">
			The orrery reads <code>/planets</code>. An empty database used to leave only the Sun, so the
			backend imports the eight planets on startup. Run <code>make db-migrate</code> to import again.
		</p>

		<dl class="sx-meta">
			<dt>Browser API</dt>
			<dd>{data.publicApiUrl}</dd>
			<dt>Server API</dt>
			<dd>{data.internalApiUrl}</dd>
			<dt>Health</dt>
			<dd>{data.health ?? 'unreachable'}</dd>
			<dt>Bodies</dt>
			<dd>{data.stats ? data.stats.total_celestial_bodies : '—'}</dd>
			<dt>Planets</dt>
			<dd>{data.planets.length}</dd>
		</dl>

		{#if typeEntries.length}
			<dl class="sx-meta">
				{#each typeEntries as [kind, count]}
					<dt>{kind}</dt>
					<dd>{count}</dd>
				{/each}
			</dl>
		{/if}

		{#if planetNames.length}
			<div class="sx-names" data-testid="planet-names">
				{#each planetNames as name}
					<span>{name}</span>
				{/each}
			</div>
		{:else}
			<p class="sx-note">No planet rows yet. The showcase still draws the reference solar system.</p>
		{/if}

		{#if data.error}
			<p class="sx-error">{data.error}</p>
		{/if}

		<p>
			<a class="sx-text-button" href="/">Open the solar system</a>
			<a class="sx-text-button" href="{data.publicApiUrl}/docs">API docs</a>
		</p>
	</section>
</main>
