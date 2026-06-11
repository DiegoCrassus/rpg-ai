import { describe, expect, it } from "vitest";

import {
  DEFAULT_VALIDATION_VISIBILITY,
  isValidationBorderVisible,
  toggleValidationVisibility,
} from "./validationVisibility";

describe("toggleValidationVisibility", () => {
  it("toggles a single status off and on", () => {
    const off = toggleValidationVisibility(DEFAULT_VALIDATION_VISIBILITY, "fail");
    expect(off.fail).toBe(false);
    expect(off.pass).toBe(true);

    const on = toggleValidationVisibility(off, "fail");
    expect(on.fail).toBe(true);
  });
});

describe("isValidationBorderVisible", () => {
  it("returns true when status is enabled", () => {
    expect(isValidationBorderVisible("warn", DEFAULT_VALIDATION_VISIBILITY)).toBe(true);
  });

  it("returns false when status is disabled in legend", () => {
    const visibility = toggleValidationVisibility(DEFAULT_VALIDATION_VISIBILITY, "pass");
    expect(isValidationBorderVisible("pass", visibility)).toBe(false);
    expect(isValidationBorderVisible("fail", visibility)).toBe(true);
  });
});
