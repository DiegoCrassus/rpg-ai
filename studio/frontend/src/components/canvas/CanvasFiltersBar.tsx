import type { CanvasFilterParams, CanvasLegend, ValidationStatus } from "../../types/canvas";

type CanvasFiltersProps = {
  legend: CanvasLegend | undefined;
  filters: CanvasFilterParams;
  meta?: { filtered_nodes: number; total_nodes: number; filtered_edges: number; total_edges: number };
  onChange: (next: CanvasFilterParams) => void;
  onReset: () => void;
};

const VALIDATION_OPTIONS: ValidationStatus[] = ["pass", "warn", "fail", "not_run"];

export function CanvasFiltersBar({
  legend,
  filters,
  meta,
  onChange,
  onReset,
}: CanvasFiltersProps) {
  const hasActive =
    Boolean(filters.section) ||
    Boolean(filters.validation_status) ||
    Boolean(filters.entity_type) ||
    Boolean(filters.q?.trim());

  return (
    <div className="flex flex-wrap items-end gap-3 rounded-xl border border-slate-800 bg-surface-card p-4">
      <label className="flex min-w-[140px] flex-col gap-1 text-xs text-slate-400">
        Section
        <select
          className="rounded-md border border-slate-700 bg-slate-900 px-2 py-1.5 text-sm text-white"
          value={filters.section ?? ""}
          onChange={(e) =>
            onChange({ ...filters, section: e.target.value || undefined })
          }
        >
          <option value="">All sections</option>
          {legend?.categories.map((cat) => (
            <option key={cat.id} value={cat.id}>
              {cat.label}
            </option>
          ))}
        </select>
      </label>

      <label className="flex min-w-[140px] flex-col gap-1 text-xs text-slate-400">
        Validation
        <select
          className="rounded-md border border-slate-700 bg-slate-900 px-2 py-1.5 text-sm text-white"
          value={filters.validation_status ?? ""}
          onChange={(e) =>
            onChange({
              ...filters,
              validation_status: (e.target.value as ValidationStatus) || undefined,
            })
          }
        >
          <option value="">Any status</option>
          {VALIDATION_OPTIONS.map((status) => (
            <option key={status} value={status}>
              {status}
            </option>
          ))}
        </select>
      </label>

      <label className="flex min-w-[120px] flex-col gap-1 text-xs text-slate-400">
        Entity type
        <input
          type="text"
          placeholder="e.g. stage, agent"
          className="rounded-md border border-slate-700 bg-slate-900 px-2 py-1.5 text-sm text-white placeholder:text-slate-600"
          value={filters.entity_type ?? ""}
          onChange={(e) =>
            onChange({ ...filters, entity_type: e.target.value || undefined })
          }
        />
      </label>

      <label className="flex min-w-[180px] flex-1 flex-col gap-1 text-xs text-slate-400">
        Search
        <input
          type="search"
          placeholder="Label, id, source ref…"
          className="rounded-md border border-slate-700 bg-slate-900 px-2 py-1.5 text-sm text-white placeholder:text-slate-600"
          value={filters.q ?? ""}
          onChange={(e) => onChange({ ...filters, q: e.target.value || undefined })}
        />
      </label>

      {hasActive ? (
        <button
          type="button"
          className="rounded-md border border-slate-600 px-3 py-1.5 text-sm text-slate-300 hover:bg-slate-800"
          onClick={onReset}
        >
          Clear filters
        </button>
      ) : null}

      {meta ? (
        <p className="ml-auto text-xs text-slate-500">
          {meta.filtered_nodes}/{meta.total_nodes} nodes · {meta.filtered_edges}/{meta.total_edges}{" "}
          edges
        </p>
      ) : null}
    </div>
  );
}
