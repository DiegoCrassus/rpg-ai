import { useQuery } from "@tanstack/react-query";

import { studioApi } from "../../api/client";
import { planeStateGroupClass } from "./planeStateStyle";

function formatUpdatedAt(value?: string): string {
  if (!value) return "";
  try {
    return new Intl.DateTimeFormat(undefined, {
      month: "short",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
    }).format(new Date(value));
  } catch {
    return value;
  }
}

export function PlaneWorkFeed() {
  const feedQuery = useQuery({
    queryKey: ["studio", "integrations", "plane", "feed"],
    queryFn: () => studioApi.planeWorkFeed(12),
    retry: false,
    staleTime: 120_000,
    refetchInterval: 120_000,
  });

  return (
    <div className="rounded-xl border border-slate-800 bg-surface-card p-5">
      <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-400">
        Plane workboard
      </h2>
      <p className="mt-1 text-xs text-slate-500">Recent cards from Plane (read-only)</p>

      {feedQuery.isLoading ? (
        <p className="mt-4 text-sm text-slate-400">Loading Plane feed…</p>
      ) : feedQuery.isError ? (
        <p className="mt-4 text-sm text-amber-300/90">
          Plane not configured or unreachable. Set PLANE_API_KEY in the repo environment.
        </p>
      ) : feedQuery.data?.items.length === 0 ? (
        <p className="mt-4 text-sm text-slate-500">No issues returned from Plane.</p>
      ) : (
        <ul className="mt-3 max-h-72 space-y-1 overflow-y-auto">
          {feedQuery.data?.items.map((item) => (
            <li key={item.card}>
              <a
                href={item.plane_url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-start gap-2 rounded-md border border-transparent px-2 py-1.5 hover:border-slate-700 hover:bg-slate-900/60"
              >
                <span className="shrink-0 font-mono text-xs text-studio-accent">{item.card}</span>
                <span className="min-w-0 flex-1">
                  <span className="block truncate text-sm text-slate-200">{item.name}</span>
                  {item.updated_at ? (
                    <span className="text-[10px] text-slate-500">
                      {formatUpdatedAt(item.updated_at)}
                    </span>
                  ) : null}
                </span>
                <span
                  className={`shrink-0 rounded border px-1 py-0.5 text-[10px] uppercase ${planeStateGroupClass(item.state.group)}`}
                >
                  {item.state.name}
                </span>
              </a>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
