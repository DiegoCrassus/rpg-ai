import { useEffect, useState } from "react";

import { MarkdownContent } from "../common/MarkdownContent";

type EditorView = "preview" | "source";

type ConfigFileEditorProps = {
  content: string;
  onChange: (value: string) => void;
  loading?: boolean;
  /** Reset to preview when path changes */
  resetKey?: string | null;
};

export function ConfigFileEditor({
  content,
  onChange,
  loading = false,
  resetKey,
}: ConfigFileEditorProps) {
  const [view, setView] = useState<EditorView>("preview");

  useEffect(() => {
    setView("preview");
  }, [resetKey]);

  if (loading) {
    return <p className="text-slate-400">Loading file…</p>;
  }

  const panelClass =
    "min-h-0 overflow-y-auto overflow-x-hidden rounded-lg border border-slate-700 bg-slate-950/60 max-h-[min(32rem,calc(100vh-14rem))] lg:max-h-none lg:flex-1";

  return (
    <div
      className="flex flex-col gap-2 lg:min-h-0 lg:flex-1"
      data-testid="config-file-editor"
    >
      <div className="flex shrink-0 items-center gap-2">
        <span className="text-xs text-slate-500">View</span>
        <div className="inline-flex rounded-md border border-slate-700 p-0.5">
          <button
            type="button"
            data-testid="config-view-preview"
            onClick={() => setView("preview")}
            className={[
              "rounded px-3 py-1 text-xs font-medium transition-colors",
              view === "preview"
                ? "bg-studio-accent/20 text-studio-accent"
                : "text-slate-400 hover:text-white",
            ].join(" ")}
          >
            Preview
          </button>
          <button
            type="button"
            data-testid="config-view-source"
            onClick={() => setView("source")}
            className={[
              "rounded px-3 py-1 text-xs font-medium transition-colors",
              view === "source"
                ? "bg-studio-accent/20 text-studio-accent"
                : "text-slate-400 hover:text-white",
            ].join(" ")}
          >
            Edit source
          </button>
        </div>
      </div>

      {view === "preview" ? (
        <div className={`${panelClass} p-3`} data-testid="config-file-scroll">
          <MarkdownContent source={content} testId="config-file-preview" compact />
        </div>
      ) : (
        <textarea
          data-testid="config-file-source"
          className={`${panelClass} w-full resize-none p-3 font-mono text-xs text-slate-200`}
          value={content}
          onChange={(event) => onChange(event.target.value)}
          spellCheck={false}
        />
      )}
    </div>
  );
}
