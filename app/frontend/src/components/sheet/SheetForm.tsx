import type { SheetField } from "../../types/api";
import { FieldRenderer } from "./FieldRenderer";
import { sortFields } from "./sheetUtils";

interface SheetFormProps {
  fields: SheetField[];
  values: Record<string, unknown>;
  onChange: (values: Record<string, unknown>) => void;
  readOnly?: boolean;
}

export function SheetForm({ fields, values, onChange, readOnly = false }: SheetFormProps) {
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
        />
      ))}
    </form>
  );
}
