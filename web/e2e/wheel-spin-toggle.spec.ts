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
