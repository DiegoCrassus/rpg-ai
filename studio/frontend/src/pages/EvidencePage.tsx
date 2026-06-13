import { useCallback, useEffect, useMemo, useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";

import { studioApi } from "../api/client";
import { DerivedBanner } from "../components/common/DerivedBanner";
import { PageHeader } from "../components/common/PageHeader";
import type { EvidenceFields } from "../types/evidence";
import type { GitHubPull } from "../types/integrations";
import { copyToClipboard } from "./evidence/copyToClipboard";
import { formatEvidenceHtml, formatEvidenceMarkdown } from "./evidence/formatEvidenceComment";
import { DEFAULT_PLANE_CARD, PLANE_CARD_PATTERN } from "../constants/plane";

const FINISH_CHANGE_DOC = ".cursor/skills/finish-change/SKILL.md";
const EVIDENCE_TEMPLATE_REF = ".sdlc/templates/plane/evidence-template.json";

function finishChangeUrl(owner: string | undefined, repository: string | undefined): string {
  if (owner && repository) {
    const repo = repository.includes("/") ? repository : `${owner}/${repository}`;
    return `https://github.com/${repo}/blob/develop/${FINISH_CHANGE_DOC}`;
  }
  return `https://github.com/search?q=repo%3A+${encodeURIComponent(FINISH_CHANGE_DOC)}`;
}

function checksStatusClass(state: string | undefined): string {
  if (!state) {
    return "text-slate-400";
  }
  if (state === "success") {
    return "text-emerald-300";
  }
  if (state === "failure" || state === "error") {
    return "text-red-300";
  }
  return "text-amber-200";
}

function PullRow({
  pull,
  selected,
  onSelect,
}: {
  pull: GitHubPull;
  selected: boolean;
  onSelect: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onSelect}
      className={[
        "w-full rounded-lg border px-3 py-2 text-left text-sm transition-colors",
        selected
          ? "border-studio-accent/50 bg-studio-accent/10"
          : "border-slate-800 bg-surface-card hover:border-slate-600",
      ].join(" ")}
    >
      <span className="font-mono text-xs text-studio-accent">#{pull.number}</span>
      <span className="ml-2 text-white">{pull.title}</span>
      <p className="mt-1 font-mono text-[11px] text-slate-500">
        {pull.head.ref} → {pull.base.ref}
        {pull.draft ? " · draft" : ""}
      </p>
    </button>
  );
}

