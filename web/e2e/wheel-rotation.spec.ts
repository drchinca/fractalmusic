import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

import { expect, test } from "@playwright/test";

// Real BE-baked data, read directly from disk — not a hand-typed fixture.
// This is the same file GatopleApp.tsx bundles, so DOM assertions below are
// checked against ground truth, not against values this test invented.
const dataPath = fileURLToPath(new URL("../public/data.json", import.meta.url));
const payload = JSON.parse(readFileSync(dataPath, "utf-8")) as {
  chromatic: readonly string[];
  roles: readonly { position: number; mode_name: string; clock_hour: number }[];
  rotations: readonly (readonly string[])[];
};

const SEG_DEG = 30;
const NOTE_RADIUS = 130;

function clockAngle(hour: number): number {
  return (hour % 12) * SEG_DEG;
}

function polar(deg: number, radius: number): readonly [number, number] {
  const rad = ((deg - 90) * Math.PI) / 180;
  return [radius * Math.cos(rad), radius * Math.sin(rad)];
}

const frigioRole = payload.roles.find((r) => r.mode_name === "Frigio");
if (!frigioRole) throw new Error("Frigio role not found in baked payload");

test.describe("Gátople wheel — real rotation against BE-baked data", () => {
  test("spinning the wheel updates the tonic readout and every role binding to match rotations[]", async ({
    page,
  }) => {
    await page.goto("/");

    const wheel = page.locator("#wheel");
    await expect(wheel).toBeVisible();

    // Reset to the known A-tonic default.
    await wheel.focus();
    await wheel.press("Home");
    await expect(wheel).toHaveAttribute("aria-valuenow", "0");
    await expect(page.locator(".tonic-readout strong")).toHaveText("A");

    // Spin 5 semitones forward (A -> D).
    for (let i = 0; i < 5; i += 1) {
      await wheel.press("ArrowRight");
    }
    await expect(wheel).toHaveAttribute("aria-valuenow", "5");
    await expect(page.locator(".tonic-readout strong")).toHaveText(payload.chromatic[5]);

    // The bindings table's Frigio row must show exactly what
    // scripts/build_gatople_data.py baked for tonicOffset=5.
    const expectedFrigioNote = payload.rotations[5][frigioRole.position];
    const bindingsRows = page.locator("#bindings tbody tr");
    const rowCount = await bindingsRows.count();
    let matched = false;
    for (let i = 0; i < rowCount; i += 1) {
      const row = bindingsRows.nth(i);
      const noteCell = row.locator("td").nth(2);
      const text = await noteCell.textContent();
      if (text?.startsWith(expectedFrigioNote)) {
        matched = true;
      }
    }
    expect(matched).toBe(true);

    // Piano and fretboard must re-render without throwing (they consume the
    // same rotations table) — a crash here would blank the whole section.
    await expect(page.locator("#piano")).toBeVisible();
    await expect(page.locator("#fretboard")).toBeVisible();
  });

  test("every note-item's actual SVG position matches rotations[] at every tonic offset", async ({
    page,
  }) => {
    // The outer disc is a circle-of-fourths clock (fractalmusic.modes._clock_hour):
    // each physical hour-step is a perfect fourth (5 semitones), not a semitone.
    // A rendering bug once made the inner disc rotate 1 hour per semitone instead —
    // that coincidentally cancels out only at tonic offsets 0, 3, 6, 9 (multiples of
    // 3), so a text-only assertion at one offset was never enough to catch it. This
    // reads the real SVG transform and checks every role's slot at every offset.
    await page.goto("/");
    const wheel = page.locator("#wheel");
    await wheel.focus();

    for (let offset = 0; offset < 12; offset += 1) {
      await wheel.press("Home");
      for (let i = 0; i < offset; i += 1) {
        await wheel.press("ArrowRight");
      }
      await expect(wheel).toHaveAttribute("aria-valuenow", String(offset));

      const items = await page.evaluate(() => {
        const inner = document.getElementById("inner-disc");
        const match = (inner?.getAttribute("transform") ?? "").match(/rotate\(([-0-9.eE]+)\)/);
        const groupDeg = match ? Number.parseFloat(match[1]) : 0;
        const rad = (groupDeg * Math.PI) / 180;
        const cos = Math.cos(rad);
        const sin = Math.sin(rad);
        return Array.from(document.querySelectorAll(".note-item")).map((item) => {
          const raw = item.getAttribute("transform") ?? "";
          const local = raw.match(/translate\(([-0-9.eE]+)[, ]+([-0-9.eE]+)\)/);
          const lx = local ? Number.parseFloat(local[1]) : 0;
          const ly = local ? Number.parseFloat(local[2]) : 0;
          const text = item.querySelector("text")?.textContent ?? "";
          return { note: text.split("/")[0], x: lx * cos - ly * sin, y: lx * sin + ly * cos };
        });
      });

      for (const role of payload.roles) {
        const [slotX, slotY] = polar(clockAngle(role.clock_hour), NOTE_RADIUS);
        let closest = items[0];
        let closestDist = Number.POSITIVE_INFINITY;
        for (const item of items) {
          const dist = Math.hypot(item.x - slotX, item.y - slotY);
          if (dist < closestDist) {
            closestDist = dist;
            closest = item;
          }
        }
        const expected = payload.rotations[offset][role.position];
        expect(
          closest.note,
          `offset=${offset} role=${role.mode_name} hour=${role.clock_hour}`,
        ).toBe(expected);
        expect(closestDist).toBeLessThan(1);
      }
    }
  });

  test("Home key returns the wheel to the A-tonic default from any rotation", async ({ page }) => {
    await page.goto("/");
    const wheel = page.locator("#wheel");
    await wheel.focus();

    for (let i = 0; i < 7; i += 1) {
      await wheel.press("ArrowRight");
    }
    await expect(wheel).not.toHaveAttribute("aria-valuenow", "0");

    await wheel.press("Home");
    await expect(wheel).toHaveAttribute("aria-valuenow", "0");
    await expect(page.locator(".tonic-readout strong")).toHaveText("A");
  });
});
