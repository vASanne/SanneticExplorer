<script lang="ts">
  import { _, locale } from "svelte-i18n";
  import { bodyName, subtypeName, tOr } from "$lib/i18n/copy";
  import type { StatusLoad } from "$lib/solar/loads";
  import LocaleSwitch from "./LocaleSwitch.svelte";
  import "./chrome.css";

  export let data: StatusLoad;

  $: planetNames = data.planets.map((planet) => planet.name);
  $: typeEntries = Object.entries(data.stats?.by_type ?? {}).filter(
    ([, count]) => count > 0
  );
  $: errorText = data.error
    ? tOr(`errors.${data.error}`, $_("errors.request_failed"))
    : "";
  $: healthText = data.health
    ? tOr(`health.${data.health}`, data.health)
    : $_("status.unreachable");
</script>

<svelte:head>
  <title>{$_("status.pageTitle")}</title>
</svelte:head>

{#key $locale}
  <main class="sx-status">
    <header class="sx-status-head">
      <a class="sx-brand" href="/">
        <div class="sx-wordmark">
          {$_("brand.lead")} <span>{$_("brand.mark")}</span>
        </div>
        <p class="sx-eyebrow">{$_("status.eyebrow")}</p>
      </a>
      <LocaleSwitch />
    </header>

    <section class="sx-status-card">
      <p class="sx-kicker">{$_("status.backend")}</p>
      <h1>{$_("status.heading")}</h1>
      <p class="sx-note">{@html $_("status.note")}</p>

      <dl class="sx-meta">
        <dt>{$_("status.browserApi")}</dt>
        <dd>{data.publicApiUrl}</dd>
        <dt>{$_("status.serverApi")}</dt>
        <dd>{data.internalApiUrl}</dd>
        <dt>{$_("status.health")}</dt>
        <dd>{healthText}</dd>
        <dt>{$_("status.bodies")}</dt>
        <dd>{data.stats ? data.stats.total_celestial_bodies : "—"}</dd>
        <dt>{$_("status.planets")}</dt>
        <dd>{data.planets.length}</dd>
      </dl>

      {#if typeEntries.length}
        <dl class="sx-meta">
          {#each typeEntries as [kind, count]}
            <dt>{subtypeName(kind)}</dt>
            <dd>{count}</dd>
          {/each}
        </dl>
      {/if}

      {#if planetNames.length}
        <div class="sx-names" data-testid="planet-names">
          {#each planetNames as name}
            <span>{bodyName(name)}</span>
          {/each}
        </div>
      {:else}
        <p class="sx-note">{$_("status.empty")}</p>
      {/if}

      {#if errorText}
        <p class="sx-error">{errorText}</p>
      {/if}

      <p>
        <a class="sx-text-button" href="/">{$_("status.openSystem")}</a>
        <a class="sx-text-button" href="{data.publicApiUrl}/docs"
          >{$_("status.apiDocs")}</a
        >
      </p>
    </section>
  </main>
{/key}
