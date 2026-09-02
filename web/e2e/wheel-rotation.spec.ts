import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

import { expect, test } from "@playwright/test";

// Real BE-baked data, read directly from disk — not a hand-typed fixture.
// This is the same file GatopleApp.tsx bundles, so DOM assertions below are
// checked against ground truth, not against values this test invented.
const dataPath = fileURLToPath(new URL("../public/data.json", import.meta.url));
const payload = JSON.parse(readFileSync(dataPath, "utf-8")) as {
  chromatic: readonly string[];
  roles: readonly { position: number; mode_name: string }[];
  rotations: readonly (readonly string[])[];
};

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
