import { useEffect, useState } from "react";
import { Navigate } from "react-router-dom";
import { supabase } from "../../lib/supabase";
import { LoadingSpinner } from "../../components/common/LoadingSpinner";
import { ErrorAlert } from "../../components/common/ErrorAlert";

export function AuthCallbackPage() {
  const [error, setError] = useState<string | null>(null);
  const [done, setDone] = useState(false);

  useEffect(() => {
    supabase.auth.getSession().then(({ data, error: sessionError }) => {
      if (sessionError) {
        setError(sessionError.message);
      } else if (data.session) {
        setDone(true);
      } else {
        setError("Sessão não encontrada após OAuth.");
      }
    });
  }, []);

  if (done) return <Navigate to="/mesas" replace />;
  if (error) return <ErrorAlert message={error} />;
  return <LoadingSpinner />;
}
