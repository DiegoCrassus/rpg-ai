import type { Location } from "react-router-dom";

/** Resolve safe in-app path after login (query param or ProtectedRoute state). */
export function getAuthRedirect(
  searchParams: URLSearchParams,
  location?: Pick<Location, "state">,
): string {
  const redirect = searchParams.get("redirect");
  if (isSafeRedirect(redirect)) {
    return redirect;
  }

  const from = location?.state as { from?: { pathname: string; search?: string } } | null;
  if (from?.from?.pathname && isSafeRedirect(from.from.pathname)) {
    return `${from.from.pathname}${from.from.search ?? ""}`;
  }

  return "/mesas";
}

function isSafeRedirect(path: string | null | undefined): path is string {
  return Boolean(path && path.startsWith("/") && !path.startsWith("//"));
}
