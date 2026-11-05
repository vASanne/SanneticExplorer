import { cleanup, render, screen, within } from "@testing-library/svelte";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
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
  });

  it("shows the eight planets when the API returns nothing", async () => {
    render(Showcase, { props: { planets: [], error: "down" } });
    expect(screen.getByText("Reference catalog")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Neptune" })).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: "Play orbit animation" })
    ).toBeInTheDocument();
  });

  it("shows the simulation date, reverse speeds, and the scale toggle", async () => {
    render(Showcase, { props: { planets: [], error: null } });
    expect(screen.getByTestId("sim-date")).toBeInTheDocument();
    expect(screen.getByTestId("today")).toHaveTextContent("Today");
    expect(screen.getByTestId("speed-readout")).toHaveTextContent("1×");
    await screen.getByTestId("speed-slower").click();
    expect(screen.getByTestId("speed-readout")).toHaveTextContent("−1×");
    await screen.getByTestId("today").click();
    expect(screen.getByTestId("scale-toggle")).toHaveTextContent("Showcase");
    await screen.getByTestId("scale-toggle").click();
    expect(screen.getByTestId("scale-toggle")).toHaveTextContent("True scale");
    expect(screen.getByRole("button", { name: "Moon" })).toBeInTheDocument();
  });

  it("opens live planet facts from the rail", async () => {
    render(Showcase, { props: { planets: [earth], error: null } });
    within(screen.getByTestId("body-rail"))
      .getByRole("button", { name: "Earth" })
      .click();
    expect(await screen.findByTestId("info-panel")).toHaveTextContent(
      "Live /planets"
    );
    expect(screen.getByTestId("info-panel")).toHaveTextContent("1.000 AU");
  });
});
