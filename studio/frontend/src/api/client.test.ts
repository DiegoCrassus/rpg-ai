import { afterEach, describe, expect, it, vi } from "vitest";

import { studioApiBase } from "./client";

describe("studioApiBase", () => {
  afterEach(() => {
    vi.unstubAllEnvs();
  });

  it("defaults to proxied /studio path", () => {
    vi.stubEnv("VITE_STUDIO_API_URL", "");
    expect(studioApiBase()).toBe("/studio");
  });

  it("prefixes configured API host with /studio", () => {
    vi.stubEnv("VITE_STUDIO_API_URL", "http://127.0.0.1:8100");
    expect(studioApiBase()).toBe("http://127.0.0.1:8100/studio");
  });

  it("strips trailing slash from configured host", () => {
    vi.stubEnv("VITE_STUDIO_API_URL", "http://127.0.0.1:8100/");
    expect(studioApiBase()).toBe("http://127.0.0.1:8100/studio");
  });
});
