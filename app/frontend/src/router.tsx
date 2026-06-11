import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { AppLayout } from "./components/layout/AppLayout";
import { MesaLayout } from "./components/layout/MesaLayout";
import { ProtectedRoute, PublicOnlyRoute } from "./components/auth/ProtectedRoute";
import { LoginPage } from "./features/auth/LoginPage";
import { RegisterPage } from "./features/auth/RegisterPage";
import { AuthCallbackPage } from "./features/auth/AuthCallbackPage";
import { ResetPasswordPage } from "./features/auth/ResetPasswordPage";
import { MesaListPage } from "./features/mesas/MesaListPage";
import { MesaCreatePage } from "./features/mesas/MesaCreatePage";
import { MesaOverviewPage } from "./features/mesas/MesaOverviewPage";
import { ImportReviewPage } from "./features/import/ImportReviewPage";
import {
  CharacterCreatePage,
  CharacterListPage,
} from "./features/characters/CharacterListPage";
import { CharacterEditorPage } from "./features/characters/CharacterEditorPage";
import {
  DocumentCreatePage,
  DocumentListPage,
} from "./features/documents/DocumentListPage";
import { DocumentEditorPage } from "./features/documents/DocumentEditorPage";
import { ParticipantsPage } from "./features/participants/ParticipantsPage";
import { AcceptInvitePage } from "./features/participants/AcceptInvitePage";
import { ProfileSettingsPage } from "./features/auth/ProfileSettingsPage";
import { AdminPage } from "./features/admin/AdminPage";

export function AppRouter() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<PublicOnlyRoute><LoginPage /></PublicOnlyRoute>} />
        <Route path="/register" element={<PublicOnlyRoute><RegisterPage /></PublicOnlyRoute>} />
        <Route path="/reset-password" element={<ResetPasswordPage />} />
        <Route path="/auth/callback" element={<AuthCallbackPage />} />
        <Route path="/accept-invite" element={<AcceptInvitePage />} />

        <Route element={<ProtectedRoute><AppLayout /></ProtectedRoute>}>
          <Route index element={<Navigate to="/mesas" replace />} />
          <Route path="mesas" element={<MesaListPage />} />
          <Route path="mesas/new" element={<MesaCreatePage />} />
          <Route path="profile" element={<ProfileSettingsPage />} />
          <Route path="admin" element={<AdminPage />} />

          <Route path="mesas/:mesaId" element={<MesaLayout />}>
            <Route index element={<MesaOverviewPage />} />
            <Route path="import" element={<ImportReviewPage />} />
            <Route path="characters" element={<CharacterListPage />} />
            <Route path="characters/new" element={<CharacterCreatePage />} />
            <Route path="characters/:characterId" element={<CharacterEditorPage />} />
            <Route path="documents" element={<DocumentListPage />} />
            <Route path="documents/new" element={<DocumentCreatePage />} />
            <Route path="documents/:documentId" element={<DocumentEditorPage />} />
            <Route path="participants" element={<ParticipantsPage />} />
          </Route>
        </Route>

        <Route path="*" element={<Navigate to="/mesas" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
