import { useEffect, useState } from "react";
import { useOutletContext, useParams } from "react-router-dom";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import type { MesaContext } from "../../components/layout/MesaLayout";
import { VISIBILITY_LABELS } from "../../lib/labels";
import {
  useDocument,
  useDocumentContent,
  useSaveDocumentContent,
} from "../../lib/queries";
import { LoadingSpinner } from "../../components/common/LoadingSpinner";
import { ErrorAlert } from "../../components/common/ErrorAlert";
import { Button } from "../../components/common/Button";

function extractMarkdownBody(content: unknown): string {
  if (!content) return "";
  if (typeof content === "object" && content !== null) {
    const obj = content as { format?: string; body?: string; payload?: { body?: string } };
    if (obj.format === "markdown" && typeof obj.body === "string") return obj.body;
    if (typeof obj.body === "string") return obj.body;
  }
  return "";
}

export function DocumentEditorPage() {
  const { mesa, isMaster } = useOutletContext<MesaContext>();
  const { documentId = "" } = useParams();
  const { data: doc, isLoading: docLoading, error } = useDocument(mesa.id, documentId);
  const { data: content, isLoading: contentLoading } = useDocumentContent(mesa.id, documentId);
  const saveContent = useSaveDocumentContent(mesa.id, documentId);

  const [body, setBody] = useState("");
  const [editing, setEditing] = useState(false);
  const [dirty, setDirty] = useState(false);

  useEffect(() => {
    setBody(extractMarkdownBody(content));
    setDirty(false);
  }, [content]);

  if (docLoading || contentLoading) return <LoadingSpinner />;
  if (error || !doc) return <ErrorAlert message="Documento não encontrado ou sem permissão." />;

  const canEdit = isMaster;

  const handleSave = async () => {
    await saveContent.mutateAsync(body);
    setDirty(false);
    setEditing(false);
  };

  return (
    <div>
      <div className="mb-4 flex flex-wrap items-start justify-between gap-3">
        <div>
          <h2 className="text-lg font-semibold">{doc.title}</h2>
          <p className="text-sm text-slate-500">
            {VISIBILITY_LABELS[doc.visibility] ?? doc.visibility} · v{doc.version}
          </p>
        </div>
        {canEdit && (
          <div className="flex gap-2">
            {editing ? (
              <>
                <Button onClick={() => void handleSave()} disabled={!dirty || saveContent.isPending}>
                  Salvar
                </Button>
                <Button variant="secondary" onClick={() => { setEditing(false); setBody(extractMarkdownBody(content)); }}>
                  Cancelar
                </Button>
              </>
            ) : (
              <Button variant="secondary" onClick={() => setEditing(true)}>Editar</Button>
            )}
          </div>
        )}
      </div>

      {editing ? (
        <textarea
          className="w-full min-h-[400px] font-mono text-sm"
          value={body}
          onChange={(e) => { setBody(e.target.value); setDirty(true); }}
        />
      ) : (
        <article className="markdown-body space-y-3 text-slate-300 [&_h1]:text-xl [&_h2]:text-lg [&_h3]:text-base [&_h1]:font-bold [&_h2]:font-semibold [&_ul]:list-disc [&_ul]:pl-5">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{body || "*Documento vazio.*"}</ReactMarkdown>
        </article>
      )}
    </div>
  );
}
