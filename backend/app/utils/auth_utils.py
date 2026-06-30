# backend/app/utils/auth_utils.py
import os
import httpx
from typing import Optional, Any
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette import status

from backend.app.core.logger_handler import logger

# 用户服务配置
USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://localhost:8001")

security = HTTPBearer()


async def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """通过用户服务验证 JWT 并获取用户 ID"""
    token = credentials.credentials

    try:
        # 调用用户服务验证 token
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(
                f"{USER_SERVICE_URL}/api/v1/auth/verify",
                json={"token": token}
            )

            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token"
                )

            data = response.json()
            if data.get("code") != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=data.get("message", "Invalid token")
                )

            user_id = data.get("data", {}).get("user_id")
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User ID not found in token"
                )

            return user_id

    except httpx.TimeoutException:
        logger.error("用户服务调用超时")
        raise HTTPException(status_code=503, detail="认证服务不可用")
    except httpx.ConnectError:
        logger.error("无法连接到用户服务")
        raise HTTPException(status_code=503, detail="认证服务连接失败")
    except Exception as e:
        logger.error(f"验证 token 失败: {e}")
        raise HTTPException(status_code=401, detail="认证失败")


async def get_user_info_from_service(user_id: str, token: str) -> Optional[dict]:
    """从用户服务获取用户信息"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(
                f"{USER_SERVICE_URL}/api/v1/users/{user_id}",
                headers={"Authorization": f"Bearer {token}"}
            )

            if response.status_code == 200:
                data = response.json()
                # 适配用户服务的返回格式
                if data.get("code") == 200:
                    return data.get("data")
                return data
            return None
    except Exception as e:
        logger.error(f"获取用户信息失败: {e}")
        return None


# 保留原有的 decode_fastapi_jwt 函数（如果你的业务代码其他地方有调用）
def decode_fastapi_jwt(token: str) -> Optional[dict]:
    """解析 JWT Token（通过用户服务验证）"""
    # 这个方法现在通过用户服务验证
    # 如果只是本地解码，可以保留原有逻辑
    import jwt
    from jose import JWTError

    SECRET_KEY = os.getenv("SECRET_KEY")
    ALGORITHM = os.getenv("ALGORITHM")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


# 如果你有 get_user_info_from_redis 函数，修改为：
async def get_user_info_from_redis(user_id: str, credentials: HTTPAuthorizationCredentials) -> Optional[dict]:
    """从用户服务获取用户信息（替代 Redis 缓存）"""
    return await get_user_info_from_service(user_id, credentials.credentials)