export function EvidencePage() {
  const [card, setCard] = useState(DEFAULT_PLANE_CARD);
  const [title, setTitle] = useState("");
  const [branch, setBranch] = useState("");
  const [fields, setFields] = useState<EvidenceFields | null>(null);
  const [copyMessage, setCopyMessage] = useState<string | null>(null);
  const [selectedPr, setSelectedPr] = useState<number | null>(null);
  const [checksRef, setChecksRef] = useState("");

  const sessionQuery = useQuery({
    queryKey: ["studio", "session", "gate"],
    queryFn: studioApi.sessionGate,
  });

  useEffect(() => {
    const gate = sessionQuery.data?.gate;
    if (gate?.card) {
      setCard(gate.card);
    }
    if (gate?.branch) {
      setBranch(gate.branch);
      setChecksRef(gate.branch);
    }
  }, [sessionQuery.data?.gate?.card, sessionQuery.data?.gate?.branch]);

  const draftMutation = useMutation({
    mutationFn: () =>
      studioApi.evidenceDraft({
        card: PLANE_CARD_PATTERN.test(card) ? card : undefined,
        title: title.trim() || undefined,
        branch: branch.trim() || undefined,
      }),
    onSuccess: (data) => {
      setFields(structuredClone(data.evidence_fields));
      if (!title.trim()) {
        setTitle(data.evidence_fields.title);
      }
    },
  });

  const planeQuery = useQuery({
    queryKey: ["studio", "integrations", "plane", card],
    queryFn: () => studioApi.planeCard(card),
    enabled: PLANE_CARD_PATTERN.test(card),
    retry: false,
  });

  const pullsQuery = useQuery({
    queryKey: ["studio", "integrations", "github", "pulls"],
    queryFn: () => studioApi.githubPulls(),
    retry: false,
  });

  const checksQuery = useQuery({
    queryKey: ["studio", "integrations", "github", "checks", checksRef],
    queryFn: () => studioApi.githubChecks(checksRef),
    enabled: Boolean(checksRef.trim()),
    retry: false,
  });

  const authority =
    draftMutation.data?.projection.authority ?? "derived_non_authoritative";

  const finishUrl = useMemo(
    () => finishChangeUrl(pullsQuery.data?.owner, pullsQuery.data?.repository),
    [pullsQuery.data?.owner, pullsQuery.data?.repository],
  );

  const loadDraft = useCallback(() => {
    if (PLANE_CARD_PATTERN.test(card)) {
      draftMutation.mutate();
    }
  }, [card, draftMutation.mutate]);

  useEffect(() => {
    if (PLANE_CARD_PATTERN.test(card) && sessionQuery.isSuccess) {
      draftMutation.mutate();
    }
  }, [card, sessionQuery.isSuccess, draftMutation.mutate]);

  const handleCopy = async (format: "markdown" | "html") => {
    if (!fields) {
      return;
    }
    const text = format === "markdown" ? formatEvidenceMarkdown(fields) : formatEvidenceHtml(fields);
    try {
      await copyToClipboard(text);
      setCopyMessage(
        format === "markdown" ? "Markdown copied to clipboard" : "HTML copied to clipboard",
      );
      window.setTimeout(() => setCopyMessage(null), 3000);
    } catch {
      setCopyMessage("Copy failed — select and copy manually from preview");
    }
  };

  const updateField = <K extends keyof EvidenceFields>(key: K, value: EvidenceFields[K]) => {
    setFields((prev) => (prev ? { ...prev, [key]: value } : prev));
  };

  const selectedPull = pullsQuery.data?.pulls.find((p) => p.number === selectedPr) ?? null;

  return (
    <div className="mx-auto max-w-6xl space-y-6">
      <DerivedBanner authority={authority} />

      <div
        role="status"
        className="rounded-lg border border-slate-600 bg-slate-900/50 px-4 py-3 text-sm text-slate-300"
      >
        Non-executing projection — paste into Plane manually after real QA and CI. Studio does not
        post comments or merge pull requests.
      </div>

      <PageHeader
        pageId="evidence"
        subtitle={`Draft from POST /studio/evidence/draft · template ${EVIDENCE_TEMPLATE_REF}`}
        aside={
          <div className="flex flex-wrap items-center gap-2">
            <a
              href={finishUrl}
              target="_blank"
              rel="noopener noreferrer"
              title={`Finish-change workflow (${FINISH_CHANGE_DOC})`}
              className="inline-flex h-8 items-center rounded-md border border-slate-600 px-3 text-xs text-slate-300 hover:border-studio-accent/50 hover:text-studio-accent"
              aria-label="Open finish-change skill documentation"
            >
              Finish-change docs
            </a>
            <button
              type="button"
              onClick={loadDraft}
              disabled={!PLANE_CARD_PATTERN.test(card) || draftMutation.isPending}
              className="rounded-md border border-studio-accent/50 bg-studio-accent/10 px-4 py-2 text-sm font-medium text-studio-accent hover:bg-studio-accent/20 disabled:opacity-50"
            >
              {draftMutation.isPending ? "Loading draft…" : "Refresh draft"}
            </button>
            {fields ? (
              <>
                <button
                  type="button"
                  onClick={() => handleCopy("markdown")}
                  className="rounded-md border border-slate-600 px-4 py-2 text-sm text-slate-200 hover:bg-slate-800"
                >
                  Copy markdown
                </button>
                <button
                  type="button"
                  onClick={() => handleCopy("html")}
                  className="rounded-md border border-slate-600 px-4 py-2 text-sm text-slate-200 hover:bg-slate-800"
                >
                  Copy HTML
                </button>
              </>
            ) : null}
          </div>
        }
      />

      {copyMessage ? (
        <p className="text-sm text-emerald-300" role="status">
          {copyMessage}
        </p>
      ) : null}

      {draftMutation.isError ? (
        <div className="rounded-lg border border-studio-fail/40 bg-red-950/40 p-4 text-red-200">
          <p className="font-medium">Cannot load evidence draft</p>
          <p className="mt-2 text-xs text-red-300/80">{draftMutation.error.message}</p>
        </div>
      ) : null}

      <div className="grid gap-6 lg:grid-cols-2">
        <section className="space-y-4 rounded-xl border border-slate-800 bg-surface-card p-4">
          <h2 className="text-lg font-semibold text-white">Evidence draft</h2>
          <div className="grid gap-3 sm:grid-cols-2">
            <label className="block text-sm text-slate-400">
              Card
              <input
                value={card}
                onChange={(e) => setCard(e.target.value.toUpperCase())}
                className="mt-1 w-full rounded border border-slate-700 bg-slate-900 px-2 py-1.5 font-mono text-sm text-slate-100"
                placeholder="RPG-91"
              />
            </label>
            <label className="block text-sm text-slate-400">
              Branch
              <input
                value={branch}
                onChange={(e) => {
                  setBranch(e.target.value);
                  setChecksRef(e.target.value);
                }}
                className="mt-1 w-full rounded border border-slate-700 bg-slate-900 px-2 py-1.5 font-mono text-sm text-slate-100"
                placeholder="feature/RPG-91-…"
              />
            </label>
          </div>
          <label className="block text-sm text-slate-400">
            Title
            <input
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="mt-1 w-full rounded border border-slate-700 bg-slate-900 px-2 py-1.5 text-sm text-slate-100"
            />
          </label>

          {planeQuery.isSuccess ? (
            <p className="text-xs text-slate-400">
              Plane:{" "}
              <a
                href={planeQuery.data.plane_url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-studio-accent hover:underline"
              >
                {planeQuery.data.name}
              </a>
              <span className="text-slate-500"> · {planeQuery.data.state.name}</span>
            </p>
          ) : planeQuery.isError ? (
            <p className="text-xs text-slate-500">Plane: not configured or unavailable</p>
          ) : null}

          {fields ? (
            <div className="space-y-3">
              <label className="block text-sm text-slate-400">
                Summary
                <textarea
                  value={fields.summary}
                  onChange={(e) => updateField("summary", e.target.value)}
                  rows={3}
                  className="mt-1 w-full rounded border border-slate-700 bg-slate-900 px-2 py-1.5 text-sm text-slate-100"
                />
              </label>
              <label className="block text-sm text-slate-400">
                Problems solved (one per line)
                <textarea
                  value={fields.problems_solved.join("\n")}
                  onChange={(e) =>
                    updateField(
                      "problems_solved",
                      e.target.value.split("\n").filter((line) => line.trim()),
                    )
                  }
                  rows={4}
                  className="mt-1 w-full rounded border border-slate-700 bg-slate-900 px-2 py-1.5 font-mono text-xs text-slate-100"
                />
              </label>
              <label className="block text-sm text-slate-400">
                Context for future (one per line)
                <textarea
                  value={fields.context_for_future.join("\n")}
                  onChange={(e) =>
                    updateField(
                      "context_for_future",
                      e.target.value.split("\n").filter((line) => line.trim()),
                    )
                  }
                  rows={3}
                  className="mt-1 w-full rounded border border-slate-700 bg-slate-900 px-2 py-1.5 font-mono text-xs text-slate-100"
                />
              </label>
              <details className="text-sm text-slate-400">
                <summary className="cursor-pointer text-slate-300">Technical &amp; validation</summary>
                <pre className="mt-2 max-h-48 overflow-auto rounded border border-slate-800 bg-slate-950 p-2 font-mono text-[11px] text-slate-400">
                  {JSON.stringify(
                    {
                      technical: fields.technical,
                      validation: fields.validation,
                      artifacts: fields.artifacts,
                    },
                    null,
                    2,
                  )}
                </pre>
              </details>
            </div>
          ) : draftMutation.isPending ? (
            <p className="text-slate-500">Loading evidence fields…</p>
          ) : (
            <p className="text-slate-500">Enter a valid card and refresh to load the draft.</p>
          )}
        </section>

        <section className="space-y-4 rounded-xl border border-slate-800 bg-surface-card p-4">
          <div className="flex items-center justify-between gap-2">
            <h2 className="text-lg font-semibold text-white">Pull requests &amp; CI</h2>
            <button
              type="button"
              onClick={() => {
                pullsQuery.refetch();
                if (checksRef.trim()) {
                  checksQuery.refetch();
                }
              }}
              className="rounded border border-slate-600 px-3 py-1 text-xs text-slate-300 hover:bg-slate-800"
            >
              Refresh
            </button>
          </div>

          {pullsQuery.isError ? (
            <p className="text-sm text-slate-500">
              GitHub pulls unavailable — configure token and repository env vars.
            </p>
          ) : pullsQuery.isLoading ? (
            <p className="text-slate-500">Loading open PRs…</p>
          ) : pullsQuery.data?.count === 0 ? (
            <p className="text-sm text-slate-500">No open pull requests for {pullsQuery.data.base}.</p>
          ) : (
            <ul className="max-h-48 space-y-2 overflow-y-auto">
              {pullsQuery.data?.pulls.map((pull) => (
                <li key={pull.number}>
                  <PullRow
                    pull={pull}
                    selected={selectedPr === pull.number}
                    onSelect={() => {
                      setSelectedPr(pull.number);
                      setChecksRef(pull.head.ref);
                    }}
                  />
                </li>
              ))}
            </ul>
          )}

          {selectedPull ? (
            <p className="text-xs text-slate-400">
              <a
                href={selectedPull.html_url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-studio-accent hover:underline"
              >
                View PR #{selectedPull.number} on GitHub
              </a>
            </p>
          ) : null}

          <label className="block text-sm text-slate-400">
            CI ref (branch or SHA)
            <input
              value={checksRef}
              onChange={(e) => setChecksRef(e.target.value)}
              className="mt-1 w-full rounded border border-slate-700 bg-slate-900 px-2 py-1.5 font-mono text-sm text-slate-100"
            />
          </label>

          {checksQuery.isError ? (
            <p className="text-sm text-slate-500">CI checks unavailable for this ref.</p>
          ) : checksQuery.isLoading && checksRef.trim() ? (
            <p className="text-slate-500">Loading check status…</p>
          ) : checksQuery.data ? (
            <div className="space-y-2 rounded-lg border border-slate-800 bg-slate-950/60 p-3 text-sm">
              <p>
                Commit{" "}
                <span className="font-mono text-xs text-slate-400">
                  {checksQuery.data.commit.sha?.slice(0, 7)}
                </span>
                {" · "}
                <span className={checksStatusClass(checksQuery.data.commit.combined_status)}>
                  {checksQuery.data.commit.combined_status ?? "unknown"}
                </span>
              </p>
              {checksQuery.data.commit.statuses?.length ? (
                <ul className="space-y-1 text-xs text-slate-400">
                  {checksQuery.data.commit.statuses.map((s) => (
                    <li key={s.context}>
                      <span className={checksStatusClass(s.state)}>{s.state}</span> — {s.context}
                    </li>
                  ))}
                </ul>
              ) : null}
              {checksQuery.data.workflow_runs.length > 0 ? (
                <ul className="space-y-1 border-t border-slate-800 pt-2 text-xs">
                  {checksQuery.data.workflow_runs.map((run) => (
                    <li key={run.id}>
                      <a
                        href={run.html_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-studio-accent hover:underline"
                      >
                        {run.name}
                      </a>
                      <span className="ml-2 text-slate-500">
                        {run.status}
                        {run.conclusion ? ` / ${run.conclusion}` : ""}
                      </span>
                    </li>
                  ))}
                </ul>
              ) : null}
            </div>
          ) : null}

          <p className="text-xs text-slate-500">
            Merge is handled outside Studio via finish-change on{" "}
            <code className="text-slate-400">develop</code> after QA and review.
          </p>
        </section>
      </div>
    </div>
  );
}
