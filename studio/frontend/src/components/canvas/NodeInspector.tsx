import type { CanvasNodeDetailResponse } from "../../types/canvas";

type NodeInspectorProps = {
  detail: CanvasNodeDetailResponse | undefined;
  loading: boolean;
  onClose: () => void;
};

export function NodeInspector({ detail, loading, onClose }: NodeInspectorProps) {
  if (!detail && !loading) {
    return null;
  }

  const node = detail?.node;

  return (
    <aside className="flex w-full max-w-md flex-col rounded-xl border border-slate-800 bg-surface-card lg:w-96">
      <div className="flex items-center justify-between border-b border-slate-800 px-4 py-3">
        <h2 className="text-sm font-semibold text-white">Node inspector</h2>
        <button
          type="button"
          className="text-xs text-slate-400 hover:text-white"
          onClick={onClose}
        >
          Close
        </button>
      </div>

      {loading ? (
        <p className="p-4 text-sm text-slate-400">Loading node detail…</p>
      ) : node ? (
        <div className="flex-1 space-y-4 overflow-y-auto p-4 text-sm">
          <div>
            <p className="text-xs uppercase tracking-wide text-slate-500">Label</p>
            <p className="mt-1 font-medium text-white">{node.label}</p>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <p className="text-xs uppercase tracking-wide text-slate-500">Type</p>
              <p className="mt-1 text-slate-200">{node.type}</p>
            </div>
            <div>
              <p className="text-xs uppercase tracking-wide text-slate-500">Category</p>
              <p className="mt-1 text-slate-200">{node.category}</p>
            </div>
          </div>
          <div>
            <p className="text-xs uppercase tracking-wide text-slate-500">Graph node id</p>
            <p className="mt-1 break-all font-mono text-xs text-slate-300">{node.graph_node_id}</p>
          </div>

          {node.validation_overlays.length > 0 ? (
            <div>
              <p className="text-xs uppercase tracking-wide text-slate-500">Validation</p>
              <ul className="mt-2 space-y-2">
                {node.validation_overlays.map((overlay) => (
                  <li
                    key={overlay.id}
                    className="rounded-lg border border-slate-700 bg-slate-900/60 px-3 py-2"
                  >
                    <p className="font-medium text-slate-200">{overlay.check_type}</p>
                    <p className="text-xs text-slate-400">
                      {overlay.status} · {overlay.message_count} message(s)
                    </p>
                  </li>
                ))}
              </ul>
            </div>
          ) : (
            <p className="text-xs text-slate-500">No validation overlays on this node.</p>
          )}

          <div>
            <p className="text-xs uppercase tracking-wide text-slate-500">Source refs</p>
            <ul className="mt-2 space-y-2">
              {node.source_refs.map((ref) => (
                <li key={`${ref.ref_type}-${ref.ref}`} className="rounded-lg bg-slate-900/60 px-3 py-2">
                  <p className="font-mono text-xs text-studio-accent">{ref.ref}</p>
                  {ref.summary ? <p className="mt-1 text-xs text-slate-400">{ref.summary}</p> : null}
                </li>
              ))}
            </ul>
          </div>

          {detail?.overlays.length ? (
            <div>
              <p className="text-xs uppercase tracking-wide text-slate-500">
                Attached overlays ({detail.overlays.length})
              </p>
              <ul className="mt-2 space-y-1 text-xs text-slate-400">
                {detail.overlays.map((overlay) => (
                  <li key={overlay.id}>
                    {overlay.check_type} — {overlay.status}
                  </li>
                ))}
              </ul>
            </div>
          ) : null}
        </div>
      ) : null}
    </aside>
  );
}
