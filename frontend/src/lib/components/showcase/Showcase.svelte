<script lang="ts">
  import { onMount } from "svelte";
  import { _, locale } from "svelte-i18n";
  import { browserApiBase, getPlanets, type PlanetData } from "$lib/api";
  import { bodyName, subtypeName, tOr } from "$lib/i18n/copy";
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
  import {
    DEFAULT_SCALE_MODE,
    EARTH_YEAR_SECONDS,
    type ScaleMode,
  } from "$lib/solar/scale";
  import { spinSummary } from "$lib/solar/spin";
  import { formatSimDate as formatJulian, julianNow } from "$lib/solar/time";
  import LocaleSwitch from "./LocaleSwitch.svelte";
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
  let scale: ScaleMode = DEFAULT_SCALE_MODE;
  let simJd = julianNow();

  $: model = resolvePlanets(planets);
  $: selected =
    model.planets.find((body) => body.name === selectedName) ?? null;
  $: speed = speedSteps[speedIndex];
  $: speedLabel = speed < 0 ? `−${Math.abs(speed)}×` : `${speed}×`;
  $: yearCaption = $locale ? earthYearCaption(speed, EARTH_YEAR_SECONDS) : "";
  $: simLabel = $locale ? formatJulian(simJd) : "—";
  $: originLabel =
    model.origin === "live"
      ? $_("status.live", { values: { count: model.liveCount } })
      : model.origin === "partial"
      ? $_("status.partial", { values: { count: model.liveCount } })
      : $_("status.reference");
  $: errorTitle = error
    ? tOr(`errors.${error}`, $_("errors.request_failed"))
    : $_("status.open");

  $: if (orrery) orrery.setScale(scale);
  $: if (orrery) orrery.setPlanets(model.planets);
  $: if (orrery) orrery.setPlaying(playing);
  $: if (orrery) orrery.setSpeed(speed);
  $: if (orrery) orrery.setOrbitsVisible(showOrbits);
  $: if (orrery) orrery.setLabelsVisible(showLabels);
  $: if (orrery) orrery.setSelected(selectedName);

  function choose(name: string) {
    if (name === "Moon" && scale !== "true") {
      scale = "true";
      orrery?.setScale("true");
    }
    selectedName = name;
    orrery?.focus(name);
  }

  function showEarthMoon() {
    scale = "true";
    orrery?.setScale("true");
    orrery?.frame("local");
  }

  function toggleScale() {
    scale = scale === "true" ? "showcase" : "true";
    if (scale !== "true" && selectedName === "Moon") selectedName = "Earth";
  }

  function goToday() {
    const jd = julianNow();
    orrery?.setJulianDay(jd);
    simJd = jd;
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
          if (jd !== simJd) simJd = jd;
        },
      });
      orrery.setPlanets(model.planets);
      orrery.setPlaying(playing);
      orrery.setSpeed(speed);
      orrery.setOrbitsVisible(showOrbits);
      orrery.setLabelsVisible(showLabels);
      const params = new URLSearchParams(window.location.search);
      const jd = Number(params.get("jd"));
      if (Number.isFinite(jd) && jd > 2000000) {
        orrery.setJulianDay(jd);
        simJd = jd;
      }
      const view = params.get("view");
      if (view === "local") {
        scale = "true";
        orrery.setScale("true");
        orrery.frame("local");
      } else if (view === "inner" || view === "system") {
        orrery.frame(view);
      }
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

  type Translate = (
    id: string,
    options?: { values?: Record<string, string | number> }
  ) => string;

  function factsFor(
    body: ResolvedBody,
    translate: Translate
  ): Array<[string, string]> {
    const spin = spinSummary(body.name);
    const rows: Array<[string, string]> = [
      [translate("facts.distance"), formatDistance(body.distanceAu)],
      [translate("facts.period"), formatPeriod(body.orbitalPeriodDays)],
      [translate("facts.eccentricity"), formatSigned(body.eccentricity, 4)],
      [
        translate("facts.inclination"),
        formatSigned(body.inclinationDeg, 2, "°"),
      ],
    ];
    if (spin) {
      rows.push([
        translate("facts.tilt"),
        formatSigned(spin.obliquityDeg, 2, "°"),
      ]);
      rows.push([
        translate("facts.sidereal"),
        formatSidereal(spin.siderealHours),
      ]);
    }
    rows.push(
      [translate("facts.radius"), formatRadius(body.radiusKm)],
      [translate("facts.mass"), formatMass(body.massKg)],
      [translate("facts.gravity"), formatGravity(body.gravityMs2)],
      [translate("facts.temperature"), formatTemperature(body.temperatureK)],
      [
        translate("facts.atmosphere"),
        body.atmosphere ?? translate("facts.none"),
      ],
      [
        translate("facts.rings"),
        body.hasRings ? translate("facts.yes") : translate("facts.no"),
      ]
    );
    return rows;
  }
