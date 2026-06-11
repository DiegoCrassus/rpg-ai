import { useState } from "react";
import type { SheetField } from "../../types/api";
import type { MediaUploadResult } from "../../lib/queries";
import { defaultRepeaterItem, getNestedValue, setNestedValue, sortFields } from "./sheetUtils";

interface FieldRendererProps {
  field: SheetField;
  pathPrefix: string;
  values: Record<string, unknown>;
  onChange: (values: Record<string, unknown>) => void;
  readOnly?: boolean;
  onMediaUpload?: (fieldKey: string, file: File) => Promise<MediaUploadResult>;
  mediaPreviewUrls?: Record<string, string>;
  onPreviewUrl?: (path: string, url: string) => void;
}

function fieldPath(prefix: string, key: string): string {
  return prefix ? `${prefix}.${key}` : key;
}

function acceptForField(field: SheetField): string {
  const exts = field.constraints?.allowed_extensions;
  if (field.type === "image") {
    return exts?.length ? exts.map((e) => `.${e}`).join(",") : "image/png,image/jpeg,image/webp";
  }
  return exts?.length ? exts.map((e) => `.${e}`).join(",") : "*/*";
}

function fileAllowed(file: File, field: SheetField): boolean {
  const exts = field.constraints?.allowed_extensions;
  if (!exts?.length) return true;
  const name = file.name.toLowerCase();
  return exts.some((ext) => name.endsWith(`.${ext.toLowerCase()}`));
}

function MediaField({
  field,
  path,
  pathValue,
  previewUrl,
  readOnly,
  onMediaUpload,
  onPreviewUrl,
  onUpdate,
}: {
  field: SheetField;
  path: string;
  pathValue: string;
  previewUrl?: string;
  readOnly: boolean;
  onMediaUpload?: (fieldKey: string, file: File) => Promise<MediaUploadResult>;
  onPreviewUrl?: (path: string, url: string) => void;
  onUpdate: (next: unknown) => void;
}) {
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);

  const label = (
    <label className="block text-sm font-medium text-slate-300 mb-1">
      {field.label}
      {field.required && <span className="text-red-400 ml-1">*</span>}
    </label>
  );

  const handleFile = async (file: File | undefined) => {
    if (!file || readOnly) return;
    if (!fileAllowed(file, field)) {
      setUploadError("Tipo de arquivo não permitido.");
      return;
    }
    if (!onMediaUpload) {
      setUploadError("Upload indisponível neste contexto.");
      return;
    }
    setUploadError(null);
    setUploading(true);
    try {
      const result = await onMediaUpload(field.key, file);
      onUpdate(result.storage_path);
      onPreviewUrl?.(path, result.signed_url);
    } catch (err) {
      setUploadError(err instanceof Error ? err.message : "Falha no upload.");
    } finally {
      setUploading(false);
    }
  };

  const resolvedPreview =
    previewUrl && (previewUrl.startsWith("http") || previewUrl.startsWith("memory://"))
      ? previewUrl
      : undefined;

  return (
    <div className="mb-4">
      {label}
      {field.type === "image" && resolvedPreview && (
        <img
          src={resolvedPreview}
          alt={field.label}
          className="mb-2 max-h-32 rounded border border-slate-700 object-contain"
        />
      )}
      {pathValue && <p className="mb-2 truncate text-xs text-slate-400">{pathValue}</p>}
      {field.type === "file" && pathValue && (
        <p className="mb-2 text-xs text-slate-500">
          {resolvedPreview ? (
            <a href={resolvedPreview} target="_blank" rel="noreferrer" className="text-brand-400 hover:underline">
              Abrir arquivo
            </a>
          ) : (
            "Arquivo anexado"
          )}
        </p>
      )}
      {!readOnly && (
        <>
          <input
            type="file"
            accept={acceptForField(field)}
            disabled={uploading}
            className="block w-full text-sm text-slate-300 file:mr-3 file:rounded file:border-0 file:bg-slate-700 file:px-3 file:py-1.5 file:text-sm file:text-slate-200"
            onChange={(e) => void handleFile(e.target.files?.[0])}
          />
          {uploading && <p className="mt-1 text-xs text-slate-500">Enviando…</p>}
          {uploadError && <p className="mt-1 text-xs text-red-400">{uploadError}</p>}
        </>
      )}
      {readOnly && !pathValue && <p className="text-xs text-slate-500">Nenhum arquivo</p>}
    </div>
  );
}

