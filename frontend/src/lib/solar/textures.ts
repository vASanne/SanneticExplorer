/**
 * Texture demand for the orrery.
 *
 * Cold load fetches only the small previews, so the scene can paint while the
 * multi-megabyte maps stay on disk. A full map, including normals and roughness,
 * is requested for the focused body and for bodies that already cover enough
 * pixels that the preview would look soft. Starfield detail waits until the
 * previews have settled so it does not compete with the first paint.
 *
 * Failures keep the previous image (solid color, then preview). A newer focus
 * aborts an in-flight full map so a slow 8K download cannot stall the next body.
 */

import { CATALOG, MOON, SUN } from "./catalog";

export type TextureRole =
  | "color"
  | "clouds"
  | "night"
  | "normal"
  | "roughness"
  | "ring"
  | "starfield";

export type TextureTier = "preview" | "full";

export interface TextureJob {
  id: string;
  body: string;
  role: TextureRole;
  fullUrl: string;
  previewUrl: string | null;
  colorSpace: "srgb" | "none";
}

export interface TextureRequest {
  id: string;
  body: string;
  tier: TextureTier;
  url: string;
}

/** A body this many pixels across is worth its full map. */
export const FULL_RES_PIXELS = 56;

export function textureJobId(body: string, role: TextureRole): string {
  return `${body}:${role}`;
}

/** Detail maps stay full-resolution only. Color stand-ins live under preview/. */
export function previewUrlFor(fullUrl: string): string | null {
  const file = fullUrl.split("?")[0]?.split("/").pop() ?? "";
  if (!file || /normal|roughness/i.test(file)) return null;
  return `/textures/preview/${file}`;
}

function job(
  body: string,
  role: TextureRole,
  fullUrl: string,
  colorSpace: "srgb" | "none"
): TextureJob {
  return {
    id: textureJobId(body, role),
    body,
    role,
    fullUrl,
    previewUrl: previewUrlFor(fullUrl),
    colorSpace,
  };
}

export function orreryTextureJobs(): TextureJob[] {
  const jobs: TextureJob[] = [
    job("Sun", "color", SUN.texture, "srgb"),
    job("starfield", "starfield", SUN.starfield, "srgb"),
    job("Moon", "color", MOON.texture, "srgb"),
  ];
  if (MOON.normal) jobs.push(job("Moon", "normal", MOON.normal, "none"));
  for (const body of CATALOG) {
    jobs.push(job(body.name, "color", body.texture, "srgb"));
    if (body.clouds) jobs.push(job(body.name, "clouds", body.clouds, "none"));
    if (body.night) jobs.push(job(body.name, "night", body.night, "srgb"));
    if (body.normal) jobs.push(job(body.name, "normal", body.normal, "none"));
    if (body.roughnessMap) {
      jobs.push(job(body.name, "roughness", body.roughnessMap, "none"));
    }
    if (body.ringTexture) {
      jobs.push(job(body.name, "ring", body.ringTexture, "srgb"));
    }
  }
  return jobs;
}

/** Vertical pixel size of a sphere. Distance is from the camera to the body. */
export function apparentPixels(
  radius: number,
  distance: number,
  viewportHeight: number,
  fovDegrees: number
): number {
  if (radius <= 0 || distance <= 0 || viewportHeight <= 0 || fovDegrees <= 0) {
    return 0;
  }
  const worldPerPixel =
    (2 * Math.tan((fovDegrees * Math.PI) / 360) * distance) / viewportHeight;
  return (radius * 2) / worldPerPixel;
}

export interface TextureDemandHooks {
  load: (url: string, signal: AbortSignal) => Promise<unknown>;
  apply: (job: TextureJob, tier: TextureTier, image: unknown) => void;
  previewSlots?: number;
  fullSlots?: number;
}

interface Flight {
  tier: TextureTier;
  abort: AbortController;
  gen: number;
}

/**
 * Fetch a map without handing decode to the main thread.
 * colorSpaceConversion "none" leaves the file's encoded samples alone so
 * THREE.SRGBColorSpace matches the previous TextureLoader path.
 */
