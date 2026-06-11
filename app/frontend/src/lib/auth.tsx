import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import type { Session } from "@supabase/supabase-js";
import type { User } from "../types/api";
import { apiFetch } from "./api";
import { supabase } from "./supabase";

interface AuthContextValue {
  session: Session | null;
  user: User | null;
  loading: boolean;
  signOut: () => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<Session | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  const syncUser = useCallback(async () => {
    try {
      const profile = await apiFetch<User>("/api/v1/auth/sync", { method: "POST" });
      setUser(profile);
    } catch {
      setUser(null);
    }
  }, []);

  const refreshUser = useCallback(async () => {
    if (!session) {
      setUser(null);
      return;
    }
    try {
      const profile = await apiFetch<User>("/api/v1/auth/me");
      setUser(profile);
    } catch {
      await syncUser();
    }
  }, [session, syncUser]);

  useEffect(() => {
    supabase.auth.getSession().then(({ data }) => {
      setSession(data.session);
      setLoading(false);
    });

    const { data: sub } = supabase.auth.onAuthStateChange((_event, next) => {
      setSession(next);
    });

    return () => sub.subscription.unsubscribe();
  }, []);

  useEffect(() => {
    if (session) {
      void syncUser();
    } else {
      setUser(null);
    }
  }, [session, syncUser]);

  const signOut = useCallback(async () => {
    await supabase.auth.signOut();
    setUser(null);
  }, []);

  const value = useMemo(
    () => ({ session, user, loading, signOut, refreshUser }),
    [session, user, loading, signOut, refreshUser],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return ctx;
}
