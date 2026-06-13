import type { FormEvent } from "react";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useCreateMesa } from "../../lib/queries";
import { apiFetch, apiUpload, ApiError } from "../../lib/api";
import { Button } from "../../components/common/Button";
import { ErrorAlert } from "../../components/common/ErrorAlert";
import { FileDropzone } from "../../components/common/FileDropzone";
import {
  DEFAULT_RPG_SYSTEM_ID,
  RPG_SYSTEM_PRESETS,
} from "./rpgSystems";
import {
  needsImportFile,
  resolveRpgSystem,
  validateCreateForm,
} from "./mesaUtils";

type SubmitPhase = "idle" | "creating" | "seeding" | "uploading";

export function MesaCreatePage() {
  const navigate = useNavigate();
  const createMesa = useCreateMesa();

  const [name, setName] = useState("");
  const [systemId, setSystemId] = useState(DEFAULT_RPG_SYSTEM_ID);
  const [customSystem, setCustomSystem] = useState("");
  const [description, setDescription] = useState("");
  const [usePlatformTemplate, setUsePlatformTemplate] = useState(true);
  const [file, setFile] = useState<File | null>(null);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [phase, setPhase] = useState<SubmitPhase>("idle");

  const showCustomSystem = systemId === "custom";
  const showPlatformTemplateOption = systemId === "dnd5e";
  const showFileUpload = needsImportFile(
    systemId,
    showPlatformTemplateOption ? usePlatformTemplate : false,
  );

  const isBusy = phase !== "idle" || createMesa.isPending;

  const handleSystemChange = (nextId: string) => {
    setSystemId(nextId);
    if (nextId === "dnd5e") {
      setUsePlatformTemplate(true);
    } else {
      setUsePlatformTemplate(false);
    }
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setSubmitError(null);

    const validation = validateCreateForm({
      name,
      systemId,
      customSystemText: customSystem,
      usePlatformTemplate: showPlatformTemplateOption && usePlatformTemplate,
      file,
    });

    if (!validation.valid) {
      setFieldErrors(validation.errors);
      return;
    }

    setFieldErrors({});
    const rpgSystem = resolveRpgSystem(systemId, customSystem);
    const useTemplate = showPlatformTemplateOption && usePlatformTemplate;

    try {
      setPhase("creating");
      const mesa = await createMesa.mutateAsync({
        name: name.trim(),
        rpg_system: rpgSystem,
        description: description.trim() || undefined,
      });

      if (useTemplate) {
        setPhase("seeding");
        await apiFetch(`/api/v1/mesas/${mesa.id}/import/seed`, { method: "POST" });
        navigate(`/mesas/${mesa.id}`);
        return;
      }

      setPhase("uploading");
      await apiUpload(`/api/v1/mesas/${mesa.id}/import`, file!);
      navigate(`/mesas/${mesa.id}/import`);
    } catch (err) {
      setSubmitError(
        err instanceof ApiError ? err.message : "Erro ao criar mesa. Tente novamente.",
      );
    } finally {
      setPhase("idle");
    }
  };

  const submitLabel =
    phase === "creating"
      ? "Criando mesa…"
      : phase === "seeding"
        ? "Aplicando template…"
        : phase === "uploading"
          ? "Enviando ficha…"
          : "Criar mesa";

  return (
    <div className="mx-auto max-w-lg">
      <h1 className="mb-6 text-2xl font-bold">Nova Mesa</h1>

      {submitError && (
        <div className="mb-4">
          <ErrorAlert message={submitError} />
        </div>
      )}

      <form onSubmit={(e) => void handleSubmit(e)} className="space-y-4">
        <div>
          <label htmlFor="mesa-name" className="mb-1 block text-sm">
            Nome da campanha
          </label>
          <input
            id="mesa-name"
            className="w-full"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Curse of Strahd"
            required
            disabled={isBusy}
          />
          {fieldErrors.name && (
            <p className="mt-1 text-sm text-red-400">{fieldErrors.name}</p>
          )}
        </div>

        <div>
          <label htmlFor="mesa-system" className="mb-1 block text-sm">
            Sistema de RPG
          </label>
          <select
            id="mesa-system"
            className="w-full"
            value={systemId}
            onChange={(e) => handleSystemChange(e.target.value)}
            disabled={isBusy}
          >
            {RPG_SYSTEM_PRESETS.map((preset) => (
              <option key={preset.id} value={preset.id}>
                {preset.label}
              </option>
            ))}
          </select>
          {fieldErrors.system && (
            <p className="mt-1 text-sm text-red-400">{fieldErrors.system}</p>
          )}
        </div>

        {showCustomSystem && (
          <div>
            <label htmlFor="mesa-custom-system" className="mb-1 block text-sm">
              Nome do sistema
            </label>
            <input
              id="mesa-custom-system"
              className="w-full"
              value={customSystem}
              onChange={(e) => setCustomSystem(e.target.value)}
              placeholder="Ex.: Tormenta 20"
              disabled={isBusy}
            />
          </div>
        )}

        <div>
          <label htmlFor="mesa-description" className="mb-1 block text-sm">
            Descrição (opcional)
          </label>
          <textarea
            id="mesa-description"
            className="min-h-[80px] w-full"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            disabled={isBusy}
          />
        </div>

        {showPlatformTemplateOption && (
          <label className="flex items-start gap-2 text-sm">
            <input
              type="checkbox"
              className="mt-1"
              checked={usePlatformTemplate}
              onChange={(e) => setUsePlatformTemplate(e.target.checked)}
              disabled={isBusy}
            />
            <span>
              Usar template oficial da plataforma (sem upload)
            </span>
          </label>
        )}

        {showFileUpload && (
          <div className="space-y-2">
            <p className="text-sm text-amber-300/90">
              Envio da ficha oficial é obrigatório para importação pelo agente.
            </p>
            <FileDropzone
              file={file}
              onFile={setFile}
              required
              error={fieldErrors.file}
              disabled={isBusy}
            />
          </div>
        )}

        <div className="flex flex-col gap-3">
          <Button type="submit" disabled={isBusy}>
            {submitLabel}
          </Button>
          <Button
            type="button"
            variant="secondary"
            disabled={isBusy}
            onClick={() => navigate("/mesas")}
          >
            Cancelar
          </Button>
        </div>
      </form>
    </div>
  );
}
