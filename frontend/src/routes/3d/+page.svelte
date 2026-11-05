<script lang="ts">
	import Showcase from '$lib/components/showcase/Showcase.svelte';
	import type { PageData } from './$types';

	export let data: PageData;
</script>

<Showcase planets={data.planets} error={data.error} />
