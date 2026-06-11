import { describe, expect, it } from "vitest";
import { getAuthRedirect } from "./authRedirect";

describe("getAuthRedirect", () => {
  it("uses redirect query param when safe", () => {
    const params = new URLSearchParams("redirect=%2Faccept-invite%3Ftoken%3Dabc");
    expect(getAuthRedirect(params)).toBe("/accept-invite?token=abc");
  });

  it("rejects external redirect targets", () => {
    const params = new URLSearchParams("redirect=//evil.example");
    expect(getAuthRedirect(params)).toBe("/mesas");
  });

  it("falls back to ProtectedRoute state.from", () => {
    const params = new URLSearchParams();
    const location = { state: { from: { pathname: "/mesas/123", search: "?tab=chars" } } };
    expect(getAuthRedirect(params, location)).toBe("/mesas/123?tab=chars");
  });
});
