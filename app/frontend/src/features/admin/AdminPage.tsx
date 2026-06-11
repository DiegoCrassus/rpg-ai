import { useAuth } from "../../lib/auth";
import {
  useAdminAuditEvents,
  useAdminMesas,
  useAdminUsers,
  useSuspendUser,
} from "../../lib/queries";
import { LoadingSpinner } from "../../components/common/LoadingSpinner";
import { ErrorAlert } from "../../components/common/ErrorAlert";
import { Button } from "../../components/common/Button";
import { MESA_STATUS_LABELS } from "../../lib/labels";
import { Navigate } from "react-router-dom";

export function AdminPage() {
  const { user } = useAuth();
  const { data: users, isLoading: uLoading, error: uError } = useAdminUsers();
  const { data: mesas, isLoading: mLoading } = useAdminMesas();
  const { data: audit, isLoading: aLoading } = useAdminAuditEvents();
  const suspendUser = useSuspendUser();

  if (!user?.is_admin) {
    return <Navigate to="/mesas" replace />;
  }

  if (uLoading || mLoading || aLoading) return <LoadingSpinner />;
  if (uError) return <ErrorAlert message="Erro ao carregar dados de admin." />;

  return (
    <div className="space-y-10">
      <h1 className="text-2xl font-bold">Administração</h1>

      <section>
        <h2 className="text-lg font-semibold mb-3">Usuários</h2>
        <div className="overflow-x-auto rounded-lg border border-slate-800">
          <table className="w-full text-sm">
            <thead className="bg-slate-900 text-left text-slate-400">
              <tr>
                <th className="px-3 py-2">E-mail</th>
                <th className="px-3 py-2">Nome</th>
                <th className="px-3 py-2">Status</th>
                <th className="px-3 py-2">Mesas como Mestre</th>
                <th className="px-3 py-2">Ações</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {users?.map((u) => (
                <tr key={u.id}>
                  <td className="px-3 py-2">{u.email}</td>
                  <td className="px-3 py-2">{u.display_name}</td>
                  <td className="px-3 py-2">{u.status}</td>
                  <td className="px-3 py-2">{u.master_mesa_count}</td>
                  <td className="px-3 py-2">
                    {u.status === "active" ? (
                      <Button
                        variant="danger"
                        className="text-xs py-1"
                        onClick={() =>
                          void suspendUser.mutateAsync({ userId: u.id, status: "suspended" })
                        }
                      >
                        Suspender
                      </Button>
                    ) : (
                      <Button
                        variant="secondary"
                        className="text-xs py-1"
                        onClick={() =>
                          void suspendUser.mutateAsync({ userId: u.id, status: "active" })
                        }
                      >
                        Reativar
                      </Button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section>
        <h2 className="text-lg font-semibold mb-3">Mesas</h2>
        <ul className="divide-y divide-slate-800 rounded-lg border border-slate-800 text-sm">
          {mesas?.map((m) => (
            <li key={m.id} className="flex justify-between px-4 py-2">
              <span>{m.name}</span>
              <span className="text-slate-500">
                {MESA_STATUS_LABELS[m.status] ?? m.status} · {m.rpg_system}
              </span>
            </li>
          ))}
        </ul>
      </section>

      <section>
        <h2 className="text-lg font-semibold mb-3">Auditoria recente</h2>
        <ul className="space-y-1 text-xs text-slate-400 font-mono max-h-64 overflow-y-auto">
          {audit?.map((e) => (
            <li key={e.id}>
              {new Date(e.created_at).toLocaleString("pt-BR")} · {e.action} · {e.resource_type}
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
