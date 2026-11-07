import { cleanup, render, screen, within } from "@testing-library/svelte";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { locale } from "svelte-i18n";
import type { PlanetData } from "$lib/api";
import Showcase from "./Showcase.svelte";

vi.mock("$lib/solar/Orrery", () => {
  class Orrery {
    setPlanets = vi.fn();
    setPlaying = vi.fn();
    setSpeed = vi.fn();
    setOrbitsVisible = vi.fn();
    setLabelsVisible = vi.fn();
    setSelected = vi.fn();
    setScale = vi.fn();
    setJulianDay = vi.fn();
    focus = vi.fn();
    frame = vi.fn();
    resize = vi.fn();
    dispose = vi.fn();
  }
  return { Orrery };
});

vi.mock("$lib/api", () => ({
  getPlanets: vi.fn(async () => []),
  browserApiBase: () => "http://localhost:13800",
}));

const earth: PlanetData = {
  id: "earth",
  name: "Earth",
  type: "planet",
  subtype: "terrestrial planet",
  data_quality: "good",
  radius_km: 6371,
  mean_distance_au: 1,
  orbital_period_days: 365.25,
  mass_kg: 5.972e24,
  surface_gravity_ms2: 9.81,
  surface_temperature_k: 288,
  eccentricity: 0.0167,
};

describe("Showcase", () => {
  afterEach(() => cleanup());

  beforeEach(() => {
    vi.clearAllMocks();
    locale.set("de");
  });

  it("shows the eight planets when the API returns nothing", async () => {
    render(Showcase, { props: { planets: [], error: "down" } });
    expect(screen.getByText("Referenzkatalog")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Neptun" })).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: "Umlaufbahn abspielen" })
    ).toBeInTheDocument();
    expect(screen.getByTitle("Anfrage fehlgeschlagen")).toBeInTheDocument();
  });

  it("shows the simulation date, reverse speeds, and the scale toggle", async () => {
    render(Showcase, { props: { planets: [], error: null } });
    expect(screen.getByTestId("sim-date")).toBeInTheDocument();
    expect(screen.getByTestId("today")).toHaveTextContent("Heute");
    expect(screen.getByTestId("speed-readout")).toHaveTextContent(
      "1 Erdjahr / 3 Min."
    );
    expect(screen.getByTestId("play-toggle")).toHaveTextContent("Start");
    await screen.getByTestId("speed-slower").click();
    expect(screen.getByTestId("speed-readout")).toHaveTextContent("rückwärts");
    await screen.getByTestId("today").click();
    expect(screen.getByTestId("scale-toggle")).toHaveTextContent("Echtmaß");
    expect(screen.getByTestId("scale-hint")).toHaveTextContent("einer Einheit");
    expect(screen.getByTestId("view-local")).toHaveTextContent("Erde–Mond");
    await screen.getByTestId("scale-toggle").click();
    expect(screen.getByTestId("scale-toggle")).toHaveTextContent("Schaustück");
    expect(screen.getByTestId("scale-hint")).toHaveTextContent(
      "keine echte Geometrie"
    );
    await screen.getByRole("button", { name: "Mond" }).click();
    expect(screen.getByTestId("scale-toggle")).toHaveTextContent("Echtmaß");
  });

  it("opens live planet facts from the rail", async () => {
    render(Showcase, { props: { planets: [earth], error: null } });
    within(screen.getByTestId("body-rail"))
      .getByRole("button", { name: "Erde" })
      .click();
    expect(await screen.findByTestId("info-panel")).toHaveTextContent(
      "Live-API"
    );
    expect(screen.getByTestId("info-panel")).toHaveTextContent("1,000 AE");
    expect(screen.getByTestId("info-panel")).toHaveTextContent(
      "Gesteinsplanet"
    );
  });

  it("switches the dock and body names to English", async () => {
    render(Showcase, { props: { planets: [], error: null } });
    await screen.getByTestId("locale-en").click();
    expect(screen.getByTestId("scale-toggle")).toHaveTextContent("True scale");
    expect(screen.getByTestId("view-local")).toHaveTextContent("Earth–Moon");
    expect(screen.getByTestId("speed-readout")).toHaveTextContent(
      "1 Earth year / 3 min."
    );
    expect(screen.getByTestId("today")).toHaveTextContent("Today");
    expect(screen.getByRole("button", { name: "Earth" })).toBeInTheDocument();
    expect(screen.getByText("Reference catalog")).toBeInTheDocument();
  });
});
