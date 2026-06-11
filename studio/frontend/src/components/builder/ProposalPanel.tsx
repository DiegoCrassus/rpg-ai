import { useMutation } from "@tanstack/react-query";

import { studioApi } from "../../api/client";
import type { DryRunResult, ProposalResponse } from "../../types/proposals";

type ProposalPanelProps = {
  proposal: ProposalResponse;
  onUpdated: (proposal: ProposalResponse) => void;
  onDiscard: () => void;
};

function DryRunBadge({ result }: { result: DryRunResult | undefined }) {
  if (!result) {
    return null;
  }
  const ok = result.exit_code === 0;
  return (
    <span
      className={[
        "rounded px-2 py-0.5 text-xs font-medium",
        ok ? "bg-emerald-500/20 text-emerald-300" : "bg-red-500/20 text-red-300",
      ].join(" ")}
    >
      {result.step}: exit {result.exit_code}
    </span>
  );
}

export function ProposalPanel({ proposal, onUpdated, onDiscard }: ProposalPanelProps) {
  const refreshProposal = async () => {
    const fresh = await studioApi.getProposal(proposal.proposal_id);
    onUpdated(fresh);
    return fresh;
  };

  const validateMutation = useMutation({
    mutationFn: () => studioApi.validateProposal(proposal.proposal_id),
    onSuccess: refreshProposal,
  });

  const doctorMutation = useMutation({
    mutationFn: () => studioApi.doctorProposal(proposal.proposal_id),
    onSuccess: refreshProposal,
  });

  const gatewayMutation = useMutation({
    mutationFn: () => studioApi.gatewayCheckProposal(proposal.proposal_id),
    onSuccess: refreshProposal,
  });

  const discardMutation = useMutation({
    mutationFn: () => studioApi.deleteProposal(proposal.proposal_id),
    onSuccess: onDiscard,
  });

  const dryRuns = proposal.dry_runs ?? {};
  const running =
    validateMutation.isPending ||
    doctorMutation.isPending ||
    gatewayMutation.isPending ||
    discardMutation.isPending;

  const lastError =
    validateMutation.error ??
    doctorMutation.error ??
    gatewayMutation.error ??
    discardMutation.error;

  return (
    <div className="space-y-4 rounded-xl border border-slate-800 bg-surface-card p-4">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="text-xs uppercase tracking-wide text-slate-500">Proposal preview</p>
          <p className="mt-1 text-sm font-medium text-white">{proposal.title}</p>
          <p className="mt-1 font-mono text-xs text-slate-400">{proposal.proposal_id}</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <DryRunBadge result={dryRuns.validate} />
          <DryRunBadge result={dryRuns.doctor} />
          <DryRunBadge result={dryRuns["gateway-check"]} />
        </div>
      </div>

      <div>
        <p className="text-xs text-slate-500">Unified diff</p>
        <pre className="mt-2 max-h-64 overflow-auto rounded-lg border border-slate-700 bg-slate-950 p-3 text-xs text-slate-300">
          {proposal.patch_body || "(no diff — proposed content matches current file)"}
        </pre>
      </div>

      <div className="flex flex-wrap gap-2">
        <button
          type="button"
          disabled={running}
          onClick={() => validateMutation.mutate()}
          className="rounded-md border border-slate-600 px-3 py-2 text-sm text-slate-200 hover:bg-slate-800 disabled:opacity-50"
        >
          Validate
        </button>
        <button
          type="button"
          disabled={running}
          onClick={() => doctorMutation.mutate()}
          className="rounded-md border border-slate-600 px-3 py-2 text-sm text-slate-200 hover:bg-slate-800 disabled:opacity-50"
        >
          Doctor
        </button>
        <button
          type="button"
          disabled={running}
          onClick={() => gatewayMutation.mutate()}
          className="rounded-md border border-slate-600 px-3 py-2 text-sm text-slate-200 hover:bg-slate-800 disabled:opacity-50"
        >
          Gateway check
        </button>
        <button
          type="button"
          disabled={running}
          onClick={() => discardMutation.mutate()}
          className="rounded-md border border-studio-fail/40 px-3 py-2 text-sm text-studio-fail hover:bg-red-950/40 disabled:opacity-50"
        >
          Discard
        </button>
      </div>

      {lastError ? (
        <p className="text-sm text-red-300">{(lastError as Error).message}</p>
      ) : null}

      {(dryRuns.validate || dryRuns.doctor || dryRuns["gateway-check"]) && (
        <div className="space-y-2 text-xs text-slate-400">
          {(["validate", "doctor", "gateway-check"] as const).map((step) => {
            const result = dryRuns[step];
            if (!result) {
              return null;
            }
            return (
              <p key={step}>
                <span className="font-medium text-slate-300">{step}:</span> {result.summary}
              </p>
            );
          })}
        </div>
      )}
    </div>
  );
}
