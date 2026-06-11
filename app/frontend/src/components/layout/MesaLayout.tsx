import { NavLink, Outlet, useParams } from "react-router-dom";
import { useAuth } from "../../lib/auth";
import { isMaster } from "../../lib/labels";
import { useMesa } from "../../lib/queries";
import { LoadingSpinner } from "../common/LoadingSpinner";
import { ErrorAlert } from "../common/ErrorAlert";
import { MESA_STATUS_LABELS } from "../../lib/labels";

const tabs = [
  { to: "", label: "Visão geral", end: true },
  { to: "import", label: "Importação", masterOnly: true },
  { to: "characters", label: "Personagens" },
  { to: "documents", label: "Documentos" },
  { to: "participants", label: "Participantes", masterOnly: true },
];

export function MesaLayout() {
  const { mesaId = "" } = useParams();
  const { user } = useAuth();
  const { data: mesa, isLoading, error } = useMesa(mesaId);
  const master = mesa ? isMaster(mesa, user?.id) : false;

  if (isLoading) return <LoadingSpinner />;
  if (error || !mesa) {
    return <ErrorAlert message="Mesa não encontrada ou acesso negado." />;
  }

  const visibleTabs = tabs.filter((t) => !t.masterOnly || master);

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-slate-100">{mesa.name}</h1>
        <p className="text-sm text-slate-400">
          {mesa.rpg_system} · {MESA_STATUS_LABELS[mesa.status] ?? mesa.status}
          {master && " · Você é o Mestre"}
        </p>
        {mesa.description && (
          <p className="mt-2 text-slate-300">{mesa.description}</p>
        )}
      </div>

      <nav className="mb-6 flex flex-wrap gap-2 border-b border-slate-800 pb-2">
        {visibleTabs.map((tab) => (
          <NavLink
            key={tab.to}
            to={tab.to === "" ? `/mesas/${mesaId}` : `/mesas/${mesaId}/${tab.to}`}
            end={tab.end}
            className={({ isActive }) =>
              `rounded-md px-3 py-1.5 text-sm ${
                isActive
                  ? "bg-brand-600 text-white"
                  : "text-slate-400 hover:bg-slate-800 hover:text-slate-200"
              }`
            }
          >
            {tab.label}
          </NavLink>
        ))}
      </nav>

      <Outlet context={{ mesa, isMaster: master }} />
    </div>
  );
}

export interface MesaContext {
  mesa: NonNullable<ReturnType<typeof useMesa>["data"]>;
  isMaster: boolean;
}
