import { useRef, useState, type DragEvent } from "react";

export const IMPORT_FILE_ACCEPT =
  ".pdf,.png,.jpg,.jpeg,.webp,application/pdf,image/*";

interface FileDropzoneProps {
  file: File | null;
  onFile: (file: File | null) => void;
  required?: boolean;
  error?: string | null;
  disabled?: boolean;
}

export function FileDropzone({
  file,
  onFile,
  required = false,
  error,
  disabled = false,
}: FileDropzoneProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragOver, setDragOver] = useState(false);

  const pickFile = (next: File | null) => {
    if (disabled) return;
    onFile(next);
  };

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setDragOver(false);
    if (disabled) return;
    const dropped = e.dataTransfer.files[0];
    if (dropped) pickFile(dropped);
  };

  return (
    <div>
      <div className="mb-2 flex items-center gap-2">
        <span className="text-sm font-medium">Ficha oficial (PDF ou imagem)</span>
        {required && (
          <span className="rounded bg-amber-900/40 px-1.5 py-0.5 text-xs text-amber-300">
            Obrigatório
          </span>
        )}
      </div>
      <div
        role="button"
        tabIndex={disabled ? -1 : 0}
        onClick={() => !disabled && inputRef.current?.click()}
        onKeyDown={(e) => {
          if (disabled) return;
          if (e.key === "Enter" || e.key === " ") {
            e.preventDefault();
            inputRef.current?.click();
          }
        }}
        onDragOver={(e) => {
          e.preventDefault();
          if (!disabled) setDragOver(true);
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
        className={[
          "rounded-lg border border-dashed p-6 text-center transition cursor-pointer",
          dragOver ? "border-brand-500 bg-brand-950/30" : "border-slate-700",
          disabled ? "opacity-50 cursor-not-allowed" : "hover:border-slate-500",
          error ? "border-red-700" : "",
        ]
          .filter(Boolean)
          .join(" ")}
      >
        <input
          ref={inputRef}
          type="file"
          accept={IMPORT_FILE_ACCEPT}
          className="hidden"
          disabled={disabled}
          onChange={(e) => pickFile(e.target.files?.[0] ?? null)}
        />
        {file ? (
          <p className="text-sm text-slate-200">{file.name}</p>
        ) : (
          <p className="text-sm text-slate-400">
            Arraste o arquivo aqui ou clique para selecionar
          </p>
        )}
      </div>
      {error && <p className="mt-2 text-sm text-red-400">{error}</p>}
    </div>
  );
}
