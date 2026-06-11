import type { FormEvent } from "react";
import { useState } from "react";
import { Link } from "react-router-dom";
import { supabase } from "../../lib/supabase";
import { Button } from "../../components/common/Button";
import { ErrorAlert } from "../../components/common/ErrorAlert";

export function ResetPasswordPage() {
  const [email, setEmail] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [sent, setSent] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    const { error: authError } = await supabase.auth.resetPasswordForEmail(email, {
      redirectTo: `${window.location.origin}/login`,
    });
    setLoading(false);
    if (authError) setError(authError.message);
    else setSent(true);
  };

  if (sent) {
    return (
      <div className="mx-auto max-w-md pt-16 text-center">
        <p className="text-slate-300">Se o e-mail existir, enviamos instruções de redefinição.</p>
        <Link to="/login" className="mt-4 inline-block text-brand-400 hover:underline">Voltar</Link>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-md pt-16">
      <h1 className="mb-6 text-2xl font-bold text-center">Redefinir senha</h1>
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
        <Button type="submit" className="w-full" disabled={loading}>
          Enviar link
        </Button>
      </form>
    </div>
  );
}