export async function loadTextureSource(
  url: string,
  signal: AbortSignal
): Promise<ImageBitmap | HTMLImageElement> {
  const response = await fetch(url, { signal, credentials: "same-origin" });
  if (!response.ok) throw new Error(`${response.status} ${url}`);
  const blob = await response.blob();
  if (typeof createImageBitmap === "function") {
    return createImageBitmap(blob, {
      imageOrientation: "none",
      premultiplyAlpha: "none",
      colorSpaceConversion: "none",
    });
  }
  const objectUrl = URL.createObjectURL(blob);
  try {
    return await new Promise<HTMLImageElement>((resolve, reject) => {
      const image = new Image();
      image.onload = () => resolve(image);
      image.onerror = () => reject(new Error(`decode ${url}`));
      image.src = objectUrl;
    });
  } finally {
    URL.revokeObjectURL(objectUrl);
  }
}

function closeImage(image: unknown) {
  if (
    image &&
    typeof image === "object" &&
    "close" in image &&
    typeof (image as { close?: unknown }).close === "function"
  ) {
    (image as { close: () => void }).close();
  }
}

export class TextureDemand {
  private jobs: Map<string, TextureJob>;
  private wanted = new Map<string, TextureTier>();
  private applied = new Map<string, TextureTier>();
  private generation = new Map<string, number>();
  private inflight = new Map<string, Flight>();
  private failed = new Set<string>();
  private queue: TextureRequest[] = [];
  private activePreview = 0;
  private activeFull = 0;
  private disposed = false;
  private focused: string | null = null;
  private readonly previewSlots: number;
  private readonly fullSlots: number;

  constructor(jobs: TextureJob[], private hooks: TextureDemandHooks) {
    this.jobs = new Map(jobs.map((entry) => [entry.id, entry]));
    this.previewSlots = hooks.previewSlots ?? 4;
    this.fullSlots = hooks.fullSlots ?? 1;
  }

  update(focused: string | null, visible: string[]) {
    if (this.disposed) return;
    this.focused = focused;
    const next = new Map<string, TextureTier>();
    for (const entry of this.jobs.values()) {
      if (entry.previewUrl) next.set(entry.id, "preview");
    }
    const detailed = new Set(visible.filter((name) => name !== "starfield"));
    if (focused && focused !== "starfield") detailed.add(focused);
    for (const body of detailed) {
      for (const entry of this.jobs.values()) {
        if (entry.body === body) next.set(entry.id, "full");
      }
    }
    if (visible.includes("starfield") && this.previewsSettled()) {
      for (const entry of this.jobs.values()) {
        if (entry.body === "starfield") next.set(entry.id, "full");
      }
    }
    for (const [id, flight] of this.inflight) {
      if (flight.tier === "full" && next.get(id) !== "full") {
        this.generation.set(id, flight.gen + 1);
        flight.abort.abort();
        this.inflight.delete(id);
        this.activeFull = Math.max(0, this.activeFull - 1);
      }
    }
    this.wanted = next;
    this.syncQueue();
    this.pump();
  }

  dispose() {
    this.disposed = true;
    this.queue = [];
    for (const flight of this.inflight.values()) flight.abort.abort();
  }

  debug() {
    return {
      applied: [...this.applied.entries()],
      queued: this.queue.map((entry) => entry.url),
      inflight: [...this.inflight.keys()],
      failed: [...this.failed],
    };
  }

  private previewsSettled() {
    for (const entry of this.jobs.values()) {
      if (!entry.previewUrl) continue;
      if (this.applied.has(entry.id)) continue;
      if (this.failed.has(`${entry.id}:preview`)) continue;
      return false;
    }
    return true;
  }

  private syncQueue() {
    const queued = new Set(
      this.queue.map((entry) => `${entry.id}:${entry.tier}`)
    );
    for (const [id, tier] of this.wanted) {
      const entry = this.jobs.get(id);
      if (!entry) continue;
      const applied = this.applied.get(id);
      if (applied === "full") continue;
      if (applied === tier) continue;
      if (this.failed.has(`${id}:${tier}`)) continue;
      const url = tier === "preview" ? entry.previewUrl : entry.fullUrl;
      if (!url) continue;
      if (tier === "full" && !applied && entry.previewUrl) {
        this.enqueue(entry, "preview", entry.previewUrl, queued);
      }
      this.enqueue(entry, tier, url, queued);
    }
    this.queue = this.queue.filter((entry) => {
      const want = this.wanted.get(entry.id);
      if (!want) return false;
      if (entry.tier === "full") return want === "full";
      return this.applied.get(entry.id) == null;
    });
  }