</script>

<svelte:head>
  <title>{$_("meta.title")}</title>
  <meta name="description" content={$_("meta.description")} />
</svelte:head>

<div class="sx-shell">
  <div class="sx-viewport" bind:this={viewport} />

  {#key $locale}
    <header class="sx-top">
      <a class="sx-brand" href="/">
        <div class="sx-wordmark">
          {$_("brand.lead")} <span>{$_("brand.mark")}</span>
        </div>
        <p class="sx-eyebrow">{$_("brand.eyebrow")}</p>
      </a>
      <div class="sx-top-actions">
        <LocaleSwitch />
        <a
          class="sx-pill"
          href="/dashboard"
          data-testid="data-status"
          title={errorTitle}
        >
          <span class="sx-dot" class:live={model.origin === "live"} />
          {originLabel}
        </a>
      </div>
    </header>

    <nav class="sx-rail" data-testid="body-rail" aria-label={$_("aria.bodies")}>
      <button
        type="button"
        aria-current={selectedName === "Sun" ? "true" : undefined}
        on:click={() => choose("Sun")}>{bodyName("Sun")}</button
      >
      {#each model.planets as body}
        <button
          type="button"
          aria-current={selectedName === body.name ? "true" : undefined}
          on:click={() => choose(body.name)}
        >
          {bodyName(body.name)}
        </button>
        {#if body.name === "Earth"}
          <button
            type="button"
            aria-current={selectedName === "Moon" ? "true" : undefined}
            on:click={() => choose("Moon")}
          >
            {bodyName("Moon")}
          </button>
        {/if}
      {/each}
    </nav>

    {#if selectedName === "Sun"}
      <aside class="sx-panel" data-testid="info-panel">
        <header>
          <div>
            <p class="sx-kicker">{$_("panels.star")}</p>
            <h2>{bodyName("Sun")}</h2>
          </div>
          <button
            type="button"
            class="sx-text-button"
            on:click={() => (selectedName = null)}>{$_("panels.close")}</button
          >
        </header>
        <p class="sx-note">{$_("panels.sunSummary")}</p>
        <dl class="sx-facts">
          <div>
            <dt>{$_("facts.radius")}</dt>
            <dd>{formatRadius(SUN.radiusKm)}</dd>
          </div>
          <div>
            <dt>{$_("facts.mass")}</dt>
            <dd>{formatMass(SUN.massKg)}</dd>
          </div>
          <div>
            <dt>{$_("facts.temperature")}</dt>
            <dd>{formatTemperature(SUN.temperatureK)}</dd>
          </div>
          <div>
            <dt>{$_("facts.class")}</dt>
            <dd>{subtypeName(SUN.subtype)}</dd>
          </div>
        </dl>
      </aside>
    {:else if selected}
      <aside class="sx-panel" data-testid="info-panel">
        <header>
          <div>
            <p class="sx-kicker">
              {selected.origin === "live"
                ? $_("panels.live")
                : $_("panels.reference")}
            </p>
            <h2>{bodyName(selected.name)}</h2>
          </div>
          <button
            type="button"
            class="sx-text-button"
            on:click={() => (selectedName = null)}>{$_("panels.close")}</button
          >
        </header>
        <p class="sx-note">
          {subtypeName(selected.subtype)}.
          {selected.origin === "live"
            ? $_("panels.liveNote")
            : $_("panels.referenceNote")}
        </p>
        <dl class="sx-facts">
          {#each factsFor(selected, $_) as fact}
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
            <p class="sx-kicker">{$_("panels.moon")}</p>
            <h2>{bodyName("Moon")}</h2>
          </div>
          <button
            type="button"
            class="sx-text-button"
            on:click={() => (selectedName = null)}>{$_("panels.close")}</button
          >
        </header>
        <p class="sx-note">{$_("panels.moonSummary")}</p>
        <dl class="sx-facts">
          <div>
            <dt>{$_("facts.distance")}</dt>
            <dd>{formatRadius(MOON.distanceKm)}</dd>
          </div>
          <div>
            <dt>{$_("facts.period")}</dt>
            <dd>{formatPeriod(MOON.periodDays)}</dd>
          </div>
          <div>
            <dt>{$_("facts.eccentricity")}</dt>
            <dd>{formatSigned(MOON.eccentricity, 4)}</dd>
          </div>
          <div>
            <dt>{$_("facts.inclination")}</dt>
            <dd>{formatSigned(MOON.inclinationDeg, 2, "°")}</dd>
          </div>
          <div>
            <dt>{$_("facts.radius")}</dt>
            <dd>{formatRadius(MOON.radiusKm)}</dd>
          </div>
          <div>
            <dt>{$_("facts.sidereal")}</dt>
            <dd>{formatSidereal(spinSummary("Moon")?.siderealHours ?? 0)}</dd>
          </div>
        </dl>
      </aside>
    {/if}

    <div class="sx-dock" data-testid="playback">
      <button type="button" data-testid="today" on:click={goToday}
        >{$_("dock.today")}</button
      >
      <time class="sx-date" data-testid="sim-date">{simLabel}</time>
      <span class="sx-rule" />
      <button
        type="button"
        data-testid="play-toggle"
        aria-pressed={playing ? "true" : "false"}
        aria-label={playing ? $_("dock.pauseAria") : $_("dock.playAria")}
        on:click={() => (playing = !playing)}
      >
        {playing ? $_("dock.pause") : $_("dock.play")}
      </button>
      <button
        type="button"
        data-testid="speed-slower"
        aria-label={$_("dock.slower")}
        on:click={slower}>−</button
      >
      <span class="sx-caption" data-testid="speed-readout">{speedLabel}</span>
      <button
        type="button"
        data-testid="speed-faster"
        aria-label={$_("dock.faster")}
        on:click={faster}>+</button
      >
      <span class="sx-caption sx-year">{yearCaption}</span>
      <span class="sx-rule" />
      <button
        type="button"
        aria-pressed={showOrbits ? "true" : "false"}
        on:click={() => (showOrbits = !showOrbits)}>{$_("dock.orbits")}</button
      >
      <button
        type="button"
        aria-pressed={showLabels ? "true" : "false"}
        on:click={() => (showLabels = !showLabels)}>{$_("dock.labels")}</button
      >
      <button
        type="button"
        data-testid="scale-toggle"
        aria-pressed={scale === "true" ? "true" : "false"}
        on:click={toggleScale}
      >
        {scale === "true" ? $_("dock.trueScale") : $_("dock.showcase")}
      </button>
      <button type="button" data-testid="view-local" on:click={showEarthMoon}
        >{$_("dock.local")}</button
      >
      <span class="sx-rule" />
      <button
        type="button"
        data-testid="view-inner"
        on:click={() => orrery?.frame("inner")}>{$_("dock.inner")}</button
      >
      <button
        type="button"
        data-testid="view-system"
        on:click={() => orrery?.frame("system")}>{$_("dock.system")}</button
      >
      <p class="sx-scale-hint" data-testid="scale-hint">
        {scale === "true" ? $_("dock.physicalHint") : $_("dock.showcaseHint")}
      </p>
    </div>
  {/key}
</div>
