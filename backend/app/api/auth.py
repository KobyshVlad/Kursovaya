from fastapi import APIRouter, Depends, HTTPException, status

from app.core.dependencies import get_db
from app.core.security import create_access_token, hash_password, verify_password
from app.database.db import Database
from app.models.schemas import LoginRequest, RegisterRequest, TokenResponse, UserResponse

router = APIRouter(prefix="/auth", tags=["Auth"])

DEFAULT_CATEGORIES = [
    "Медицина",
    "Образование",
    "Продукты",
    "Транспорт",
    "ЖКХ",
    "Аренда",
    "Кредит",
    "Ипотека",
    "Зарплата",
    "Премия",
]


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    payload: RegisterRequest,
    db: Database = Depends(get_db),
):
    existing = await db.fetchrow(
        "SELECT id FROM users WHERE email = $1",
        payload.email,
    )
    if existing is not None:
        raise HTTPException(status_code=400, detail="Пользователь с таким email уже существует")

    try:
        password_hash = hash_password(payload.password)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    async with db.acquire() as conn:
        async with conn.transaction():
            row = await conn.fetchrow(
                '''
                INSERT INTO users (name, email, password_hash, start_month, created_at, updated_at)
                VALUES ($1, $2, $3, $4, NOW(), NOW())
                RETURNING id, name, email, start_month, created_at, updated_at
                ''',
                payload.name,
                payload.email,
                password_hash,
                payload.start_month,
            )

            await conn.executemany(
                '''
                INSERT INTO categories (user_id, name, created_at, updated_at)
                VALUES ($1, $2, NOW(), NOW())
                ''',
                [(row["id"], category_name) for category_name in DEFAULT_CATEGORIES],
            )

    return dict(row)


@router.post("/login", response_model=TokenResponse)
async def login(
    payload: LoginRequest,
    db: Database = Depends(get_db),
):
    row = await db.fetchrow(
        "SELECT id, email, password_hash FROM users WHERE email = $1",
        payload.email,
    )
    if row is None or not verify_password(payload.password, row["password_hash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверный email или пароль")

    access_token = create_access_token(str(row["id"]))
    return {"access_token": access_token, "token_type": "bearer"}
