import { expect, test } from "@playwright/test";

test.describe("Armónicos φ — embedded in La Rueda, reorders with the live tonic", () => {
  test("the chart's note order starts at the current tonic and reorders when the wheel spins", async ({
    page,
  }) => {
    await page.goto("/");

    const panel = page.locator(".harmonics-panel");
    await expect(panel).toBeVisible();

    async function noteLabels(): Promise<string[]> {
      return page.evaluate(() =>
        Array.from(document.querySelectorAll(".harmonics-notelabel")).map((el) => el.textContent ?? ""),
      );
    }

    const wheel = page.locator("#wheel");
    await wheel.focus();
    await wheel.press("Home");
    await expect(page.locator(".harmonics-header")).toContainText("A");
    expect(await noteLabels()).toEqual(["A", "A#", "B", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#"]);

    for (let i = 0; i < 5; i += 1) {
      await wheel.press("ArrowRight");
    }
    await expect(page.locator(".harmonics-header")).toContainText("D");
    expect(await noteLabels()).toEqual(["D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B", "C", "C#"]);
  });
});
