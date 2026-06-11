"""Auth routes."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from rpg_platform.api.deps import CurrentUser, DbSession, TokenClaims, get_token_claims
from rpg_platform.services.users import sync_user_from_claims

router = APIRouter(prefix="/auth", tags=["auth"])


class UserResponse(BaseModel):
    id: str
    email: str
    display_name: str
    is_admin: bool
    status: str

    model_config = {"from_attributes": True}


@router.post("/sync", response_model=UserResponse)
async def sync_auth(
    session: DbSession,
    claims: TokenClaims = Depends(get_token_claims),
) -> UserResponse:
    user = await sync_user_from_claims(session, claims)
    return UserResponse(
        id=str(user.id),
        email=user.email,
        display_name=user.display_name,
        is_admin=user.is_admin,
        status=user.status.value,
    )


@router.get("/me", response_model=UserResponse)
async def auth_me(user: CurrentUser) -> UserResponse:
    return UserResponse(
        id=str(user.id),
        email=user.email,
        display_name=user.display_name,
        is_admin=user.is_admin,
        status=user.status.value,
    )
