from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, Header
from FastAPIUserService.config.db_config import get_db
from FastAPIUserService.crud.users import get_user_by_token
from starlette import status


# 整合 根据 Token 查询用户，返回用户
async def get_current_user(authorization: str = Header(..., alias="Authorization"), db: AsyncSession = Depends(get_db)):
    token = authorization
    user = await get_user_by_token(db, token)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="无效令牌或令牌已过期")
    return user





