<script lang="ts">
	import StatusPage from '$lib/components/showcase/StatusPage.svelte';
	import type { PageData } from './$types';

	export let data: PageData;
</script>

<StatusPage {data} />
