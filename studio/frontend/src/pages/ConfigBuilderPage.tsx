import { useCallback, useEffect, useMemo, useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";

import { studioApi } from "../api/client";
import { DEFAULT_PLANE_CARD } from "../constants/plane";
import { PageHeader } from "../components/common/PageHeader";
import type { PageHelpId } from "../components/common/pageHelp";
import { ConfigFileEditor } from "../components/builder/ConfigFileEditor";
import { ProposalPanel } from "../components/builder/ProposalPanel";
import { ProposedBanner } from "../components/builder/ProposedBanner";
import {
  buildConfigProposalRequest,
  CONFIG_KIND_META,
  isValidSlug,
  normalizeSlug,
  targetPathForSlug,
  templateContent,
  type ConfigBuilderMode,
} from "../components/builder/configDraft";
import type { ConfigKind } from "../types/config";
import type { ProposalResponse } from "../types/proposals";

const KIND_PAGE_ID: Record<ConfigKind, PageHelpId> = {
  agent: "agents",
  command: "commands",
  rule: "rules",
  skill: "rules",
};

type ConfigBuilderPageProps = {
  kind: ConfigKind;
  title: string;
  subtitle: string;
  pageId?: PageHelpId;
};

export function ConfigBuilderPage({ kind, title, subtitle, pageId }: ConfigBuilderPageProps) {
  const meta = CONFIG_KIND_META[kind];

  const [search, setSearch] = useState("");
  const [selectedPath, setSelectedPath] = useState<string | null>(null);
  const [mode, setMode] = useState<ConfigBuilderMode>("edit");
  const [newSlug, setNewSlug] = useState("");
  const [newDescription, setNewDescription] = useState("");
  const [editorContent, setEditorContent] = useState("");
  const [proposalTitle, setProposalTitle] = useState(meta.defaultTitle);
  const [simulatedCard, setSimulatedCard] = useState(DEFAULT_PLANE_CARD);
  const [proposal, setProposal] = useState<ProposalResponse | null>(null);

  const filesQuery = useQuery({
    queryKey: ["studio", "config", "files", kind, search],
    queryFn: () => studioApi.configFiles(kind, search.trim() || undefined),
    refetchInterval: 120_000,
  });

  const sessionQuery = useQuery({
    queryKey: ["studio", "session", "gate"],
    queryFn: studioApi.sessionGate,
  });

  useEffect(() => {
    const card = sessionQuery.data?.gate?.card;
    if (card) {
      setSimulatedCard(card);
    }
  }, [sessionQuery.data?.gate?.card]);

  const activePath = useMemo(() => {
    if (mode === "create") {
      const slug = normalizeSlug(newSlug);
      return slug && isValidSlug(slug) ? targetPathForSlug(kind, slug) : null;
    }
    return selectedPath;
  }, [kind, mode, newSlug, selectedPath]);

  const contentQuery = useQuery({
    queryKey: ["studio", "config", "file", activePath],
    queryFn: () => studioApi.configFile(activePath!),
    enabled: Boolean(activePath) && mode === "edit",
  });

  useEffect(() => {
    if (mode !== "edit" || !contentQuery.data) {
      return;
    }
    setEditorContent(contentQuery.data.content);
    setProposal(null);
  }, [contentQuery.data, mode]);

  const startCreate = useCallback(() => {
    setMode("create");
    setSelectedPath(null);
    setNewSlug("");
    setNewDescription("");
    const slug = "";
    setEditorContent(templateContent(kind, slug || "draft", ""));
    setProposalTitle(meta.defaultTitle);
    setProposal(null);
  }, [kind, meta.defaultTitle]);

  const selectFile = useCallback((path: string) => {
    setMode("edit");
    setSelectedPath(path);
    setProposal(null);
  }, []);

  useEffect(() => {
    if (mode !== "create") {
      return;
    }
    const slug = normalizeSlug(newSlug);
    if (!isValidSlug(slug)) {
      return;
    }
    setEditorContent(templateContent(kind, slug, newDescription));
  }, [kind, mode, newSlug, newDescription]);

  const createProposalMutation = useMutation({
    mutationFn: () => {
      if (!activePath) {
        throw new Error("Select a file or enter a valid slug");
      }
      const exists = mode === "edit" && (contentQuery.data?.exists ?? true);
      const body = buildConfigProposalRequest({
        kind,
        path: activePath,
        content: editorContent,
        title: proposalTitle,
        card: simulatedCard,
        mode,
        exists,
      });
      return studioApi.createProposal(body);
    },
    onSuccess: setProposal,
  });

  const slug = normalizeSlug(newSlug);
  const slugValid = isValidSlug(slug);

  if (filesQuery.isError) {
    return (
      <div className="mx-auto max-w-3xl space-y-4">
        <ProposedBanner />
        <div className="rounded-lg border border-studio-fail/40 bg-red-950/40 p-4 text-red-200">
          <p className="font-medium">Cannot load {meta.label} builder</p>
          <p className="mt-1 text-sm">
            Start the backend with <code className="text-red-100">make studio-dev</code>, then
            refresh.
          </p>
          <p className="mt-2 text-xs text-red-300/80">{filesQuery.error.message}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto flex max-w-[1600px] flex-col gap-4 lg:h-[calc(100vh-7rem)] lg:overflow-hidden">
      <div className="shrink-0 space-y-4">
        <ProposedBanner />

        <PageHeader
          pageId={pageId ?? KIND_PAGE_ID[kind]}
          title={title}
          subtitle={subtitle}
        />
      </div>

      <div className="grid gap-4 lg:min-h-0 lg:flex-1 lg:grid-cols-[280px_minmax(0,1fr)_320px] lg:overflow-hidden">
        <aside className="flex flex-col gap-3 rounded-xl border border-slate-800 bg-surface-card/30 p-4 lg:min-h-0 lg:overflow-hidden">
          <div className="flex items-center justify-between gap-2">
            <p className="text-xs uppercase tracking-wide text-slate-500">Files</p>
            <button
              type="button"
              onClick={startCreate}
              className="rounded-md border border-slate-600 px-2 py-1 text-xs text-slate-200 hover:bg-slate-800"
            >
              New
            </button>
          </div>
          <input
            className="w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-white"
            placeholder="Search…"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
          />
          {filesQuery.isLoading ? (
            <p className="text-sm text-slate-400">Loading…</p>
          ) : (
            <ul className="max-h-48 space-y-1 overflow-y-auto text-sm lg:max-h-none lg:min-h-0 lg:flex-1">
              {(filesQuery.data?.files ?? []).map((file) => (
                <li key={file.path}>
                  <button
                    type="button"
                    onClick={() => selectFile(file.path)}
                    className={[
                      "w-full rounded-md px-2 py-1.5 text-left font-mono text-xs",
                      selectedPath === file.path && mode === "edit"
                        ? "bg-studio-accent/15 text-studio-accent"
                        : "text-slate-300 hover:bg-slate-800",
                    ].join(" ")}
                  >
                    {file.name}
                  </button>
                </li>
              ))}
            </ul>
          )}
        </aside>

        <section className="flex flex-col gap-3 rounded-xl border border-slate-800 bg-surface-card/30 p-4 lg:min-h-0 lg:overflow-hidden">
          {mode === "create" ? (
            <div className="grid shrink-0 gap-3 sm:grid-cols-2">
              <label className="block text-sm">
                <span className="text-slate-400">Slug</span>
                <input
                  className="mt-1 w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 font-mono text-xs text-white"
                  value={newSlug}
                  onChange={(event) => setNewSlug(event.target.value)}
                  placeholder="my-agent"
                />
                {!newSlug || slugValid ? null : (
                  <span className="mt-1 block text-xs text-amber-300">
                    Use lowercase letters, numbers, and hyphens.
                  </span>
                )}
              </label>
              <label className="block text-sm">
                <span className="text-slate-400">Short description</span>
                <input
                  className="mt-1 w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-white"
                  value={newDescription}
                  onChange={(event) => setNewDescription(event.target.value)}
                />
              </label>
            </div>
          ) : null}

          <p className="shrink-0 font-mono text-xs text-slate-500">
            {activePath ?? meta.pathHint}
            {mode === "create" ? " (new)" : ""}
          </p>

          <div className="flex flex-col lg:min-h-0 lg:flex-1">
            <ConfigFileEditor
              content={editorContent}
              loading={mode === "edit" && contentQuery.isLoading}
              resetKey={activePath}
              onChange={(value) => {
                setEditorContent(value);
                setProposal(null);
              }}
            />
          </div>

          {mode === "create" && slugValid ? (
            <p className="text-xs text-amber-300/90">
              New skills require the parent folder to exist in the repo before create_file succeeds.
            </p>
          ) : null}
        </section>

        <aside className="min-h-0 space-y-4 overflow-y-auto rounded-xl border border-slate-800 bg-surface-card p-4">
          <p className="text-xs uppercase tracking-wide text-slate-500">Export proposal</p>
          <label className="mt-3 block text-sm">
            <span className="text-slate-400">Title</span>
            <input
              className="mt-1 w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-white"
              value={proposalTitle}
              onChange={(event) => setProposalTitle(event.target.value)}
            />
          </label>
          <label className="mt-3 block text-sm">
            <span className="text-slate-400">Simulated gate card</span>
            <input
              className="mt-1 w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 font-mono text-xs text-white"
              value={simulatedCard}
              onChange={(event) => setSimulatedCard(event.target.value)}
            />
          </label>
          <button
            type="button"
            disabled={
              createProposalMutation.isPending ||
              !activePath ||
              !editorContent.trim() ||
              (mode === "create" && !slugValid)
            }
            onClick={() => createProposalMutation.mutate()}
            className="mt-4 w-full rounded-md bg-studio-accent px-4 py-2 text-sm font-medium text-slate-950 hover:bg-sky-300 disabled:opacity-50"
          >
            {createProposalMutation.isPending ? "Creating proposal…" : "Create proposal"}
          </button>
          {createProposalMutation.error ? (
            <p className="mt-2 text-sm text-red-300">
              {(createProposalMutation.error as Error).message}
            </p>
          ) : null}
        </aside>
      </div>

      {proposal ? (
        <div className="max-h-[min(40vh,20rem)] shrink-0 overflow-y-auto">
          <ProposalPanel
            proposal={proposal}
            onUpdated={setProposal}
            onDiscard={() => setProposal(null)}
          />
        </div>
      ) : null}
    </div>
  );
}
