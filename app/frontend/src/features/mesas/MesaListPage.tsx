import { Link } from "react-router-dom";
import { MESA_STATUS_LABELS } from "../../lib/labels";
import { useMesas } from "../../lib/queries";
import { useAuth } from "../../lib/auth";
import { LoadingSpinner } from "../../components/common/LoadingSpinner";
import { ErrorAlert } from "../../components/common/ErrorAlert";
import { Button } from "../../components/common/Button";

export function MesaListPage() {
  const { session, user, loading: authLoading } = useAuth();
  const { data: mesas, isLoading, isError } = useMesas({
    enabled: Boolean(session && user),
  });

  if (authLoading || isLoading) return <LoadingSpinner />;
  if (isError && !isLoading) {
    return <ErrorAlert message="Não foi possível carregar as mesas." />;
  }

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold">Minhas Mesas</h1>
      </div>

      {mesas?.length === 0 ? (
        <div className="flex justify-center py-12">
          <div className="max-w-md rounded-lg border border-slate-800 bg-slate-900/50 p-8 text-center">
            <h2 className="mb-2 text-xl font-semibold">Nenhuma mesa ainda</h2>
            <p className="mb-6 text-sm text-slate-400">
              Crie sua primeira mesa para começar uma campanha. Se preferir experimentar antes,
              use a mesa demo após rodar <code className="text-slate-300">migrate</code> e{" "}
              <code className="text-slate-300">seed-demo</code>.
            </p>
            <Link to="/mesas/new">
              <Button>Criar primeira mesa</Button>
            </Link>
          </div>
        </div>
      ) : (
        <ul className="grid gap-4 sm:grid-cols-2">
          {mesas?.map((mesa) => (
            <li key={mesa.id}>
              <Link
                to={`/mesas/${mesa.id}`}
                className="block rounded-lg border border-slate-800 bg-slate-900/50 p-4 hover:border-brand-600 transition"
              >
                <h2 className="font-semibold text-lg">{mesa.name}</h2>
                <p className="text-sm text-slate-400">{mesa.rpg_system}</p>
                <span className="mt-2 inline-block rounded bg-slate-800 px-2 py-0.5 text-xs text-slate-300">
                  {MESA_STATUS_LABELS[mesa.status] ?? mesa.status}
                </span>
              </Link>
            </li>
          ))}
          <li>
            <Link
              to="/mesas/new"
              className="flex h-full min-h-[120px] flex-col items-center justify-center rounded-lg border border-dashed border-slate-700 bg-slate-900/30 p-4 text-slate-400 transition hover:border-brand-600 hover:text-brand-300"
            >
              <span className="text-2xl leading-none">+</span>
              <span className="mt-2 text-sm font-medium">Nova mesa</span>
            </Link>
          </li>
        </ul>
      )}
    </div>
  );
}
