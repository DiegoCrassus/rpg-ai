import type { CanvasLegend, ValidationStatus } from "../../types/canvas";
import { validationStatusColor } from "./mapViewModel";
import { ALL_VALIDATION_STATUSES, type ValidationVisibility } from "./validationVisibility";

type CanvasLegendPanelProps = {
  legend: CanvasLegend | undefined;
  visibleStatuses: ValidationVisibility;
  onToggleStatus: (status: ValidationStatus) => void;
};

const STATUS_LABELS: Record<ValidationStatus, string> = {
  pass: "Pass",
  warn: "Warn",
  fail: "Fail",
  not_run: "Not run",
};

export function CanvasLegendPanel({
  legend,
  visibleStatuses,
  onToggleStatus,
}: CanvasLegendPanelProps) {
  if (!legend) {
    return null;
  }

  return (
    <div className="rounded-xl border border-slate-800 bg-surface-card p-4">
      <h2 className="text-xs font-semibold uppercase tracking-wide text-slate-400">Legend</h2>
      <div className="mt-3 space-y-3">
        <div>
          <p className="text-xs text-slate-500">Categories</p>
          <ul className="mt-1 flex flex-wrap gap-2">
            {legend.categories.map((cat) => (
              <li
                key={cat.id}
                className="rounded-full border border-slate-700 px-2 py-0.5 text-xs text-slate-300"
              >
                {cat.label}
              </li>
            ))}
          </ul>
        </div>
        <div>
          <p className="text-xs text-slate-500">Validation (node border) — click to toggle</p>
          <ul className="mt-1 space-y-1">
            {ALL_VALIDATION_STATUSES.map((status) => {
              const active = visibleStatuses[status];
              return (
                <li key={status}>
                  <button
                    type="button"
                    aria-pressed={active}
                    className={[
                      "flex w-full items-center gap-2 rounded-md px-2 py-1 text-left text-xs transition-colors",
                      active
                        ? "text-slate-300 hover:bg-slate-800"
                        : "text-slate-500 line-through hover:bg-slate-800/60",
                    ].join(" ")}
                    onClick={() => onToggleStatus(status)}
                  >
                    <span
                      className={[
                        "inline-block h-2.5 w-2.5 rounded-full",
                        active ? "" : "opacity-40",
                      ].join(" ")}
                      style={{ backgroundColor: validationStatusColor(status) }}
                    />
                    {STATUS_LABELS[status]}
                    <span className="text-slate-500">
                      ({legend.validation_statuses[status] ?? 0})
                    </span>
                  </button>
                </li>
              );
            })}
          </ul>
        </div>
      </div>
    </div>
  );
}
