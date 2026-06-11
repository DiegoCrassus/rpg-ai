import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch, apiUpload, ApiError } from "../lib/api";
import type {
  AdminMesa,
  AdminUser,
  AuditEvent,
  Character,
  ContractEnvelope,
  CharacterSheetPayload,
  Document,
  ImportJob,
  Invite,
  Mesa,
  Participant,
  SheetTemplatePayload,
  Template,
  User,
} from "../types/api";

export function useMesas() {
  return useQuery({
    queryKey: ["mesas"],
    queryFn: () => apiFetch<Mesa[]>("/api/v1/mesas"),
  });
}

export function useMesa(mesaId: string) {
  return useQuery({
    queryKey: ["mesa", mesaId],
    queryFn: () => apiFetch<Mesa>(`/api/v1/mesas/${mesaId}`),
    enabled: Boolean(mesaId),
  });
}

export function useCreateMesa() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (body: { name: string; rpg_system: string; description?: string }) =>
      apiFetch<Mesa>("/api/v1/mesas", { method: "POST", body: JSON.stringify(body) }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["mesas"] }),
  });
}

export function useImportJob(mesaId: string, poll = false) {
  return useQuery({
    queryKey: ["import", mesaId],
    queryFn: async () => {
      try {
        return await apiFetch<ImportJob>(`/api/v1/mesas/${mesaId}/import`);
      } catch (err) {
        if (err instanceof ApiError && err.status === 404) return null;
        throw err;
      }
    },
    enabled: Boolean(mesaId),
    refetchInterval: (query) => {
      if (!poll) return false;
      const status = query.state.data?.status;
      if (!status) return 2000;
      return ["pending", "processing"].includes(status) ? 2000 : false;
    },
    retry: false,
  });
}

export function useUploadImport(mesaId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (file: File) =>
      apiUpload<ImportJob>(`/api/v1/mesas/${mesaId}/import`, file),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["import", mesaId] }),
  });
}

export function useApproveImport(mesaId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: () =>
      apiFetch<{ template_id: string; mesa_status: string }>(
        `/api/v1/mesas/${mesaId}/import/approve`,
        { method: "POST" },
      ),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["import", mesaId] });
      qc.invalidateQueries({ queryKey: ["mesa", mesaId] });
      qc.invalidateQueries({ queryKey: ["templates", mesaId] });
    },
  });
}

export function useRejectImport(mesaId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: () =>
      apiFetch<ImportJob>(`/api/v1/mesas/${mesaId}/import/reject`, { method: "POST" }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["import", mesaId] }),
  });
}

export function useSeedImport(mesaId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: () =>
      apiFetch<{ template_id: string; mesa_status: string }>(
        `/api/v1/mesas/${mesaId}/import/seed`,
        { method: "POST" },
      ),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["import", mesaId] });
      qc.invalidateQueries({ queryKey: ["mesa", mesaId] });
      qc.invalidateQueries({ queryKey: ["templates", mesaId] });
    },
  });
}

export function useTemplates(mesaId: string) {
  return useQuery({
    queryKey: ["templates", mesaId],
    queryFn: () => apiFetch<Template[]>(`/api/v1/mesas/${mesaId}/templates`),
    enabled: Boolean(mesaId),
  });
}

export function useTemplateSchema(mesaId: string, templateId: string) {
  return useQuery({
    queryKey: ["template-schema", mesaId, templateId],
    queryFn: () =>
      apiFetch<ContractEnvelope<SheetTemplatePayload>>(
        `/api/v1/mesas/${mesaId}/templates/${templateId}/schema`,
      ),
    enabled: Boolean(mesaId && templateId),
  });
}

export function useCharacters(mesaId: string) {
  return useQuery({
    queryKey: ["characters", mesaId],
    queryFn: () => apiFetch<Character[]>(`/api/v1/mesas/${mesaId}/characters`),
    enabled: Boolean(mesaId),
  });
}

export function useCharacter(mesaId: string, characterId: string) {
  return useQuery({
    queryKey: ["character", mesaId, characterId],
    queryFn: () =>
      apiFetch<Character>(`/api/v1/mesas/${mesaId}/characters/${characterId}`),
    enabled: Boolean(mesaId && characterId),
  });
}

export function useCharacterData(mesaId: string, characterId: string) {
  return useQuery({
    queryKey: ["character-data", mesaId, characterId],
    queryFn: () =>
      apiFetch<ContractEnvelope<CharacterSheetPayload>>(
        `/api/v1/mesas/${mesaId}/characters/${characterId}/data`,
      ),
    enabled: Boolean(mesaId && characterId),
  });
}

export function useCreateCharacter(mesaId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (body: {
      template_id: string;
      character_name: string;
      visibility?: string;
      initial_values?: Record<string, unknown>;
    }) =>
      apiFetch<Character>(`/api/v1/mesas/${mesaId}/characters`, {
        method: "POST",
        body: JSON.stringify(body),
      }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["characters", mesaId] }),
  });
}

