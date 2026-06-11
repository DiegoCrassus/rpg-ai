import { useSearchParams } from "react-router-dom";

import { DerivedBanner } from "../components/common/DerivedBanner";
import { PageHeader } from "../components/common/PageHeader";

type StubPageProps = {
  title: string;
  phase: string;
};

export function StubPage({ title, phase }: StubPageProps) {
  const [searchParams] = useSearchParams();
  const selectedNodeId = searchParams.get("node");

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <DerivedBanner />
      <PageHeader
        pageId="settings"
        title={title}
        subtitle={`Placeholder for ${phase}. Implementation follows the Studio Service roadmap.`}
      />
      {selectedNodeId ? (
        <div className="rounded-lg border border-studio-accent/30 bg-studio-accent/5 px-4 py-3 text-sm text-slate-300">
          <p className="text-xs uppercase tracking-wide text-slate-500">Selection context</p>
          <p className="mt-1 font-mono text-xs text-studio-accent">{selectedNodeId}</p>
          <p className="mt-2 text-xs text-slate-500">
            Propose-only — no files are written until a patch is merged via git/Plane workflow.
          </p>
        </div>
      ) : null}
      <div className="rounded-xl border border-dashed border-slate-700 bg-surface-card/50 p-8 text-center text-sm text-slate-500">
        Screen stub — no API wiring yet.
      </div>
    </div>
  );
}
