from fastapi import Request, HTTPException
from backend.app.db.redis_config import connect_redis


def rate_limit(limit: int = 1, window: int = 60):
    """
    限流依赖函数
    :param limit: 时间窗口内最大请求数
    :param window: 时间窗口大小（秒）
    :return: 依赖数据
    """
    async def dependency(request: Request):
        # 获取客户端IP
        client_ip = request.client.host
        if not client_ip:
            client_ip = request.headers.get('x-Forwarded-For', '').split(',')[0].strip() or 'unknown'

        # 生成限流键
        key = f"rate_limit:aichat:{client_ip}"

        # 获取Redis连接
        redis = await connect_redis()

        # 获取当前计数
        current = await redis.get(key)
        current = int(current) if current else 0

        if current >= limit:
            # 限流触发
            raise HTTPException(
                status_code=429,
                detail="请求过于频繁，请稍后再试"
            )

        # 增加计数
        if current == 0:
            # 第一次请求，设置过期时间
            await redis.setex(key, window, 1)
        else:
            await redis.incr(key)

    return dependency

class RateLimitMiddleware:
    """
    全局限流中间件
    """
    def __init__(self, app, limit: int = 100, window: int = 60):
        self.app = app
        self.limit = limit
        self.window = window

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # 从scope中直接获取客户端IP，不构造Request（避免消费请求体）
        client_ip = scope.get("client", (None, None))[0]
        if not client_ip:
            # 从headers中获取forwarded ip
            headers = dict(scope.get("headers", []))
            forwarded = headers.get(b"x-forwarded-for", b"").decode()
            client_ip = forwarded.split(",")[0].strip() if forwarded else "unknown"

        # 生成限流键
        key = f"rate_limit:global:{client_ip}"

        # 获取Redis连接
        redis = await connect_redis()

        # 获取当前计数
        current = await redis.get(key)
        current = int(current) if current else 0

        if current >= self.limit:
            # 限流触发
            from starlette.responses import JSONResponse
            response = JSONResponse(
                {"detail": "请求过于频繁，请稍后再试"},
                status_code=429
            )
            await response(scope, receive, send)
            return

        # 增加计数
        if current == 0:
            # 第一次请求，设置过期时间
            await redis.setex(key, self.window, 1)
        else:
            # 后续请求，增加计数
            await redis.incr(key)

        await self.app(scope, receive, send)









