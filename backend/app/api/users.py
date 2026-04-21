from fastapi import APIRouter, Depends, HTTPException

from app.core.dependencies import get_current_user, get_db
from app.database.db import Database
from app.models.schemas import UserResponse, UserUpdateRequest

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
async def get_me(current_user=Depends(get_current_user)):
    return dict(current_user)


@router.put("/me", response_model=UserResponse)
async def update_me(
    payload: UserUpdateRequest,
    db: Database = Depends(get_db),
    current_user=Depends(get_current_user),
):
    conflict = await db.fetchrow(
        "SELECT id FROM users WHERE email = $1 AND id <> $2",
        payload.email,
        current_user["id"],
    )
    if conflict:
        raise HTTPException(status_code=400, detail="Email already in use")

    updated = await db.fetchrow(
        """
        UPDATE users
        SET name = $1, email = $2, start_month = $3, updated_at = NOW()
        WHERE id = $4
        RETURNING id, name, email, start_month, created_at, updated_at
        """,
        payload.name,
        payload.email,
        payload.start_month,
        current_user["id"],
    )
    return dict(updated)
