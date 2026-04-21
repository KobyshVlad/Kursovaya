from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.dependencies import get_current_user, get_db
from app.database.db import Database
from app.models.schemas import (
    BudgetCompareResponse,
    BudgetCreateRequest,
    BudgetResponse,
    BudgetUpdateRequest,
)

router = APIRouter(prefix="/budget", tags=["Budget"])


async def _ensure_category_owner(db: Database, category_id: int, user_id: int) -> None:
    category = await db.fetchrow(
        "SELECT id FROM categories WHERE id = $1 AND user_id = $2",
        category_id,
        user_id,
    )
    if category is None:
        raise HTTPException(status_code=400, detail="Category does not belong to user")


@router.get("", response_model=list[BudgetResponse])
async def list_budget(
    month: int = Query(..., ge=1, le=12),
    year: int = Query(..., ge=2000),
    db: Database = Depends(get_db),
    current_user=Depends(get_current_user),
):
    rows = await db.fetch(
        '''
        SELECT b.id, b.user_id, b.category_id, c.name AS category_name,
               b.month, b.year, b.planned_amount, b.created_at, b.updated_at
        FROM budget b
        JOIN categories c ON c.id = b.category_id
        WHERE b.user_id = $1 AND b.month = $2 AND b.year = $3
        ORDER BY c.name ASC
        ''',
        current_user["id"],
        month,
        year,
    )
    return [dict(row) for row in rows]


@router.post("", response_model=BudgetResponse, status_code=status.HTTP_201_CREATED)
async def create_budget(
    payload: BudgetCreateRequest,
    db: Database = Depends(get_db),
    current_user=Depends(get_current_user),
):
    await _ensure_category_owner(db, payload.category_id, current_user["id"])
    row = await db.fetchrow(
        '''
        INSERT INTO budget (
            user_id, category_id, month, year, planned_amount, created_at, updated_at
        )
        VALUES ($1, $2, $3, $4, $5, NOW(), NOW())
        ON CONFLICT (user_id, category_id, month, year)
        DO UPDATE SET planned_amount = EXCLUDED.planned_amount, updated_at = NOW()
        RETURNING id, user_id, category_id, month, year, planned_amount, created_at, updated_at
        ''',
        current_user["id"],
        payload.category_id,
        payload.month,
        payload.year,
        payload.planned_amount,
    )

    category = await db.fetchrow("SELECT name FROM categories WHERE id = $1", payload.category_id)
    data = dict(row)
    data["category_name"] = category["name"]
    return data


@router.put("/{budget_id}", response_model=BudgetResponse)
async def update_budget(
    budget_id: int,
    payload: BudgetUpdateRequest,
    db: Database = Depends(get_db),
    current_user=Depends(get_current_user),
):
    row = await db.fetchrow(
        '''
        UPDATE budget
        SET planned_amount = $1, updated_at = NOW()
        WHERE id = $2 AND user_id = $3
        RETURNING id, user_id, category_id, month, year, planned_amount, created_at, updated_at
        ''',
        payload.planned_amount,
        budget_id,
        current_user["id"],
    )
    if row is None:
        raise HTTPException(status_code=404, detail="Budget record not found")
    category = await db.fetchrow("SELECT name FROM categories WHERE id = $1", row["category_id"])
    data = dict(row)
    data["category_name"] = category["name"]
    return data


@router.get("/actual-summary")
async def actual_summary(
    month: int = Query(..., ge=1, le=12),
    year: int = Query(..., ge=2000),
    db: Database = Depends(get_db),
    current_user=Depends(get_current_user),
):
    rows = await db.fetch(
        '''
        SELECT aes.category_id,
               c.name AS category_name,
               aes.month,
               aes.year,
               aes.total_actual AS actual_amount
        FROM actual_expense_summary aes
        JOIN categories c ON c.id = aes.category_id
        WHERE aes.user_id = $1 AND aes.month = $2 AND aes.year = $3
        ORDER BY c.name ASC
        ''',
        current_user["id"],
        month,
        year,
    )
    return [dict(row) for row in rows]


@router.get("/compare", response_model=list[BudgetCompareResponse])
async def compare_budget(
    month: int = Query(..., ge=1, le=12),
    year: int = Query(..., ge=2000),
    db: Database = Depends(get_db),
    current_user=Depends(get_current_user),
):
    rows = await db.fetch(
        '''
        SELECT b.category_id,
               c.name AS category_name,
               b.month,
               b.year,
               b.planned_amount,
               COALESCE(aes.total_actual, 0) AS actual_amount,
               b.planned_amount - COALESCE(aes.total_actual, 0) AS difference
        FROM budget b
        JOIN categories c ON c.id = b.category_id
        LEFT JOIN actual_expense_summary aes
               ON aes.user_id = b.user_id
              AND aes.category_id = b.category_id
              AND aes.month = b.month
              AND aes.year = b.year
        WHERE b.user_id = $1 AND b.month = $2 AND b.year = $3
        ORDER BY c.name ASC
        ''',
        current_user["id"],
        month,
        year,
    )
    return [
        {
            **dict(row),
            "actual_amount": row["actual_amount"] if row["actual_amount"] is not None else Decimal("0"),
        }
        for row in rows
    ]
