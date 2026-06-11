import { useCallback, useEffect, useState } from "react";
import { useOutletContext, useParams } from "react-router-dom";
import type { MesaContext } from "../../components/layout/MesaLayout";
import { SheetForm } from "../../components/sheet/SheetForm";
import type { SheetField } from "../../types/api";
import { useAuth } from "../../lib/auth";
import {
  useCharacter,
  useCharacterData,
  useSaveCharacterData,
  useTemplateSchema,
  useUploadCharacterMedia,
} from "../../lib/queries";
import { LoadingSpinner } from "../../components/common/LoadingSpinner";
import { ErrorAlert } from "../../components/common/ErrorAlert";
import { Button } from "../../components/common/Button";

export function CharacterEditorPage() {
  const { mesa, isMaster } = useOutletContext<MesaContext>();
  const { user } = useAuth();
  const { characterId = "" } = useParams();
  const { data: character, isLoading: charLoading } = useCharacter(mesa.id, characterId);
  const { data: sheetData, isLoading: dataLoading } = useCharacterData(mesa.id, characterId);
  const { data: schemaEnvelope, isLoading: schemaLoading } = useTemplateSchema(
    mesa.id,
    character?.template_id ?? "",
  );
  const saveData = useSaveCharacterData(mesa.id, characterId);
  const uploadMedia = useUploadCharacterMedia(mesa.id, characterId);

  const [values, setValues] = useState<Record<string, unknown>>({});
  const [mediaPreviewUrls, setMediaPreviewUrls] = useState<Record<string, string>>({});
  const [dirty, setDirty] = useState(false);
  const [saved, setSaved] = useState(false);

  const handleMediaUpload = useCallback(
    async (fieldKey: string, file: File) => {
      const result = await uploadMedia.mutateAsync({ fieldKey, file });
      setDirty(true);
      return result;
    },
    [uploadMedia],
  );

  const handlePreviewUrl = useCallback((path: string, url: string) => {
    setMediaPreviewUrls((prev) => ({ ...prev, [path]: url }));
  }, []);

  useEffect(() => {
    if (sheetData?.payload?.values) {
      setValues(sheetData.payload.values as Record<string, unknown>);
      setDirty(false);
    }
  }, [sheetData]);

  const fields = (schemaEnvelope?.payload?.fields ?? []) as SheetField[];
  const canEdit = isMaster || character?.owner_id === user?.id;

  if (charLoading || dataLoading || schemaLoading) return <LoadingSpinner />;
  if (!character) return <ErrorAlert message="Personagem não encontrado." />;

  const handleSave = async () => {
    await saveData.mutateAsync(values);
    setDirty(false);
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <div>
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-lg font-semibold">{character.character_name}</h2>
        <div className="flex items-center gap-2">
          {saved && <span className="text-sm text-green-400">Salvo!</span>}
          <Button onClick={() => void handleSave()} disabled={!dirty || saveData.isPending}>
            {saveData.isPending ? "Salvando…" : "Salvar ficha"}
          </Button>
        </div>
      </div>

      {fields.length > 0 ? (
        <SheetForm
          fields={fields}
          values={values}
          onChange={(next) => {
            setValues(next);
            setDirty(true);
          }}
          readOnly={!canEdit && !isMaster}
          onMediaUpload={canEdit || isMaster ? handleMediaUpload : undefined}
          mediaPreviewUrls={mediaPreviewUrls}
          onPreviewUrl={handlePreviewUrl}
        />
      ) : (
        <ErrorAlert message="Schema do template indisponível." />
      )}
    </div>
  );
}
