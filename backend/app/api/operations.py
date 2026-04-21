from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.dependencies import get_current_user, get_db
from app.database.db import Database
from app.models.schemas import (
    OperationCreateRequest,
    OperationResponse,
    OperationUpdateRequest,
)

router = APIRouter(prefix="/operations", tags=["Operations"])


async def _ensure_category_owner(db: Database, category_id: int, user_id: int) -> None:
    category = await db.fetchrow(
        "SELECT id FROM categories WHERE id = $1 AND user_id = $2",
        category_id,
        user_id,
    )
    if category is None:
        raise HTTPException(status_code=400, detail="Category does not belong to user")


@router.get("", response_model=list[OperationResponse])
async def list_operations(
    month: int | None = Query(None, ge=1, le=12),
    year: int | None = Query(None, ge=2000),
    db: Database = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if month is None or year is None:
        rows = await db.fetch(
            '''
            SELECT o.id, o.user_id, o.category_id, c.name AS category_name,
                   o.type, o.amount, o.operation_date, o.comment, o.created_at, o.updated_at
            FROM operations o
            JOIN categories c ON c.id = o.category_id
            WHERE o.user_id = $1
            ORDER BY o.operation_date DESC, o.created_at DESC
            ''',
            current_user["id"],
        )
    else:
        rows = await db.fetch(
            '''
            SELECT o.id, o.user_id, o.category_id, c.name AS category_name,
                   o.type, o.amount, o.operation_date, o.comment, o.created_at, o.updated_at
            FROM operations o
            JOIN categories c ON c.id = o.category_id
            WHERE o.user_id = $1
              AND EXTRACT(MONTH FROM o.operation_date) = $2
              AND EXTRACT(YEAR FROM o.operation_date) = $3
            ORDER BY o.operation_date DESC, o.created_at DESC
            ''',
            current_user["id"],
            month,
            year,
        )
    return [dict(row) for row in rows]


@router.post("", response_model=OperationResponse, status_code=status.HTTP_201_CREATED)
async def create_operation(
    payload: OperationCreateRequest,
    db: Database = Depends(get_db),
    current_user=Depends(get_current_user),
):
    await _ensure_category_owner(db, payload.category_id, current_user["id"])
    row = await db.fetchrow(
        '''
        INSERT INTO operations (
            user_id, category_id, type, amount, operation_date, comment, created_at, updated_at
        )
        VALUES ($1, $2, $3, $4, $5, $6, NOW(), NOW())
        RETURNING id, user_id, category_id, type, amount, operation_date, comment, created_at, updated_at
        ''',
        current_user["id"],
        payload.category_id,
        payload.type,
        payload.amount,
        payload.operation_date,
        payload.comment,
    )
    category = await db.fetchrow("SELECT name FROM categories WHERE id = $1", payload.category_id)
    data = dict(row)
    data["category_name"] = category["name"]
    return data


@router.put("/{operation_id}", response_model=OperationResponse)
async def update_operation(
    operation_id: int,
    payload: OperationUpdateRequest,
    db: Database = Depends(get_db),
    current_user=Depends(get_current_user),
):
    await _ensure_category_owner(db, payload.category_id, current_user["id"])
    row = await db.fetchrow(
        '''
        UPDATE operations
        SET category_id = $1,
            type = $2,
            amount = $3,
            operation_date = $4,
            comment = $5,
            updated_at = NOW()
        WHERE id = $6 AND user_id = $7
        RETURNING id, user_id, category_id, type, amount, operation_date, comment, created_at, updated_at
        ''',
        payload.category_id,
        payload.type,
        payload.amount,
        payload.operation_date,
        payload.comment,
        operation_id,
        current_user["id"],
    )
    if row is None:
        raise HTTPException(status_code=404, detail="Operation not found")
    category = await db.fetchrow("SELECT name FROM categories WHERE id = $1", payload.category_id)
    data = dict(row)
    data["category_name"] = category["name"]
    return data


@router.delete("/{operation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_operation(
    operation_id: int,
    db: Database = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = await db.execute(
        "DELETE FROM operations WHERE id = $1 AND user_id = $2",
        operation_id,
        current_user["id"],
    )
    if result == "DELETE 0":
        raise HTTPException(status_code=404, detail="Operation not found")
