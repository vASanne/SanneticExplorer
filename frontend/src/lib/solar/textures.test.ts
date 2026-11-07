import { statSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";
import {
  FULL_RES_PIXELS,
  TextureDemand,
  apparentPixels,
  orreryTextureJobs,
  previewUrlFor,
  type TextureJob,
  type TextureTier,
} from "./textures";

const previewDir = resolve(
  dirname(fileURLToPath(import.meta.url)),
  "../../../static/textures/preview"
);

function deferred() {
  let resolvePromise: (value: unknown) => void = () => {};
  let rejectPromise: (error: unknown) => void = () => {};
  const promise = new Promise((resolve, reject) => {
    resolvePromise = resolve;
    rejectPromise = reject;
  });
  return { promise, resolve: resolvePromise, reject: rejectPromise };
}

describe("texture demand", () => {
  it("keeps the cold set to small previews", () => {
    const jobs = orreryTextureJobs();
    const previews = jobs
      .map((entry) => entry.previewUrl)
      .filter((url): url is string => Boolean(url));
    expect(previews.length).toBeGreaterThan(10);
    expect(previews.every((url) => url.startsWith("/textures/preview/"))).toBe(
      true
    );
    const full = jobs.map((entry) => entry.fullUrl);
    expect(full).toContain("/textures/earth_normal.png");
    expect(full).toContain("/textures/mercury.jpg");
    expect(previews).not.toContain("/textures/earth_normal.png");
    expect(previewUrlFor("/textures/earth_normal.png")).toBeNull();
    expect(previewUrlFor("/textures/moon.jpg")).toBe(
      "/textures/preview/moon.jpg"
    );
    let bytes = 0;
    for (const url of previews) {
      const file = url.split("/").pop() ?? "";
      bytes += statSync(resolve(previewDir, file)).size;
    }
    expect(bytes).toBeLessThan(500_000);
    expect(bytes).toBeGreaterThan(50_000);
  });

  it("asks for a full map only once a body is large or focused", () => {
    const far = apparentPixels(0.002, 120, 800, 48);
    const near = apparentPixels(0.7, 8, 800, 48);
    expect(far).toBeLessThan(FULL_RES_PIXELS);
    expect(near).toBeGreaterThan(FULL_RES_PIXELS);
    expect(apparentPixels(0, 10, 800, 48)).toBe(0);
  });

  it("applies previews, then the focused body, and ignores a stale full map", async () => {
    const jobs: TextureJob[] = [
      {
        id: "Sun:color",
        body: "Sun",
        role: "color",
        fullUrl: "/textures/sun.jpg",
        previewUrl: "/textures/preview/sun.jpg",
        colorSpace: "srgb",
      },
      {
        id: "Earth:color",
        body: "Earth",
        role: "color",
        fullUrl: "/textures/earth_day.jpg",
        previewUrl: "/textures/preview/earth_day.jpg",
        colorSpace: "srgb",
      },
      {
        id: "Earth:normal",
        body: "Earth",
        role: "normal",
        fullUrl: "/textures/earth_normal.png",
        previewUrl: null,
        colorSpace: "none",
      },
      {
        id: "Mars:color",
        body: "Mars",
        role: "color",
        fullUrl: "/textures/mars.jpg",
        previewUrl: "/textures/preview/mars.jpg",
        colorSpace: "srgb",
      },
      {
        id: "starfield:starfield",
        body: "starfield",
        role: "starfield",
        fullUrl: "/textures/stars.jpg",
        previewUrl: "/textures/preview/stars.jpg",
        colorSpace: "srgb",
      },
    ];
    const loads = new Map<
      string,
      ReturnType<typeof deferred> & { signal: AbortSignal }
    >();
    const applied: Array<{ id: string; tier: TextureTier }> = [];
    const demand = new TextureDemand(jobs, {
      previewSlots: 4,
      fullSlots: 1,
      load: (url, signal) => {
        const pending = deferred();
        loads.set(url, { ...pending, signal });
        return pending.promise;
      },
      apply: (job: TextureJob, tier) => applied.push({ id: job.id, tier }),
    });

    demand.update(null, []);
    expect([...loads.keys()].every((url) => url.includes("/preview/"))).toBe(
      true
    );
    expect(loads.has("/textures/earth_normal.png")).toBe(false);
    for (const [url, pending] of loads) pending.resolve(url);
    await flush();
    expect(applied.filter((entry) => entry.tier === "preview")).toHaveLength(4);

    demand.update("Earth", ["starfield"]);
    const earthFull = loads.get("/textures/earth_day.jpg");
    expect(earthFull).toBeTruthy();
    expect(loads.has("/textures/stars.jpg")).toBe(false);
    expect(loads.has("/textures/earth_normal.png")).toBe(false);

    demand.update("Mars", ["starfield"]);
    expect(earthFull?.signal.aborted).toBe(true);
    earthFull?.resolve("late-earth");
    const mars = loads.get("/textures/mars.jpg");
    expect(mars).toBeTruthy();
    mars?.resolve("mars");
    await flush();
    expect(
      applied.some(
        (entry) => entry.id === "Earth:color" && entry.tier === "full"
      )
    ).toBe(false);
    expect(applied).toContainEqual({ id: "Mars:color", tier: "full" });

    demand.update("Earth", []);
    await flush();
    const retry = loads.get("/textures/earth_day.jpg");
    expect(retry?.signal.aborted).toBe(false);
    retry?.reject(new Error("decode failed"));
    await flush();
    expect(demand.debug().failed).toContain("Earth:color:full");
    expect(applied).toContainEqual({ id: "Earth:color", tier: "preview" });
    demand.dispose();
  });

  it("keeps going when a preview fails", async () => {
    const jobs = orreryTextureJobs().filter(
      (entry) => entry.body === "Venus" || entry.body === "Sun"
    );
    const loads = new Map<string, ReturnType<typeof deferred>>();
    const applied: string[] = [];
    const demand = new TextureDemand(jobs, {
      previewSlots: 2,
      fullSlots: 1,
      load: (url) => {
        const pending = deferred();
        loads.set(url, pending);
        return pending.promise;
      },
      apply: (job) => applied.push(job.id),
    });
    demand.update(null, []);
    loads.get("/textures/preview/venus.jpg")?.reject(new Error("404"));
    loads.get("/textures/preview/sun.jpg")?.resolve("sun");
    await flush();
    expect(applied).toEqual(["Sun:color"]);
    expect(demand.debug().failed).toContain("Venus:color:preview");
    demand.dispose();
  });
});

function flush() {
  return new Promise((resolve) => setTimeout(resolve, 0));
}
