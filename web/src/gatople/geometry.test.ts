import { describe, expect, it } from "vitest";

import payloadJson from "../../public/data.json";
import {
  arcPath,
  clockAngle,
  displayNote,
  indexOfNote,
  noteAtRolePosition,
  polar,
  roleAtNote,
} from "./geometry";
import type { Payload } from "./types";

// Real BE-baked data, not a hand-typed fixture — the same file GatopleApp
// imports. If scripts/build_gatople_data.py's shape ever changes, this
// breaks here first instead of silently in the browser.
const payload = payloadJson as unknown as Payload;

describe("polar", () => {
  it("places 0 degrees straight up (SVG y grows downward)", () => {
    const [x, y] = polar(0, 100);
    expect(x).toBeCloseTo(0);
    expect(y).toBeCloseTo(-100);
  });

  it("places 90 degrees to the right", () => {
    const [x, y] = polar(90, 100);
    expect(x).toBeCloseTo(100);
    expect(y).toBeCloseTo(0);
  });
});

describe("clockAngle", () => {
  it("maps clock hour to 30 degrees per hour", () => {
    expect(clockAngle(0)).toBe(0);
    expect(clockAngle(3)).toBe(90);
    expect(clockAngle(12)).toBe(0); // 12 % 12 === 0
  });
});

describe("arcPath", () => {
  it("uses the small-arc flag for spans under 180 degrees", () => {
    const path = arcPath(0, 30, 100, 50);
    expect(path).toContain("A 100 100 0 0 1");
  });

  it("uses the large-arc flag for spans over 180 degrees", () => {
    const path = arcPath(0, 200, 100, 50);
    expect(path).toContain("A 100 100 0 1 1");
  });
});

describe("indexOfNote", () => {
  it("finds a note's position in the chromatic ring", () => {
    expect(indexOfNote("A", payload.chromatic)).toBe(0);
    expect(indexOfNote("G#", payload.chromatic)).toBe(11);
  });

  it("returns -1 for a note not in the ring", () => {
    expect(indexOfNote("H", payload.chromatic)).toBe(-1);
  });
});

describe("displayNote", () => {
  it("appends the flat spelling for black keys", () => {
    expect(displayNote("A#", payload.enharmonic)).toBe("A#/Bb");
  });

  it("leaves naturals unchanged", () => {
    expect(displayNote("A", payload.enharmonic)).toBe("A");
  });
});

describe("noteAtRolePosition + roleAtNote (real baked rotations)", () => {
  it("round-trips: the note at a role's position, spun back to the same role", () => {
    // At every tonic, for every role position, looking up its note and then
    // looking up that note's role must return the same role we started with.
    for (let tonicOffset = 0; tonicOffset < 12; tonicOffset += 1) {
      for (const role of payload.roles) {
        const note = noteAtRolePosition(role.position, tonicOffset, payload.rotations);
        const found = roleAtNote(note, payload.roles, tonicOffset, payload.rotations);
        expect(found?.position).toBe(role.position);
      }
    }
  });

  it("matches the book-canonical A-tonic default (rotations[0] is the identity)", () => {
    expect(payload.rotations[0]).toEqual(payload.chromatic);
  });

  it("spinning to F puts C at the Frigio role (book-verified example)", () => {
    const fOffset = indexOfNote("F", payload.chromatic);
    const frigioRole = payload.roles.find((r) => r.mode_name === "Frigio");
    expect(frigioRole).toBeDefined();
    const note = noteAtRolePosition(frigioRole!.position, fOffset, payload.rotations);
    expect(note).toBe("C");
  });
});
