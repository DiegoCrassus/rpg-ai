import type { SheetField } from "../../types/api";
import type { MediaUploadResult } from "../../lib/queries";
import { FieldRenderer } from "./FieldRenderer";
import { sortFields } from "./sheetUtils";

interface SheetFormProps {
  fields: SheetField[];
  values: Record<string, unknown>;
  onChange: (values: Record<string, unknown>) => void;
  readOnly?: boolean;
  onMediaUpload?: (fieldKey: string, file: File) => Promise<MediaUploadResult>;
  mediaPreviewUrls?: Record<string, string>;
  onPreviewUrl?: (path: string, url: string) => void;
}

export function SheetForm({
  fields,
  values,
  onChange,
  readOnly = false,
  onMediaUpload,
  mediaPreviewUrls,
  onPreviewUrl,
}: SheetFormProps) {
  return (
    <form
      className="space-y-2"
      onSubmit={(e) => e.preventDefault()}
    >
      {sortFields(fields).map((field) => (
        <FieldRenderer
          key={field.key}
          field={field}
          pathPrefix=""
          values={values}
          onChange={onChange}
          readOnly={readOnly}
          onMediaUpload={onMediaUpload}
          mediaPreviewUrls={mediaPreviewUrls}
          onPreviewUrl={onPreviewUrl}
        />
      ))}
    </form>
  );
}
