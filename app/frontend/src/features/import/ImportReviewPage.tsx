import type { ChangeEvent } from "react";
import { useMemo, useState } from "react";
import { useNavigate, useOutletContext } from "react-router-dom";
import type { MesaContext } from "../../components/layout/MesaLayout";
import { SheetForm } from "../../components/sheet/SheetForm";
import { extractProposalFields } from "../../components/sheet/sheetUtils";
import type { SheetField } from "../../types/api";
import { IMPORT_STATUS_LABELS } from "../../lib/labels";
import {
  useApproveImport,
  useImportJob,
  useRejectImport,
  useSeedImport,
  useUploadImport,
} from "../../lib/queries";
import { Button } from "../../components/common/Button";
import { ErrorAlert } from "../../components/common/ErrorAlert";
import { LoadingSpinner } from "../../components/common/LoadingSpinner";
import { ApiError } from "../../lib/api";

export function ImportReviewPage() {
  const { mesa, isMaster } = useOutletContext<MesaContext>();
  const navigate = useNavigate();
  const [fileError, setFileError] = useState<string | null>(null);

  const shouldPoll = mesa.status === "importing";
  const { data: job, isLoading, isFetching } = useImportJob(mesa.id, shouldPoll);
  const upload = useUploadImport(mesa.id);
  const approve = useApproveImport(mesa.id);
  const reject = useRejectImport(mesa.id);
  const seed = useSeedImport(mesa.id);

  const proposalInfo = useMemo(() => extractProposalFields(job?.proposal ?? null), [job?.proposal]);
  const previewFields = (proposalInfo?.fields ?? []) as SheetField[];

  if (!isMaster) {
    return <ErrorAlert message="Somente o Mestre pode gerenciar a importação." />;
  }

  const handleFile = async (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setFileError(null);
    try {
      await upload.mutateAsync(file);
    } catch (err) {
      setFileError(err instanceof ApiError ? err.message : "Falha no upload.");
    }
  };

  const handleApprove = async () => {
    await approve.mutateAsync();
    navigate(`/mesas/${mesa.id}`);
  };

  const handleSeed = async () => {
    await seed.mutateAsync();
    navigate(`/mesas/${mesa.id}`);
  };

  const mutationError =
    approve.error instanceof ApiError
      ? approve.error.message
      : seed.error instanceof ApiError
        ? seed.error.message
        : null;

  return (
    <div>
      <h2 className="text-lg font-semibold mb-4">Importação de ficha</h2>

      {mesa.status !== "importing" && (
        <p className="text-sm text-slate-400 mb-4">
          Esta mesa já concluiu o bootstrap. Você pode revisar o histórico abaixo.
        </p>
      )}

      <div className="mb-6 rounded-lg border border-dashed border-slate-700 p-6">
        <label className="block text-sm font-medium mb-2">
          Enviar PDF ou imagem da ficha oficial
        </label>
        <input
          type="file"
          accept=".pdf,.png,.jpg,.jpeg,.webp,application/pdf,image/*"
          onChange={(e) => void handleFile(e)}
          disabled={upload.isPending}
        />
        {fileError && <p className="mt-2 text-sm text-red-400">{fileError}</p>}
        {upload.isPending && <p className="mt-2 text-sm text-slate-400">Enviando…</p>}
      </div>

      {isLoading ? (
        <LoadingSpinner />
      ) : !job ? (
        <p className="text-slate-400 text-sm">Nenhuma importação iniciada ainda.</p>
      ) : (
        <div className="grid gap-6 lg:grid-cols-2">
          <section className="rounded-lg border border-slate-800 p-4">
            <h3 className="font-medium mb-3">Status do agente</h3>
            <dl className="space-y-2 text-sm">
              <div className="flex justify-between">
                <dt className="text-slate-400">Status</dt>
                <dd>{IMPORT_STATUS_LABELS[job.status] ?? job.status}</dd>
              </div>
              {job.detected_system && (
                <div className="flex justify-between">
                  <dt className="text-slate-400">Sistema detectado</dt>
                  <dd>{job.detected_system}</dd>
                </div>
              )}
              {job.error_message && (
                <div>
                  <dt className="text-slate-400">Erro</dt>
                  <dd className="text-red-400">{job.error_message}</dd>
                </div>
              )}
            </dl>
            {isFetching && ["pending", "processing"].includes(job.status) && (
              <p className="mt-3 text-xs text-brand-400 animate-pulse">Aguardando proposta…</p>
            )}

            <div className="mt-6 flex flex-wrap gap-2">
              {job.status === "proposed" && (
                <>
                  <Button onClick={() => void handleApprove()} disabled={approve.isPending}>
                    Aprovar template
                  </Button>
                  <Button
                    variant="danger"
                    onClick={() => void reject.mutateAsync()}
                    disabled={reject.isPending}
                  >
                    Rejeitar
                  </Button>
                </>
              )}
              {(job.status === "failed" || job.status === "rejected" || !job.proposal) &&
                mesa.status === "importing" && (
                  <Button variant="secondary" onClick={() => void handleSeed()} disabled={seed.isPending}>
                    Usar seed D&D 5e
                  </Button>
                )}
            </div>
            {mutationError && <p className="mt-2 text-sm text-red-400">{mutationError}</p>}
          </section>

          <section className="rounded-lg border border-slate-800 p-4">
            <h3 className="font-medium mb-3">
              Prévia do template
              {proposalInfo?.name && `: ${proposalInfo.name}`}
            </h3>
            {previewFields.length > 0 ? (
              <div className="max-h-[480px] overflow-y-auto">
                <SheetForm
                  fields={previewFields}
                  values={{}}
                  onChange={() => {}}
                  readOnly
                />
              </div>
            ) : (
              <p className="text-sm text-slate-500">
                A prévia aparecerá quando o agente enviar a proposta.
              </p>
            )}
          </section>
        </div>
      )}
    </div>
  );
}
