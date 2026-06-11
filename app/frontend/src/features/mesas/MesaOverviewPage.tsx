import { Link, Navigate } from "react-router-dom";
import { useOutletContext } from "react-router-dom";
import type { MesaContext } from "../../components/layout/MesaLayout";
import { useTemplates } from "../../lib/queries";
import { Button } from "../../components/common/Button";

export function MesaOverviewPage() {
  const { mesa, isMaster } = useOutletContext<MesaContext>();
  const { data: templates } = useTemplates(mesa.id);

  if (mesa.status === "importing" && isMaster) {
    return <Navigate to={`/mesas/${mesa.id}/import`} replace />;
  }

  return (
    <div className="space-y-6">
      <section>
        <h2 className="text-lg font-semibold mb-3">Atalhos</h2>
        <div className="flex flex-wrap gap-3">
          <Link to={`/mesas/${mesa.id}/characters`}>
            <Button variant="secondary">Personagens</Button>
          </Link>
          <Link to={`/mesas/${mesa.id}/documents`}>
            <Button variant="secondary">Documentos</Button>
          </Link>
          {isMaster && (
            <Link to={`/mesas/${mesa.id}/participants`}>
              <Button variant="secondary">Participantes</Button>
            </Link>
          )}
        </div>
      </section>

      {templates && templates.length > 0 && (
        <section>
          <h2 className="text-lg font-semibold mb-3">Templates de ficha</h2>
          <ul className="space-y-2">
            {templates.map((t) => (
              <li key={t.id} className="rounded border border-slate-800 px-3 py-2 text-sm">
                {t.name}
                {t.is_seed && (
                  <span className="ml-2 text-xs text-slate-500">(seed D&D 5e)</span>
                )}
              </li>
            ))}
          </ul>
        </section>
      )}
    </div>
  );
}
