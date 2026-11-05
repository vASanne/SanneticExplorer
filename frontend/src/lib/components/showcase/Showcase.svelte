<script lang="ts">
  import { onMount } from "svelte";
  import { browserApiBase, getPlanets, type PlanetData } from "$lib/api";
  import { MOON, SUN } from "$lib/solar/catalog";
  import {
    earthYearCaption,
    formatDistance,
    formatGravity,
    formatMass,
    formatPeriod,
    formatRadius,
    formatSidereal,
    formatSigned,
    formatTemperature,
  } from "$lib/solar/format";
  import type { Orrery } from "$lib/solar/Orrery";
  import { resolvePlanets, type ResolvedBody } from "$lib/solar/resolve";
  import { EARTH_YEAR_SECONDS, type ScaleMode } from "$lib/solar/scale";
  import { spinSummary } from "$lib/solar/spin";
  import { formatSimDate as formatJulian, julianNow } from "$lib/solar/time";
  import "./chrome.css";

  export let planets: PlanetData[] = [];
  export let error: string | null = null;

  const speedSteps = [-1000, -100, -10, -1, 1, 10, 100, 1000];

  let viewport: HTMLDivElement;
  let orrery: Orrery | null = null;
  let playing = false;
  let speedIndex = speedSteps.indexOf(1);
  let showOrbits = true;
  let showLabels = true;
  let selectedName: string | null = null;
  let scale: ScaleMode = "showcase";
  let simLabel = "—";

  $: model = resolvePlanets(planets);
  $: selected =
    model.planets.find((body) => body.name === selectedName) ?? null;
  $: speed = speedSteps[speedIndex];
  $: speedLabel = speed < 0 ? `−${Math.abs(speed)}×` : `${speed}×`;
  $: yearCaption = earthYearCaption(speed, EARTH_YEAR_SECONDS);

  $: if (orrery) orrery.setScale(scale);
  $: if (orrery) orrery.setPlanets(model.planets);
  $: if (orrery) orrery.setPlaying(playing);
  $: if (orrery) orrery.setSpeed(speed);
  $: if (orrery) orrery.setOrbitsVisible(showOrbits);
  $: if (orrery) orrery.setLabelsVisible(showLabels);
  $: if (orrery) orrery.setSelected(selectedName);

  function choose(name: string) {
    selectedName = name;
    orrery?.focus(name);
  }

  function goToday() {
    const jd = julianNow();
    orrery?.setJulianDay(jd);
    simLabel = formatJulian(jd);
  }

  function slower() {
    speedIndex = Math.max(0, speedIndex - 1);
  }

  function faster() {
    speedIndex = Math.min(speedSteps.length - 1, speedIndex + 1);
  }

  function onKey(event: KeyboardEvent) {
    const tag = (event.target as HTMLElement | null)?.tagName;
    if (
      tag === "INPUT" ||
      tag === "TEXTAREA" ||
      tag === "BUTTON" ||
      tag === "A"
    )
      return;
    if (event.code === "Space") {
      event.preventDefault();
      playing = !playing;
    } else if (event.key === "Escape") {
      selectedName = null;
    }
  }

  onMount(() => {
    simLabel = formatJulian(julianNow());
    const reduced =
      window.matchMedia?.("(prefers-reduced-motion: reduce)")?.matches ?? false;
    if (reduced) playing = false;
    let cancelled = false;
    window.addEventListener("keydown", onKey);
    import("$lib/solar/Orrery").then(({ Orrery: OrreryScene }) => {
      if (cancelled) return;
      orrery = new OrreryScene(viewport, {
        onSelect: (name) => {
          selectedName = name;
        },
        onTime: (jd) => {
          const label = formatJulian(jd);
          if (label !== simLabel) simLabel = label;
        },
      });
      orrery.setPlanets(model.planets);
      orrery.setPlaying(playing);
      orrery.setSpeed(speed);
      orrery.setOrbitsVisible(showOrbits);
      orrery.setLabelsVisible(showLabels);
    });

    if (model.origin !== "live") {
      getPlanets(browserApiBase())
        .then((live) => {
          if (!cancelled && live.length > 0) {
            planets = live;
            error = null;
          }
        })
        .catch(() => {
          /* The reference catalog stays on screen. */
        });
    }

    return () => {
      cancelled = true;
      window.removeEventListener("keydown", onKey);
      orrery?.dispose();
      orrery = null;
    };
  });

  function factsFor(body: ResolvedBody): Array<[string, string]> {
    const spin = spinSummary(body.name);
    const rows: Array<[string, string]> = [
      ["Distance", formatDistance(body.distanceAu)],
      ["Period", formatPeriod(body.orbitalPeriodDays)],
      ["Eccentricity", formatSigned(body.eccentricity, 4)],
      ["Inclination", formatSigned(body.inclinationDeg, 2, "°")],
    ];
    if (spin) {
      rows.push(["Axial tilt", formatSigned(spin.obliquityDeg, 2, "°")]);
      rows.push(["Sidereal day", formatSidereal(spin.siderealHours)]);
    }
    rows.push(
      ["Radius", formatRadius(body.radiusKm)],
      ["Mass", formatMass(body.massKg)],
      ["Gravity", formatGravity(body.gravityMs2)],
      ["Temperature", formatTemperature(body.temperatureK)],
      ["Atmosphere", body.atmosphere ?? "None"],
      ["Rings", body.hasRings ? "Yes" : "No"]
    );
    return rows;
  }
