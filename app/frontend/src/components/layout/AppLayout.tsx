import { Link, NavLink, Outlet } from "react-router-dom";
import { useAuth } from "../../lib/auth";
import { Button } from "../common/Button";

export function AppLayout() {
  const { user, signOut } = useAuth();

  return (
    <div className="min-h-screen flex flex-col">
      <header className="border-b border-slate-800 bg-slate-900/80 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
          <Link to="/mesas" className="text-lg font-bold text-brand-100">
            RPG Platform
          </Link>
          <nav className="flex items-center gap-4 text-sm">
            <NavLink
              to="/mesas"
              className={({ isActive }) =>
                isActive ? "text-brand-400" : "text-slate-400 hover:text-slate-200"
              }
            >
              Mesas
            </NavLink>
            <NavLink
              to="/profile"
              className={({ isActive }) =>
                isActive ? "text-brand-400" : "text-slate-400 hover:text-slate-200"
              }
            >
              Perfil
            </NavLink>
            {user?.is_admin && (
              <NavLink
                to="/admin"
                className={({ isActive }) =>
                  isActive ? "text-brand-400" : "text-slate-400 hover:text-slate-200"
                }
              >
                Admin
              </NavLink>
            )}
            <Link to="/mesas/new">
              <Button variant="secondary" className="py-1.5 px-3 text-xs">
                Nova Mesa
              </Button>
            </Link>
            <span className="text-slate-500">{user?.display_name || user?.email}</span>
            <Button variant="ghost" onClick={() => void signOut()}>
              Sair
            </Button>
          </nav>
        </div>
      </header>
      <main className="flex-1 mx-auto w-full max-w-6xl px-4 py-6">
        <Outlet />
      </main>
    </div>
  );
}
