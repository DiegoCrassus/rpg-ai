type ProposedBannerProps = {
  className?: string;
};

export function ProposedBanner({ className = "" }: ProposedBannerProps) {
  return (
    <div
      role="status"
      className={[
        "rounded-lg border border-amber-500/50 bg-amber-500/10 px-4 py-3 text-sm text-amber-100",
        className,
      ].join(" ")}
    >
      <span className="font-medium uppercase tracking-wide text-xs text-amber-300/90">
        Propose-only builder
      </span>
      <p className="mt-1">
        Visual graph edits are{" "}
        <code className="text-amber-200">proposed_non_authoritative</code>. Nothing is written to
        the repo until a patch is merged via Plane card → branch → commit → PR.
      </p>
    </div>
  );
}
