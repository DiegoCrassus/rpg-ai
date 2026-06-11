import type { FormEvent } from "react";
import { useState } from "react";
import { useOutletContext } from "react-router-dom";
import type { MesaContext } from "../../components/layout/MesaLayout";
import { useCreateInvite, useInvites, useParticipants } from "../../lib/queries";
import { LoadingSpinner } from "../../components/common/LoadingSpinner";
import { ErrorAlert } from "../../components/common/ErrorAlert";
import { Button } from "../../components/common/Button";

export function ParticipantsPage() {
  const { mesa, isMaster } = useOutletContext<MesaContext>();
  const { data: participants, isLoading: pLoading } = useParticipants(mesa.id);
  const { data: invites, isLoading: iLoading } = useInvites(mesa.id);
  const createInvite = useCreateInvite(mesa.id);
  const [email, setEmail] = useState("");
  const [lastToken, setLastToken] = useState<string | null>(null);

  if (!isMaster) {
    return <ErrorAlert message="Somente o Mestre gerencia participantes." />;
  }

  if (pLoading || iLoading) return <LoadingSpinner />;

  const handleInvite = async (e: FormEvent) => {
    e.preventDefault();
    const invite = await createInvite.mutateAsync(email);
    setLastToken(invite.token ?? null);
    setEmail("");
  };

  return (
    <div className="space-y-8">
      <section>
        <h2 className="text-lg font-semibold mb-3">Participantes</h2>
        <ul className="divide-y divide-slate-800 rounded-lg border border-slate-800">
          {participants?.map((p) => (
            <li key={p.id} className="flex justify-between px-4 py-2 text-sm">
              <span>{p.user_id.slice(0, 8)}…</span>
              <span className="text-slate-500 capitalize">{p.role}</span>
            </li>
          ))}
        </ul>
      </section>

      <section>
        <h2 className="text-lg font-semibold mb-3">Convites</h2>
        <form onSubmit={(e) => void handleInvite(e)} className="mb-4 flex gap-2">
          <input
            type="email"
            className="flex-1"
            placeholder="e-mail do jogador"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <Button type="submit" disabled={createInvite.isPending}>Convidar</Button>
        </form>
        {lastToken && (
          <div className="mb-4 rounded border border-brand-800 bg-brand-950/30 p-3 text-sm">
            <p className="text-slate-300 mb-1">Link de convite (MVP — copie e envie manualmente):</p>
            <code className="break-all text-brand-300">
              {window.location.origin}/accept-invite?token={lastToken}
            </code>
          </div>
        )}
        <ul className="space-y-2 text-sm">
          {invites?.map((inv) => (
            <li key={inv.id} className="flex justify-between text-slate-400">
              <span>{inv.email}</span>
              <span>{inv.status} · expira {new Date(inv.expires_at).toLocaleDateString("pt-BR")}</span>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
