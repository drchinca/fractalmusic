import { describe, expect, it } from "vitest";

import { runIdFromAudioUrl } from "./auditApi";

describe("runIdFromAudioUrl", () => {
  it("extracts the cache key from a real audio_url shape", () => {
    expect(runIdFromAudioUrl("/audio-cache/a1b2c3d4.wav")).toBe("a1b2c3d4");
  });

  it("works with a full origin URL", () => {
    expect(runIdFromAudioUrl("http://localhost:8002/audio-cache/deadbeef.wav")).toBe("deadbeef");
  });

  it("returns null when the URL doesn't end in .wav", () => {
    expect(runIdFromAudioUrl("/audio-cache/deadbeef.mp3")).toBeNull();
  });
});
