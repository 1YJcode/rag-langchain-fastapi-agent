from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from starlette import status

from FastAPIUserService.config.db_config import get_db
from FastAPIUserService.crud.users import get_user_by_token
from FastAPIUserService.utils.success_response import success_response

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


class VerifyTokenRequest(BaseModel):
    token: str


@router.post("/verify")
async def verify_token(request: VerifyTokenRequest, db: AsyncSession = Depends(get_db)):
    """
    验证用户 Token 的有效性，返回用户 ID。
    供 backend Agent 服务调用以验证用户身份。
    """
    user = await get_user_by_token(db, request.token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效令牌或令牌已过期"
        )

    return success_response(message="Token 验证成功", data={"user_id": user.id})
