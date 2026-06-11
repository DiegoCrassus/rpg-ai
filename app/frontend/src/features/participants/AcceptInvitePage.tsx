import type { FormEvent } from "react";
import { useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { useAcceptInvite } from "../../lib/queries";
import { useAuth } from "../../lib/auth";
import { Button } from "../../components/common/Button";
import { ErrorAlert } from "../../components/common/ErrorAlert";
import { LoadingSpinner } from "../../components/common/LoadingSpinner";
import { ApiError } from "../../lib/api";

export function AcceptInvitePage() {
  const [params] = useSearchParams();
  const navigate = useNavigate();
  const { session, loading } = useAuth();
  const acceptInvite = useAcceptInvite();
  const [token, setToken] = useState(params.get("token") ?? "");
  const [error, setError] = useState<string | null>(null);

  if (loading) return <LoadingSpinner />;

  if (!session) {
    return (
      <div className="mx-auto max-w-md pt-16 text-center">
        <p className="mb-4 text-slate-300">Faça login para aceitar o convite.</p>
        <Button
          onClick={() => {
            const redirectTarget = token
              ? `/accept-invite?token=${encodeURIComponent(token)}`
              : "/accept-invite";
            navigate(`/login?redirect=${encodeURIComponent(redirectTarget)}`);
          }}
        >
          Ir para login
        </Button>
      </div>
    );
  }

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);
    try {
      const result = await acceptInvite.mutateAsync(token);
      navigate(`/mesas/${result.mesa_id}`);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Falha ao aceitar convite.");
    }
  };

  return (
    <div className="mx-auto max-w-md pt-16">
      <h1 className="mb-6 text-xl font-bold text-center">Aceitar convite</h1>
      {error && <div className="mb-4"><ErrorAlert message={error} /></div>}
      <form onSubmit={(e) => void handleSubmit(e)} className="space-y-4">
        <div>
          <label className="block text-sm mb-1">Token do convite</label>
          <input className="w-full" value={token} onChange={(e) => setToken(e.target.value)} required />
        </div>
        <Button type="submit" className="w-full" disabled={acceptInvite.isPending}>
          Entrar na mesa
        </Button>
      </form>
    </div>
  );
}
