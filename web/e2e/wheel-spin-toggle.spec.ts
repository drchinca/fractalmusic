import { expect, test } from "@playwright/test";

test.describe("Wheel spin toggle — outer ring and chord overlay follow the lock state", () => {
  test("by default the outer ring and chord overlay rotate together with the notes", async ({
    page,
  }) => {
    await page.goto("/");
    const wheel = page.locator("#wheel");
    await wheel.focus();
    await wheel.press("Home");
    for (let i = 0; i < 4; i += 1) {
      await wheel.press("ArrowRight");
    }

    const [outerGroup, chordGroup] = await wheel.evaluate((svg) => {
      const groups = Array.from(svg.children).filter((el) => el.tagName === "g");
      const outer = groups[0];
      const overlay = groups[groups.length - 1];
      return [outer.getAttribute("transform"), overlay.getAttribute("transform")];
    });

    expect(outerGroup).not.toBeNull();
    expect(outerGroup).not.toBe("");
    expect(chordGroup).not.toBeNull();
  });

  test("outer-ring glyphs stay upright when the whole wheel spins together", async ({ page }) => {
    // Regression: wrapping OuterDisc in a rotation group without counter-
    // rotating each glyph turns a "+" into an "×" and a "↓" into a tick mark.
    await page.goto("/");
    const wheel = page.locator("#wheel");
    await wheel.focus();
    await wheel.press("Home");
    for (let i = 0; i < 7; i += 1) {
      await wheel.press("ArrowRight");
    }

    const outerRotation = await wheel.evaluate((svg) => {
      const groups = Array.from(svg.children).filter((el) => el.tagName === "g");
      const match = (groups[0].getAttribute("transform") ?? "").match(/rotate\(([-0-9.]+)\)/);
      return match ? Number.parseFloat(match[1]) : 0;
    });
    expect(outerRotation).not.toBe(0);

    const glyphRotations = await page.evaluate(() =>
      Array.from(document.querySelectorAll(".role-glyph")).map((el) => {
        const g = el.closest("g[transform]");
        const match = (g?.getAttribute("transform") ?? "").match(/rotate\(([-0-9.]+)\)/);
        return match ? Number.parseFloat(match[1]) : null;
      }),
    );
    expect(glyphRotations).toHaveLength(12);
    for (const glyphRotation of glyphRotations) {
      expect(glyphRotation).not.toBeNull();
      // Net rotation on the glyph (outer spin + its own counter-rotation) must
      // cancel out to a multiple of 360, or the symbol renders sideways.
      const net = ((outerRotation + (glyphRotation ?? 0)) % 360 + 360) % 360;
      expect(net).toBeLessThan(0.01);
    }
  });

  test("locking the outer ring removes rotation from the outer disc but not the notes", async ({
    page,
  }) => {
    await page.goto("/");
    const wheel = page.locator("#wheel");
    await wheel.focus();
    await wheel.press("Home");
    for (let i = 0; i < 4; i += 1) {
      await wheel.press("ArrowRight");
    }

    await page.getByRole("button", { name: "Anillo fijo" }).click();

    const outerTransform = await wheel.evaluate((svg) => {
      const groups = Array.from(svg.children).filter((el) => el.tagName === "g");
      return groups[0].getAttribute("transform");
    });
    const innerTransform = await page.locator("#inner-disc").getAttribute("transform");

    expect(outerTransform).toBeNull();
    expect(innerTransform).toMatch(/rotate\(/);
  });
});
