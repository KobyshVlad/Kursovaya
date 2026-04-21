from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer

from app.core.security import TokenError, decode_access_token
from app.database.db import Database


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_db(request: Request) -> Database:
    return request.app.state.db


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Database = Depends(get_db),
):
    try:
        payload = decode_access_token(token)
        user_id = int(payload["sub"])
    except (TokenError, KeyError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

    user = await db.fetchrow(
        """
        SELECT id, name, email, start_month, created_at, updated_at
        FROM users
        WHERE id = $1
        """,
        user_id,
    )
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user
