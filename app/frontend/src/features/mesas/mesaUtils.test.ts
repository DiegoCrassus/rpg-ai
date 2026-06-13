import { describe, expect, it } from "vitest";
import {
  DEFAULT_SEED_MESA_NAME,
  needsImportFile,
  resolveRpgSystem,
  resolveSeedMesaName,
  validateCreateForm,
} from "./mesaUtils";

describe("resolveSeedMesaName", () => {
  it("uses default when name is empty", () => {
    expect(resolveSeedMesaName("")).toBe(DEFAULT_SEED_MESA_NAME);
    expect(resolveSeedMesaName("   ")).toBe(DEFAULT_SEED_MESA_NAME);
  });

  it("uses trimmed form name when provided", () => {
    expect(resolveSeedMesaName("  Minha Campanha  ")).toBe("Minha Campanha");
  });
});

describe("resolveRpgSystem", () => {
  it("returns preset value for known ids", () => {
    expect(resolveRpgSystem("dnd5e", "")).toBe("D&D 5e");
    expect(resolveRpgSystem("pf2e", "")).toBe("Pathfinder 2e");
  });

  it("returns trimmed custom text for custom id", () => {
    expect(resolveRpgSystem("custom", "  Tormenta 20  ")).toBe("Tormenta 20");
  });
});

describe("needsImportFile", () => {
  it("skips upload when D&D uses platform template", () => {
    expect(needsImportFile("dnd5e", true)).toBe(false);
  });

  it("requires upload for D&D without platform template", () => {
    expect(needsImportFile("dnd5e", false)).toBe(true);
  });

  it("requires upload for non-D&D systems", () => {
    expect(needsImportFile("pf2e", false)).toBe(true);
    expect(needsImportFile("custom", false)).toBe(true);
  });
});

describe("validateCreateForm", () => {
  const base = {
    name: "Campanha",
    systemId: "dnd5e",
    customSystemText: "",
    usePlatformTemplate: true,
    file: null,
  };

  it("passes for D&D with platform template and no file", () => {
    expect(validateCreateForm(base).valid).toBe(true);
  });

  it("requires name", () => {
    const result = validateCreateForm({ ...base, name: "  " });
    expect(result.valid).toBe(false);
    expect(result.errors.name).toBeTruthy();
  });

  it("requires custom system name when custom selected", () => {
    const result = validateCreateForm({
      ...base,
      systemId: "custom",
      customSystemText: "",
    });
    expect(result.valid).toBe(false);
    expect(result.errors.system).toBeTruthy();
  });

  it("requires file when import is needed", () => {
    const result = validateCreateForm({
      ...base,
      usePlatformTemplate: false,
      file: null,
    });
    expect(result.valid).toBe(false);
    expect(result.errors.file).toBeTruthy();
  });

  it("passes when file provided for import flow", () => {
    const file = new File(["x"], "sheet.pdf", { type: "application/pdf" });
    const result = validateCreateForm({
      ...base,
      usePlatformTemplate: false,
      file,
    });
    expect(result.valid).toBe(true);
  });
});
