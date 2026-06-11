import { useEffect, useState } from "react";
import { Navigate, useSearchParams } from "react-router-dom";
import { getAuthRedirect } from "../../lib/authRedirect";
import { supabase } from "../../lib/supabase";
import { LoadingSpinner } from "../../components/common/LoadingSpinner";
import { ErrorAlert } from "../../components/common/ErrorAlert";

export function AuthCallbackPage() {
  const [searchParams] = useSearchParams();
  const redirectTo = getAuthRedirect(searchParams);
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

  if (done) return <Navigate to={redirectTo} replace />;
  if (error) return <ErrorAlert message={error} />;
  return <LoadingSpinner />;
}
