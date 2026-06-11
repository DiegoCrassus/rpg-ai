import type { FormEvent } from "react";
import { useState } from "react";
import { Link, Navigate, useLocation, useSearchParams } from "react-router-dom";
import { useAuth } from "../../lib/auth";
import { getAuthRedirect } from "../../lib/authRedirect";
import { supabase } from "../../lib/supabase";
import { Button } from "../../components/common/Button";
import { ErrorAlert } from "../../components/common/ErrorAlert";

export function LoginPage() {
  const { session } = useAuth();
  const [searchParams] = useSearchParams();
  const location = useLocation();
  const redirectTo = getAuthRedirect(searchParams, location);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  if (session) return <Navigate to={redirectTo} replace />;

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    const { error: authError } = await supabase.auth.signInWithPassword({ email, password });
    setLoading(false);
    if (authError) setError(authError.message);
  };

  const handleGoogle = async () => {
    setError(null);
    const callbackUrl = new URL("/auth/callback", window.location.origin);
    if (searchParams.get("redirect")) {
      callbackUrl.searchParams.set("redirect", searchParams.get("redirect")!);
    }
    const { error: authError } = await supabase.auth.signInWithOAuth({
      provider: "google",
      options: { redirectTo: callbackUrl.toString() },
    });
    if (authError) setError(authError.message);
  };

  return (
    <div className="mx-auto max-w-md pt-16">
      <h1 className="mb-6 text-2xl font-bold text-center">Entrar</h1>
      {error && <div className="mb-4"><ErrorAlert message={error} /></div>}
      <form onSubmit={(e) => void handleSubmit(e)} className="space-y-4">
        <div>
          <label className="block text-sm mb-1">E-mail</label>
          <input
            type="email"
            className="w-full"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>
        <div>
          <label className="block text-sm mb-1">Senha</label>
          <input
            type="password"
            className="w-full"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>
        <Button type="submit" className="w-full" disabled={loading}>
          {loading ? "Entrando…" : "Entrar"}
        </Button>
      </form>
      <div className="my-4 text-center text-sm text-slate-500">ou</div>
      <Button variant="secondary" className="w-full" onClick={() => void handleGoogle()}>
        Continuar com Google
      </Button>
      <p className="mt-6 text-center text-sm text-slate-400">
        Não tem conta? <Link to="/register" className="text-brand-400 hover:underline">Cadastre-se</Link>
      </p>
      <p className="mt-2 text-center text-sm">
        <Link to="/reset-password" className="text-slate-400 hover:underline">Esqueci minha senha</Link>
      </p>
    </div>
  );
}
