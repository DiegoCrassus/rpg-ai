import type { FormEvent } from "react";
import { useEffect, useRef, useState } from "react";
import { useAuth } from "../../lib/auth";
import { useProfile, useUpdateProfile, useUploadAvatar } from "../../lib/queries";
import { Button } from "../../components/common/Button";
import { ErrorAlert } from "../../components/common/ErrorAlert";
import { LoadingSpinner } from "../../components/common/LoadingSpinner";

export function ProfileSettingsPage() {
  const { refreshUser } = useAuth();
  const { data: profile, isLoading, error } = useProfile();
  const updateProfile = useUpdateProfile();
  const uploadAvatar = useUploadAvatar();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [displayName, setDisplayName] = useState("");
  const [saved, setSaved] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  useEffect(() => {
    if (profile?.display_name) {
      setDisplayName(profile.display_name);
    }
  }, [profile?.display_name]);

  if (isLoading) return <LoadingSpinner />;
  if (error || !profile) return <ErrorAlert message="Não foi possível carregar o perfil." />;

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setFormError(null);
    setSaved(false);
    try {
      await updateProfile.mutateAsync(displayName.trim());
      await refreshUser();
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } catch (err) {
      setFormError(err instanceof Error ? err.message : "Erro ao salvar perfil.");
    }
  };

  const handleAvatarChange = async (file: File | undefined) => {
    if (!file) return;
    setFormError(null);
    try {
      await uploadAvatar.mutateAsync(file);
      await refreshUser();
    } catch (err) {
      setFormError(err instanceof Error ? err.message : "Erro ao enviar avatar.");
    }
  };

  return (
    <div className="mx-auto max-w-lg">
      <h1 className="mb-6 text-2xl font-bold">Meu perfil</h1>
      {formError && (
        <div className="mb-4">
          <ErrorAlert message={formError} />
        </div>
      )}

      <div className="mb-8 flex items-center gap-4">
        <div className="flex h-20 w-20 items-center justify-center overflow-hidden rounded-full border border-slate-700 bg-slate-800">
          {profile.avatar_url ? (
            <img src={profile.avatar_url} alt="Avatar" className="h-full w-full object-cover" />
          ) : (
            <span className="text-2xl text-slate-500">
              {(profile.display_name || profile.email).charAt(0).toUpperCase()}
            </span>
          )}
        </div>
        <div>
          <input
            ref={fileInputRef}
            type="file"
            accept="image/png,image/jpeg,image/webp"
            className="hidden"
            onChange={(e) => void handleAvatarChange(e.target.files?.[0])}
          />
          <Button
            type="button"
            variant="secondary"
            disabled={uploadAvatar.isPending}
            onClick={() => fileInputRef.current?.click()}
          >
            {uploadAvatar.isPending ? "Enviando…" : "Alterar avatar"}
          </Button>
          <p className="mt-1 text-xs text-slate-500">PNG, JPG ou WebP</p>
        </div>
      </div>

      <form onSubmit={(e) => void handleSubmit(e)} className="space-y-4">
        <div>
          <label className="mb-1 block text-sm">E-mail</label>
          <input type="email" className="w-full opacity-60" value={profile.email} disabled />
        </div>
        <div>
          <label className="mb-1 block text-sm">Nome de exibição</label>
          <input
            type="text"
            className="w-full"
            value={displayName}
            maxLength={120}
            required
            onChange={(e) => setDisplayName(e.target.value)}
          />
        </div>
        <div className="flex items-center gap-3">
          <Button type="submit" disabled={updateProfile.isPending}>
            {updateProfile.isPending ? "Salvando…" : "Salvar"}
          </Button>
          {saved && <span className="text-sm text-green-400">Salvo!</span>}
        </div>
      </form>
    </div>
  );
}
