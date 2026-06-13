import { describe, expect, it } from "vitest";
import { IMPORT_FILE_ACCEPT } from "../../components/common/FileDropzone";

describe("FileDropzone", () => {
  it("accepts pdf and image types consistent with import review", () => {
    expect(IMPORT_FILE_ACCEPT).toContain(".pdf");
    expect(IMPORT_FILE_ACCEPT).toContain("application/pdf");
    expect(IMPORT_FILE_ACCEPT).toContain("image/*");
    expect(IMPORT_FILE_ACCEPT).toContain(".webp");
  });
});