  private enqueue(
    entry: TextureJob,
    tier: TextureTier,
    url: string,
    queued: Set<string>
  ) {
    const key = `${entry.id}:${tier}`;
    if (queued.has(key)) return;
    if (this.inflight.get(entry.id)?.tier === tier) return;
    if (this.failed.has(key)) return;
    const applied = this.applied.get(entry.id);
    if (applied === "full" || applied === tier) return;
    this.queue.push({ id: entry.id, body: entry.body, tier, url });
    queued.add(key);
  }

  private score(entry: TextureRequest) {
    if (entry.tier === "full" && entry.body === this.focused) return 0;
    if (entry.tier === "full" && entry.body !== "starfield") return 1;
    if (entry.tier === "preview") return 2;
    return 3;
  }

  private pick() {
    const ranked = [...this.queue].sort(
      (a, b) => this.score(a) - this.score(b)
    );
    for (const entry of ranked) {
      if (this.inflight.has(entry.id)) continue;
      if (entry.tier === "preview" && this.activePreview >= this.previewSlots) {
        continue;
      }
      if (entry.tier === "full" && this.activeFull >= this.fullSlots) continue;
      if (entry.tier === "full" && entry.body === "starfield") {
        const previewsOpen =
          this.activePreview > 0 ||
          this.queue.some((item) => item.tier === "preview");
        if (previewsOpen) continue;
      }
      return entry;
    }
    return null;
  }

  private pump() {
    if (this.disposed) return;
    let next = this.pick();
    while (next) {
      const chosen = next;
      this.queue = this.queue.filter((entry) => entry !== chosen);
      this.start(chosen);
      next = this.pick();
    }
  }

  private start(entry: TextureRequest) {
    const gen = this.generation.get(entry.id) ?? 0;
    const abort = new AbortController();
    this.inflight.set(entry.id, { tier: entry.tier, abort, gen });
    if (entry.tier === "full") this.activeFull += 1;
    else this.activePreview += 1;
    const aborted = new Promise<never>((_, reject) => {
      if (abort.signal.aborted) {
        reject(new DOMException("aborted", "AbortError"));
        return;
      }
      abort.signal.addEventListener(
        "abort",
        () => reject(new DOMException("aborted", "AbortError")),
        { once: true }
      );
    });
    Promise.race([this.hooks.load(entry.url, abort.signal), aborted]).then(
      (image) => this.settle(entry, gen, image, null),
      (error: unknown) => this.settle(entry, gen, null, error)
    );
  }

  private settle(
    entry: TextureRequest,
    gen: number,
    image: unknown,
    error: unknown
  ) {
    const flight = this.inflight.get(entry.id);
    const owns = Boolean(
      flight && flight.gen === gen && flight.tier === entry.tier
    );
    if (owns) {
      this.inflight.delete(entry.id);
      if (entry.tier === "full")
        this.activeFull = Math.max(0, this.activeFull - 1);
      else this.activePreview = Math.max(0, this.activePreview - 1);
    }
    const stale =
      this.disposed ||
      (this.generation.get(entry.id) ?? 0) !== gen ||
      Boolean(flight && flight.abort.signal.aborted && error);
    if (stale) {
      closeImage(image);
      this.pump();
      return;
    }
    if (error || image == null) {
      this.failed.add(`${entry.id}:${entry.tier}`);
      this.pump();
      return;
    }
    if (entry.tier === "full" && this.wanted.get(entry.id) !== "full") {
      closeImage(image);
      this.pump();
      return;
    }
    if (this.applied.get(entry.id) === "full" && entry.tier === "preview") {
      closeImage(image);
      this.pump();
      return;
    }
    this.applied.set(entry.id, entry.tier);
    const textureJob = this.jobs.get(entry.id);
    if (textureJob) this.hooks.apply(textureJob, entry.tier, image);
    this.syncQueue();
    this.pump();
  }
}
