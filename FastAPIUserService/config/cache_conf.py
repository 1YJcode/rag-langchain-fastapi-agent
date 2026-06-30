import redis.asyncio as redis

REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0


# 创建 Redis 的连接对象
redis_client = redis.Redis(
    host=REDIS_HOST,  # redis服务器地址
    port=REDIS_PORT,  # 端口号 6379
    db=REDIS_DB,      # 数据库编号（0~15）
    decode_response=True  # 是否将返回的数据从字节流解码为字符串
)
