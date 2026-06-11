type DerivedBannerProps = {
  authority?: string | null;
  className?: string;
};

const DEFAULT_AUTHORITY = "derived_non_authoritative";

export function DerivedBanner({ authority, className = "" }: DerivedBannerProps) {
  const label = authority?.trim() || DEFAULT_AUTHORITY;
  const isDerived = label === DEFAULT_AUTHORITY || label.includes("non_authoritative");

  return (
    <div
      role="status"
      className={[
        "rounded-lg border px-4 py-3 text-sm",
        isDerived
          ? "border-amber-500/40 bg-amber-500/10 text-amber-100"
          : "border-slate-600 bg-slate-800/60 text-slate-200",
        className,
      ].join(" ")}
    >
      <span className="font-medium uppercase tracking-wide text-xs text-amber-300/90">
        Non-authoritative view
      </span>
      <p className="mt-1">
        Data shown here is <code className="text-amber-200">{label}</code>. Plane, GitHub, and
        committed repo files remain the source of truth.
      </p>
    </div>
  );
}