export function FieldRenderer({
  field,
  pathPrefix,
  values,
  onChange,
  readOnly = false,
  onMediaUpload,
  mediaPreviewUrls,
  onPreviewUrl,
}: FieldRendererProps) {
  const path = fieldPath(pathPrefix, field.key);
  const value = getNestedValue(values, path);

  const update = (next: unknown) => {
    onChange(setNestedValue(values, path, next));
  };

  const label = (
    <label className="block text-sm font-medium text-slate-300 mb-1">
      {field.label}
      {field.required && <span className="text-red-400 ml-1">*</span>}
    </label>
  );

  switch (field.type) {
    case "text":
      return (
        <div className="mb-4">
          {label}
          <input
            type="text"
            className="w-full"
            value={(value as string) ?? ""}
            maxLength={field.constraints?.max_length}
            disabled={readOnly}
            onChange={(e) => update(e.target.value)}
          />
        </div>
      );

    case "textarea":
      return (
        <div className="mb-4">
          {label}
          <textarea
            className="w-full min-h-[100px]"
            value={(value as string) ?? ""}
            maxLength={field.constraints?.max_length}
            disabled={readOnly}
            onChange={(e) => update(e.target.value)}
          />
        </div>
      );

    case "number":
      return (
        <div className="mb-4">
          {label}
          <input
            type="number"
            className="w-full"
            value={value === null || value === undefined ? "" : String(value)}
            min={field.constraints?.min}
            max={field.constraints?.max}
            step={field.constraints?.integer ? 1 : "any"}
            disabled={readOnly}
            onChange={(e) => {
              const raw = e.target.value;
              update(raw === "" ? null : Number(raw));
            }}
          />
        </div>
      );

    case "checkbox":
      return (
        <div className="mb-4 flex items-center gap-2">
          <input
            type="checkbox"
            checked={Boolean(value)}
            disabled={readOnly}
            onChange={(e) => update(e.target.checked)}
          />
          <span className="text-sm text-slate-300">{field.label}</span>
        </div>
      );

    case "select":
      return (
        <div className="mb-4">
          {label}
          <select
            className="w-full"
            value={(value as string) ?? ""}
            disabled={readOnly}
            onChange={(e) => update(e.target.value)}
          >
            <option value="">—</option>
            {(field.constraints?.options ?? []).map((opt) => (
              <option key={opt} value={opt}>
                {opt}
              </option>
            ))}
          </select>
        </div>
      );

    case "multiselect": {
      const selected = Array.isArray(value) ? (value as string[]) : [];
      return (
        <div className="mb-4">
          {label}
          <div className="flex flex-wrap gap-2">
            {(field.constraints?.options ?? []).map((opt) => {
              const checked = selected.includes(opt);
              return (
                <label key={opt} className="flex items-center gap-1 text-sm">
                  <input
                    type="checkbox"
                    checked={checked}
                    disabled={readOnly}
                    onChange={() => {
                      const next = checked
                        ? selected.filter((s) => s !== opt)
                        : [...selected, opt];
                      update(next);
                    }}
                  />
                  {opt}
                </label>
              );
            })}
          </div>
        </div>
      );
    }

    case "group":
      return (
        <fieldset className="mb-6 rounded-lg border border-slate-700 p-4">
          <legend className="px-2 text-sm font-semibold text-brand-100">{field.label}</legend>
          {sortFields(field.children ?? []).map((child) => (
            <FieldRenderer
              key={child.key}
              field={child}
              pathPrefix={path}
              values={values}
              onChange={onChange}
              readOnly={readOnly}
              onMediaUpload={onMediaUpload}
              mediaPreviewUrls={mediaPreviewUrls}
              onPreviewUrl={onPreviewUrl}
            />
          ))}
        </fieldset>
      );

    case "repeater": {
      const items = Array.isArray(value) ? (value as Record<string, unknown>[]) : [];
      const maxItems = field.constraints?.max_items ?? 50;
      return (
        <div className="mb-6">
          {label}
          <div className="space-y-4">
            {items.map((_item, index) => (
              <div key={index} className="rounded border border-slate-700 p-3">
                <div className="mb-2 flex items-center justify-between">
                  <span className="text-xs text-slate-400">
                    {field.item_label ?? "Item"} {index + 1}
                  </span>
                  {!readOnly && (
                    <button
                      type="button"
                      className="text-xs text-red-400 hover:text-red-300"
                      onClick={() => {
                        const next = items.filter((_, i) => i !== index);
                        update(next);
                      }}
                    >
                      Remover
                    </button>
                  )}
                </div>
                {sortFields(field.children ?? []).map((child) => (
                  <FieldRenderer
                    key={child.key}
                    field={child}
                    pathPrefix={`${path}.${index}`}
                    values={values}
                    onChange={onChange}
                    readOnly={readOnly}
                    onMediaUpload={onMediaUpload}
                    mediaPreviewUrls={mediaPreviewUrls}
                    onPreviewUrl={onPreviewUrl}
                  />
                ))}
              </div>
            ))}
          </div>
          {!readOnly && items.length < maxItems && (
            <button
              type="button"
              className="mt-2 text-sm text-brand-400 hover:text-brand-300"
              onClick={() => update([...items, defaultRepeaterItem(field.children)])}
            >
              + Adicionar {field.item_label ?? "item"}
            </button>
          )}
        </div>
      );
    }

    case "image":
    case "file":
      return (
        <MediaField
          field={field}
          path={path}
          pathValue={typeof value === "string" ? value : ""}
          previewUrl={mediaPreviewUrls?.[path]}
          readOnly={readOnly}
          onMediaUpload={onMediaUpload}
          onPreviewUrl={onPreviewUrl}
          onUpdate={update}
        />
      );

    default:
      return null;
  }
}
