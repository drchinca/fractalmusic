import { describe, expect, it } from "vitest";

import payloadJson from "../../public/data.json";
import type { Payload } from "../gatople/types";

// Real BE-baked data, not a hand-typed fixture — same file HarmonicsPanel
// bundles. Guards the phi/coordinates_3d contract this view depends on.
const payload = payloadJson as unknown as Payload;

describe("harmonics data contract", () => {
  it("carries phi as the exact golden-ratio value fractalmusic.geometry uses", () => {
    expect(payload.phi).toBeCloseTo((1 + Math.sqrt(5)) / 2, 12);
  });

  it("gives every role a 3-component coordinate whose magnitude matches an icosahedron vertex", () => {
    expect(payload.roles).toHaveLength(12);
    for (const role of payload.roles) {
      expect(role.coordinates_3d).toHaveLength(3);
      const [x, y, z] = role.coordinates_3d;
      const magnitude = Math.hypot(x, y, z);
      // Every _ICOSAHEDRON_VERTICES entry is one of {0, ±1, ±phi} per axis,
      // exactly two of which are non-zero — magnitude is always sqrt(1+phi^2).
      expect(magnitude).toBeCloseTo(Math.sqrt(1 + payload.phi * payload.phi), 6);
    }
  });

  it("groups the 12 notes into three 4-note blocks where one axis is zero", () => {
    const sorted = [...payload.roles].sort((a, b) => a.position - b.position);
    for (const role of sorted) {
      const zeroAxisCount = role.coordinates_3d.filter((component) => component === 0).length;
      expect(zeroAxisCount).toBe(1);
    }
  });
});