export function useSaveCharacterData(mesaId: string, characterId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (values: Record<string, unknown>) =>
      apiFetch<Character>(`/api/v1/mesas/${mesaId}/characters/${characterId}/data`, {
        method: "PUT",
        body: JSON.stringify({ values }),
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["character-data", mesaId, characterId] });
      qc.invalidateQueries({ queryKey: ["character", mesaId, characterId] });
    },
  });
}

export function useDocuments(mesaId: string, search?: string) {
  return useQuery({
    queryKey: ["documents", mesaId, search ?? ""],
    queryFn: () => {
      const params = search ? `?q=${encodeURIComponent(search)}` : "";
      return apiFetch<Document[]>(`/api/v1/mesas/${mesaId}/documents${params}`);
    },
    enabled: Boolean(mesaId),
  });
}

export function useDocument(mesaId: string, documentId: string) {
  return useQuery({
    queryKey: ["document", mesaId, documentId],
    queryFn: () =>
      apiFetch<Document>(`/api/v1/mesas/${mesaId}/documents/${documentId}`),
    enabled: Boolean(mesaId && documentId),
  });
}

export function useDocumentContent(mesaId: string, documentId: string) {
  return useQuery({
    queryKey: ["document-content", mesaId, documentId],
    queryFn: () =>
      apiFetch<{ format?: string; body?: string } | Record<string, unknown>>(
        `/api/v1/mesas/${mesaId}/documents/${documentId}/content`,
      ),
    enabled: Boolean(mesaId && documentId),
  });
}

export function useCreateDocument(mesaId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (body: {
      title: string;
      type: string;
      visibility: string;
      content_format?: string;
      tags?: string[];
      initial_content?: string;
    }) =>
      apiFetch<Document>(`/api/v1/mesas/${mesaId}/documents`, {
        method: "POST",
        body: JSON.stringify(body),
      }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["documents", mesaId] }),
  });
}

export function useSaveDocumentContent(mesaId: string, documentId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (content: string) =>
      apiFetch(`/api/v1/mesas/${mesaId}/documents/${documentId}/content`, {
        method: "PUT",
        body: JSON.stringify({ content }),
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["document-content", mesaId, documentId] });
      qc.invalidateQueries({ queryKey: ["document", mesaId, documentId] });
    },
  });
}

export function useParticipants(mesaId: string) {
  return useQuery({
    queryKey: ["participants", mesaId],
    queryFn: () =>
      apiFetch<Participant[]>(`/api/v1/mesas/${mesaId}/participants`),
    enabled: Boolean(mesaId),
  });
}

export function useInvites(mesaId: string) {
  return useQuery({
    queryKey: ["invites", mesaId],
    queryFn: () => apiFetch<Invite[]>(`/api/v1/mesas/${mesaId}/invites`),
    enabled: Boolean(mesaId),
  });
}

export function useCreateInvite(mesaId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (email: string) =>
      apiFetch<Invite>(`/api/v1/mesas/${mesaId}/invites`, {
        method: "POST",
        body: JSON.stringify({ email }),
      }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["invites", mesaId] }),
  });
}

export function useAcceptInvite() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (token: string) =>
      apiFetch<{ mesa_id: string; participant_id: string; role: string }>(
        "/api/v1/invites/accept",
        { method: "POST", body: JSON.stringify({ token }) },
      ),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["mesas"] }),
  });
}

export function useAdminUsers() {
  return useQuery({
    queryKey: ["admin-users"],
    queryFn: () => apiFetch<AdminUser[]>("/api/v1/admin/users"),
  });
}

export function useAdminMesas() {
  return useQuery({
    queryKey: ["admin-mesas"],
    queryFn: () => apiFetch<AdminMesa[]>("/api/v1/admin/mesas"),
  });
}

export function useAdminAuditEvents() {
  return useQuery({
    queryKey: ["admin-audit"],
    queryFn: () => apiFetch<AuditEvent[]>("/api/v1/admin/audit-events"),
  });
}

export function useSuspendUser() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ userId, status }: { userId: string; status: string }) =>
      apiFetch<User>(`/api/v1/admin/users/${userId}/status`, {
        method: "PATCH",
        body: JSON.stringify({ status }),
      }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["admin-users"] }),
  });
}

export function useUpdateProfile() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (display_name: string) =>
      apiFetch<User>("/api/v1/users/me", {
        method: "PATCH",
        body: JSON.stringify({ display_name }),
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["profile"] });
    },
  });
}

export function useProfile() {
  return useQuery({
    queryKey: ["profile"],
    queryFn: () => apiFetch<User>("/api/v1/users/me"),
  });
}

export function useUploadAvatar() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (file: File) => apiUpload<{ signed_url: string }>("/api/v1/users/me/avatar", file),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["profile"] });
    },
  });
}

export interface MediaUploadResult {
  storage_path: string;
  signed_url: string;
}

export function useUploadCharacterMedia(mesaId: string, characterId: string) {
  return useMutation({
    mutationFn: ({ fieldKey, file }: { fieldKey: string; file: File }) =>
      apiUpload<MediaUploadResult>(
        `/api/v1/mesas/${mesaId}/characters/${characterId}/media`,
        file,
        "file",
        { field_key: fieldKey },
      ),
  });
}
