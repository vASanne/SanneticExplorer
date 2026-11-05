<script lang="ts">
  import { browser } from "$app/environment";
  import { locale } from "$lib/i18n";
  import "../app.css";

  $: if (browser && $locale) document.documentElement.lang = $locale;
</script>

<div class="min-h-screen" style="background:#05060a;color:#ece8e1">
  <slot />
</div>
