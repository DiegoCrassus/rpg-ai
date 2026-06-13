import { describe, expect, it } from "vitest";
import { DEFAULT_SEED_MESA_NAME, resolveSeedMesaName } from "./mesaUtils";

describe("resolveSeedMesaName", () => {
  it("uses default when name is empty", () => {
    expect(resolveSeedMesaName("")).toBe(DEFAULT_SEED_MESA_NAME);
    expect(resolveSeedMesaName("   ")).toBe(DEFAULT_SEED_MESA_NAME);
  });

  it("uses trimmed form name when provided", () => {
    expect(resolveSeedMesaName("  Minha Campanha  ")).toBe("Minha Campanha");
  });
});
