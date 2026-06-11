import type { FormEvent } from "react";
import { useState } from "react";
import { Link, useNavigate, useOutletContext } from "react-router-dom";
import type { MesaContext } from "../../components/layout/MesaLayout";
import { VISIBILITY_LABELS, SHEET_VISIBILITY_OPTIONS } from "../../lib/labels";
import { useCharacters, useCreateCharacter, useTemplates } from "../../lib/queries";
import { LoadingSpinner } from "../../components/common/LoadingSpinner";
import { ErrorAlert } from "../../components/common/ErrorAlert";
import { Button } from "../../components/common/Button";

export function CharacterListPage() {
  const { mesa } = useOutletContext<MesaContext>();
  const { data: characters, isLoading, error } = useCharacters(mesa.id);

  if (isLoading) return <LoadingSpinner />;
  if (error) return <ErrorAlert message="Erro ao carregar personagens." />;

  return (
    <div>
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-lg font-semibold">Personagens</h2>
        <Link to={`/mesas/${mesa.id}/characters/new`}>
          <Button>Novo personagem</Button>
        </Link>
      </div>

      {characters?.length === 0 ? (
        <p className="text-slate-400">Nenhum personagem criado ainda.</p>
      ) : (
        <ul className="divide-y divide-slate-800 rounded-lg border border-slate-800">
          {characters?.map((c) => (
            <li key={c.id}>
              <Link
                to={`/mesas/${mesa.id}/characters/${c.id}`}
                className="flex items-center justify-between px-4 py-3 hover:bg-slate-900/50"
              >
                <span className="font-medium">{c.character_name}</span>
                <span className="text-xs text-slate-500">
                  {VISIBILITY_LABELS[c.visibility] ?? c.visibility}
                </span>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export function CharacterCreatePage() {
  const { mesa } = useOutletContext<MesaContext>();
  const navigate = useNavigate();
  const { data: templates, isLoading } = useTemplates(mesa.id);
  const createCharacter = useCreateCharacter(mesa.id);
  const [templateId, setTemplateId] = useState("");
  const [name, setName] = useState("");
  const [visibility, setVisibility] = useState("owner_only");

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    const created = await createCharacter.mutateAsync({
      template_id: templateId,
      character_name: name,
      visibility,
    });
    navigate(`/mesas/${mesa.id}/characters/${created.id}`);
  };

  if (isLoading) return <LoadingSpinner />;

  return (
    <div className="max-w-md">
      <h2 className="text-lg font-semibold mb-4">Novo personagem</h2>
      {!templates?.length ? (
        <ErrorAlert message="Nenhum template disponível. Conclua a importação primeiro." />
      ) : (
        <form onSubmit={(e) => void handleSubmit(e)} className="space-y-4">
          <div>
            <label className="block text-sm mb-1">Template</label>
            <select
              className="w-full"
              value={templateId}
              onChange={(e) => setTemplateId(e.target.value)}
              required
            >
              <option value="">Selecione…</option>
              {templates.map((t) => (
                <option key={t.id} value={t.id}>{t.name}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm mb-1">Nome do personagem</label>
            <input className="w-full" value={name} onChange={(e) => setName(e.target.value)} required />
          </div>
          <div>
            <label className="block text-sm mb-1">Visibilidade</label>
            <select className="w-full" value={visibility} onChange={(e) => setVisibility(e.target.value)}>
              {SHEET_VISIBILITY_OPTIONS.map((o) => (
                <option key={o.value} value={o.value}>{o.label}</option>
              ))}
            </select>
          </div>
          <Button type="submit" disabled={createCharacter.isPending}>Criar</Button>
        </form>
      )}
    </div>
  );
}
