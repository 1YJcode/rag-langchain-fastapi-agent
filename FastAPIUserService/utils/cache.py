import json
from typing import Any

from FastAPIUserService.config.cache_conf import redis_client

# 设置和读取（字符串和 列表或字典） "[{}]"
# 读取：字符串缓存
async def get_str_cache(key: str):
    try:
        return await redis_client.get(key)
    
    except Exception as e:
        print(f"获取str缓存失败{e}")
        return None


# 读取：列表或字典缓存
async def get_json_cache(key: str):
    try:
        data = await redis_client.get(key)
        if data:
            return json.loads(data)
    
    except Exception as e:
        print(f"获取json缓存失败:{e}")
        return None


# 设置缓存setex(key, value, expire)
async def set_cache(key: str, value: Any, expire: int = 3600):
    try:
        if isinstance(value, (dict, list)):
            # 转字符串
            value = json.dumps(value, ensure_ascii=False) # ensure_ascii不将中文转义
            await redis_client.setex(key, expire, value)
            return True
    except Exception as e:
        print(f"设置缓存失败：{e}")
        return False