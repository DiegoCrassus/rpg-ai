import { describe, expect, it } from "vitest";
import { defaultRepeaterItem, getNestedValue, setNestedValue, sortFields } from "./sheetUtils";

describe("sheetUtils", () => {
  it("sorts fields by order", () => {
    const sorted = sortFields([
      { key: "b", order: 2 },
      { key: "a", order: 1 },
    ]);
    expect(sorted.map((f) => f.key)).toEqual(["a", "b"]);
  });

  it("gets and sets nested values", () => {
    const values = { identity: { character_name: "Aragorn" } };
    expect(getNestedValue(values, "identity.character_name")).toBe("Aragorn");
    const next = setNestedValue(values, "identity.level", 5);
    expect(getNestedValue(next, "identity.level")).toBe(5);
  });

  it("builds default repeater item", () => {
    const item = defaultRepeaterItem([
      { key: "name", type: "text" },
      { key: "bonus", type: "number" },
      { key: "proficient", type: "checkbox" },
    ]);
    expect(item).toEqual({ name: "", bonus: null, proficient: false });
  });
});
