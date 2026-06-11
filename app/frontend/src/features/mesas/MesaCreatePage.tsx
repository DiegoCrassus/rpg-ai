import type { FormEvent } from "react";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useCreateMesa } from "../../lib/queries";
import { Button } from "../../components/common/Button";
import { ErrorAlert } from "../../components/common/ErrorAlert";
import { ApiError } from "../../lib/api";

export function MesaCreatePage() {
  const navigate = useNavigate();
  const createMesa = useCreateMesa();
  const [name, setName] = useState("");
  const [rpgSystem, setRpgSystem] = useState("D&D 5e");
  const [description, setDescription] = useState("");

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    try {
      const mesa = await createMesa.mutateAsync({
        name,
        rpg_system: rpgSystem,
        description: description || undefined,
      });
      navigate(`/mesas/${mesa.id}/import`);
    } catch (err) {
      /* handled via mutation error */
    }
  };

  const errorMsg =
    createMesa.error instanceof ApiError
      ? createMesa.error.message
      : createMesa.error
        ? "Erro ao criar mesa."
        : null;

  return (
    <div className="mx-auto max-w-lg">
      <h1 className="mb-6 text-2xl font-bold">Nova Mesa</h1>
      {errorMsg && <div className="mb-4"><ErrorAlert message={errorMsg} /></div>}
      <form onSubmit={(e) => void handleSubmit(e)} className="space-y-4">
        <div>
          <label className="block text-sm mb-1">Nome da campanha</label>
          <input
            className="w-full"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Curse of Strahd"
            required
          />
        </div>
        <div>
          <label className="block text-sm mb-1">Sistema de RPG</label>
          <input
            className="w-full"
            value={rpgSystem}
            onChange={(e) => setRpgSystem(e.target.value)}
            required
          />
        </div>
        <div>
          <label className="block text-sm mb-1">Descrição (opcional)</label>
          <textarea
            className="w-full min-h-[80px]"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />
        </div>
        <div className="flex gap-3">
          <Button type="submit" disabled={createMesa.isPending}>
            {createMesa.isPending ? "Criando…" : "Criar e importar ficha"}
          </Button>
          <Button type="button" variant="secondary" onClick={() => navigate("/mesas")}>
            Cancelar
          </Button>
        </div>
      </form>
    </div>
  );
}
