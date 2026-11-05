<script lang="ts">
  import { _ } from "svelte-i18n";
  import { locale, setAppLocale, type AppLocale } from "$lib/i18n";

  const codes: AppLocale[] = ["de", "en"];
</script>

<div class="sx-locales" role="group" aria-label={$_("aria.language")}>
  {#each codes as code}
    <button
      type="button"
      data-testid="locale-{code}"
      aria-pressed={$locale === code ? "true" : "false"}
      on:click={() => setAppLocale(code)}
    >
      {$_(`locale.${code}`)}
    </button>
  {/each}
</div>
