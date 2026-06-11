"""User profile routes."""

from fastapi import APIRouter, UploadFile
from pydantic import BaseModel, Field
from rpg_platform.api.deps import CurrentUser, DbSession, StorageDep

router = APIRouter(prefix="/users", tags=["users"])


class UserProfileResponse(BaseModel):
    id: str
    email: str
    display_name: str
    avatar_storage_path: str | None
    is_admin: bool
    status: str
    master_mesa_count: int


class UpdateProfileRequest(BaseModel):
    display_name: str | None = Field(default=None, max_length=120)


@router.get("/me", response_model=UserProfileResponse)
async def get_profile(user: CurrentUser) -> UserProfileResponse:
    return UserProfileResponse(
        id=str(user.id),
        email=user.email,
        display_name=user.display_name,
        avatar_storage_path=user.avatar_storage_path,
        is_admin=user.is_admin,
        status=user.status.value,
        master_mesa_count=user.master_mesa_count,
    )


@router.patch("/me", response_model=UserProfileResponse)
async def update_profile(
    body: UpdateProfileRequest,
    user: CurrentUser,
    session: DbSession,
) -> UserProfileResponse:
    if body.display_name is not None:
        user.display_name = body.display_name
    await session.flush()
    return UserProfileResponse(
        id=str(user.id),
        email=user.email,
        display_name=user.display_name,
        avatar_storage_path=user.avatar_storage_path,
        is_admin=user.is_admin,
        status=user.status.value,
        master_mesa_count=user.master_mesa_count,
    )


@router.post("/me/avatar")
async def upload_avatar(
    file: UploadFile,
    user: CurrentUser,
    session: DbSession,
    storage: StorageDep,
) -> dict:
    ext = "png"
    if file.content_type == "image/jpeg":
        ext = "jpg"
    elif file.content_type == "image/webp":
        ext = "webp"
    path = f"{user.id}/avatar.{ext}"
    data = await file.read()
    await storage.put_bytes("profiles", path, data, content_type=file.content_type or "image/png")
    user.avatar_storage_path = path
    await session.flush()
    url = await storage.create_signed_url("profiles", path)
    return {"avatar_storage_path": path, "signed_url": url}
