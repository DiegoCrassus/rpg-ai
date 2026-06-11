import type { FormEvent } from "react";
import { useState } from "react";
import { Link, useNavigate, useOutletContext } from "react-router-dom";
import type { MesaContext } from "../../components/layout/MesaLayout";
import {
  DOCUMENT_TYPE_OPTIONS,
  DOCUMENT_VISIBILITY_OPTIONS,
  VISIBILITY_LABELS,
} from "../../lib/labels";
import { useCreateDocument, useDocuments } from "../../lib/queries";
import { LoadingSpinner } from "../../components/common/LoadingSpinner";
import { ErrorAlert } from "../../components/common/ErrorAlert";
import { Button } from "../../components/common/Button";

export function DocumentListPage() {
  const { mesa, isMaster } = useOutletContext<MesaContext>();
  const [search, setSearch] = useState("");
  const [query, setQuery] = useState("");
  const { data: documents, isLoading, error } = useDocuments(mesa.id, query);

  if (isLoading) return <LoadingSpinner />;
  if (error) return <ErrorAlert message="Erro ao carregar documentos." />;

  return (
    <div>
      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <h2 className="text-lg font-semibold">Documentos</h2>
        {isMaster && (
          <Link to={`/mesas/${mesa.id}/documents/new`}>
            <Button>Novo documento</Button>
          </Link>
        )}
      </div>

      <form
        className="mb-4 flex gap-2"
        onSubmit={(e) => {
          e.preventDefault();
          setQuery(search);
        }}
      >
        <input
          className="flex-1"
          placeholder="Buscar por título ou conteúdo…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <Button type="submit" variant="secondary">Buscar</Button>
      </form>

      {documents?.length === 0 ? (
        <p className="text-slate-400">Nenhum documento visível para você.</p>
      ) : (
        <ul className="divide-y divide-slate-800 rounded-lg border border-slate-800">
          {documents?.map((doc) => (
            <li key={doc.id}>
              <Link
                to={`/mesas/${mesa.id}/documents/${doc.id}`}
                className="block px-4 py-3 hover:bg-slate-900/50"
              >
                <div className="flex items-center justify-between">
                  <span className="font-medium">{doc.title}</span>
                  <span className="text-xs text-slate-500">
                    {VISIBILITY_LABELS[doc.visibility] ?? doc.visibility}
                  </span>
                </div>
                {doc.tags.length > 0 && (
                  <div className="mt-1 flex gap-1">
                    {doc.tags.map((tag) => (
                      <span key={tag} className="rounded bg-slate-800 px-1.5 text-xs text-slate-400">
                        {tag}
                      </span>
                    ))}
                  </div>
                )}
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export function DocumentCreatePage() {
  const { mesa } = useOutletContext<MesaContext>();
  const navigate = useNavigate();
  const createDoc = useCreateDocument(mesa.id);
  const [title, setTitle] = useState("");
  const [type, setType] = useState("session");
  const [visibility, setVisibility] = useState("all_players");
  const [tags, setTags] = useState("");
  const [content, setContent] = useState("");

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    const doc = await createDoc.mutateAsync({
      title,
      type,
      visibility,
      tags: tags.split(",").map((t) => t.trim()).filter(Boolean),
      initial_content: content,
    });
    navigate(`/mesas/${mesa.id}/documents/${doc.id}`);
  };

  return (
    <div className="max-w-2xl">
      <h2 className="text-lg font-semibold mb-4">Novo documento</h2>
      <form onSubmit={(e) => void handleSubmit(e)} className="space-y-4">
        <div>
          <label className="block text-sm mb-1">Título</label>
          <input className="w-full" value={title} onChange={(e) => setTitle(e.target.value)} required />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm mb-1">Tipo</label>
            <select className="w-full" value={type} onChange={(e) => setType(e.target.value)}>
              {DOCUMENT_TYPE_OPTIONS.map((o) => (
                <option key={o.value} value={o.value}>{o.label}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm mb-1">Visibilidade</label>
            <select className="w-full" value={visibility} onChange={(e) => setVisibility(e.target.value)}>
              {DOCUMENT_VISIBILITY_OPTIONS.map((o) => (
                <option key={o.value} value={o.value}>{o.label}</option>
              ))}
            </select>
          </div>
        </div>
        <div>
          <label className="block text-sm mb-1">Tags (separadas por vírgula)</label>
          <input className="w-full" value={tags} onChange={(e) => setTags(e.target.value)} placeholder="npc, sessão-1" />
        </div>
        <div>
          <label className="block text-sm mb-1">Conteúdo inicial (Markdown)</label>
          <textarea
            className="w-full min-h-[200px] font-mono text-sm"
            value={content}
            onChange={(e) => setContent(e.target.value)}
          />
        </div>
        <Button type="submit" disabled={createDoc.isPending}>Criar</Button>
      </form>
    </div>
  );
}