</script>

<svelte:head>
  <title>Sannetic Explorer</title>
  <meta
    name="description"
    content="A live orrery of the solar system. Sun and eight planets, fed by the Sannetic Explorer API."
  />
</svelte:head>

<div class="sx-shell">
  <div class="sx-viewport" bind:this={viewport} />

  <header class="sx-top">
    <a class="sx-brand" href="/">
      <div class="sx-wordmark">Sannetic <span>Explorer</span></div>
      <p class="sx-eyebrow">Solar system</p>
    </a>
    <a
      class="sx-pill"
      href="/dashboard"
      data-testid="data-status"
      title={error || "Open live data status"}
    >
      <span class="sx-dot" class:live={model.origin === "live"} />
      {#if model.origin === "live"}
        Live · {model.liveCount} planets
      {:else if model.origin === "partial"}
        Partial · {model.liveCount} live
      {:else}
        Reference catalog
      {/if}
    </a>
  </header>

  <nav class="sx-rail" data-testid="body-rail" aria-label="Celestial bodies">
    <button
      type="button"
      aria-current={selectedName === "Sun" ? "true" : undefined}
      on:click={() => choose("Sun")}>Sun</button
    >
    {#each model.planets as body}
      <button
        type="button"
        aria-current={selectedName === body.name ? "true" : undefined}
        on:click={() => choose(body.name)}
      >
        {body.name}
      </button>
      {#if body.name === "Earth"}
        <button
          type="button"
          aria-current={selectedName === "Moon" ? "true" : undefined}
          on:click={() => choose("Moon")}
        >
          Moon
        </button>
      {/if}
    {/each}
  </nav>

  {#if selectedName === "Sun"}
    <aside class="sx-panel" data-testid="info-panel">
      <header>
        <div>
          <p class="sx-kicker">Star</p>
          <h2>Sun</h2>
        </div>
        <button
          type="button"
          class="sx-text-button"
          on:click={() => (selectedName = null)}>Close</button
        >
      </header>
      <p class="sx-note">{SUN.summary}</p>
      <dl class="sx-facts">
        <div>
          <dt>Radius</dt>
          <dd>{formatRadius(SUN.radiusKm)}</dd>
        </div>
        <div>
          <dt>Mass</dt>
          <dd>{formatMass(SUN.massKg)}</dd>
        </div>
        <div>
          <dt>Temperature</dt>
          <dd>{formatTemperature(SUN.temperatureK)}</dd>
        </div>
        <div>
          <dt>Class</dt>
          <dd>{SUN.subtype}</dd>
        </div>
      </dl>
    </aside>
  {:else if selected}
    <aside class="sx-panel" data-testid="info-panel">
      <header>
        <div>
          <p class="sx-kicker">
            {selected.origin === "live" ? "Live /planets" : "Reference catalog"}
          </p>
          <h2>{selected.name}</h2>
        </div>
        <button
          type="button"
          class="sx-text-button"
          on:click={() => (selectedName = null)}>Close</button
        >
      </header>
      <p class="sx-note">
        {selected.subtype}.
        {#if selected.origin === "live"}
          Sizes and J2000 elements follow the API. Missing angles use the JPL
          tables, with secular rates. Tilt and spin follow the IAU poles.
        {:else}
          This body is not in the current API payload, so the JPL reference
          elements are shown.
        {/if}
      </p>
      <dl class="sx-facts">
        {#each factsFor(selected) as fact}
          <div>
            <dt>{fact[0]}</dt>
            <dd>{fact[1]}</dd>
          </div>
        {/each}
      </dl>
    </aside>
  {:else if selectedName === "Moon"}
    <aside class="sx-panel" data-testid="info-panel">
      <header>
        <div>
          <p class="sx-kicker">Earth’s moon</p>
          <h2>Moon</h2>
        </div>
        <button
          type="button"
          class="sx-text-button"
          on:click={() => (selectedName = null)}>Close</button
        >
      </header>
      <p class="sx-note">{MOON.summary}</p>
      <dl class="sx-facts">
        <div>
          <dt>Distance</dt>
          <dd>{MOON.distanceKm.toLocaleString("en-US")} km</dd>
        </div>
        <div>
          <dt>Period</dt>
          <dd>{formatPeriod(MOON.periodDays)}</dd>
        </div>
        <div>
          <dt>Eccentricity</dt>
          <dd>{formatSigned(MOON.eccentricity, 4)}</dd>
        </div>
        <div>
          <dt>Inclination</dt>
          <dd>{formatSigned(MOON.inclinationDeg, 2, "°")}</dd>
        </div>
        <div>
          <dt>Radius</dt>
          <dd>{formatRadius(MOON.radiusKm)}</dd>
        </div>
        <div>
          <dt>Sidereal day</dt>
          <dd>{formatSidereal(spinSummary("Moon")?.siderealHours ?? 0)}</dd>
        </div>
      </dl>
    </aside>
  {/if}

  <div class="sx-dock" data-testid="playback">
    <button type="button" data-testid="today" on:click={goToday}>Today</button>
    <time class="sx-date" data-testid="sim-date">{simLabel}</time>
    <span class="sx-rule" />
    <button
      type="button"
      data-testid="play-toggle"
      aria-pressed={playing ? "true" : "false"}
      aria-label={playing ? "Pause orbit animation" : "Play orbit animation"}
      on:click={() => (playing = !playing)}
    >
      {playing ? "Pause" : "Play"}
    </button>
    <button
      type="button"
      data-testid="speed-slower"
      aria-label="Slower, including reverse"
      on:click={slower}>−</button
    >
    <span class="sx-caption" data-testid="speed-readout">{speedLabel}</span>
    <button
      type="button"
      data-testid="speed-faster"
      aria-label="Faster"
      on:click={faster}>+</button
    >
    <span class="sx-caption sx-year">{yearCaption}</span>
    <span class="sx-rule" />
    <button
      type="button"
      aria-pressed={showOrbits ? "true" : "false"}
      on:click={() => (showOrbits = !showOrbits)}>Orbits</button
    >
    <button
      type="button"
      aria-pressed={showLabels ? "true" : "false"}
      on:click={() => (showLabels = !showLabels)}>Labels</button
    >
    <button
      type="button"
      data-testid="scale-toggle"
      aria-pressed={scale === "true" ? "true" : "false"}
      on:click={() => (scale = scale === "true" ? "showcase" : "true")}
    >
      {scale === "true" ? "True scale" : "Showcase"}
    </button>
    <span class="sx-rule" />
    <button
      type="button"
      data-testid="view-inner"
      on:click={() => orrery?.frame("inner")}>Inner</button
    >
    <button
      type="button"
      data-testid="view-system"
      on:click={() => orrery?.frame("system")}>System</button
    >
  </div>
</div>
