from fastapi import APIRouter, Depends, HTTPException, status

from app.core.dependencies import get_current_user, get_db
from app.database.db import Database
from app.models.schemas import CategoryCreateRequest, CategoryResponse, CategoryUpdateRequest

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("", response_model=list[CategoryResponse])
async def list_categories(
    db: Database = Depends(get_db),
    current_user=Depends(get_current_user),
):
    rows = await db.fetch(
        """
        SELECT id, user_id, name, created_at, updated_at
        FROM categories
        WHERE user_id = $1
        ORDER BY name ASC
        """,
        current_user["id"],
    )
    return [dict(row) for row in rows]


@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    payload: CategoryCreateRequest,
    db: Database = Depends(get_db),
    current_user=Depends(get_current_user),
):
    row = await db.fetchrow(
        """
        INSERT INTO categories (user_id, name, created_at, updated_at)
        VALUES ($1, $2, NOW(), NOW())
        RETURNING id, user_id, name, created_at, updated_at
        """,
        current_user["id"],
        payload.name,
    )
    return dict(row)


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    payload: CategoryUpdateRequest,
    db: Database = Depends(get_db),
    current_user=Depends(get_current_user),
):
    row = await db.fetchrow(
        """
        UPDATE categories
        SET name = $1, updated_at = NOW()
        WHERE id = $2 AND user_id = $3
        RETURNING id, user_id, name, created_at, updated_at
        """,
        payload.name,
        category_id,
        current_user["id"],
    )
    if row is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return dict(row)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: int,
    db: Database = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = await db.execute(
        "DELETE FROM categories WHERE id = $1 AND user_id = $2",
        category_id,
        current_user["id"],
    )
    if result == "DELETE 0":
        raise HTTPException(status_code=404, detail="Category not found")
