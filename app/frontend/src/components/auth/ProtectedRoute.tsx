import type { ReactNode } from "react";
import { Navigate, useLocation, useSearchParams } from "react-router-dom";
import { useAuth } from "../../lib/auth";
import { getAuthRedirect } from "../../lib/authRedirect";
import { LoadingSpinner } from "../common/LoadingSpinner";

export function ProtectedRoute({ children }: { children: ReactNode }) {
  const { session, loading, user } = useAuth();
  const location = useLocation();

  if (loading) return <LoadingSpinner />;

  if (!session) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (user?.status === "suspended") {
    return (
      <div className="mx-auto max-w-md pt-16 text-center text-red-300">
        Sua conta está suspensa. Entre em contato com o suporte.
      </div>
    );
  }

  return <>{children}</>;
}

export function PublicOnlyRoute({ children }: { children: ReactNode }) {
  const { session, loading } = useAuth();
  const [searchParams] = useSearchParams();
  const location = useLocation();
  if (loading) return <LoadingSpinner />;
  if (session) {
    return <Navigate to={getAuthRedirect(searchParams, location)} replace />;
  }
  return <>{children}</>;
}
