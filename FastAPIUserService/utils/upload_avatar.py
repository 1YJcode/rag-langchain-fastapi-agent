import os
import uuid
from fastapi import UploadFile, HTTPException, status

from FastAPIUserService.schemas.users import UserUpdateRequest

# 使用绝对路径，确保无论从哪个目录启动都能找到头像文件
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static", "avatars")
os.makedirs(UPLOAD_DIR, exist_ok=True)

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


async def upload_avatar_orm(file: UploadFile):
    # 第1层：Content-Length 秒拒（不发在请求体上的大文件，不读流）
    content_length = file.headers.get("content-length")
    if content_length and int(content_length) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="图片大小不能超过5MB"
        )

    # 校验文件类型
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只允许上传图片文件"
        )

    # 第2层：分块读取，超过 5MB 立刻终止（防止 Content-Length 缺失或被篡改）
    chunks = []
    total = 0
    while True:
        chunk = await file.read(8192)  # 8KB per chunk
        if not chunk:
            break
        total += len(chunk)
        if total > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="图片大小不能超过5MB"
            )
        chunks.append(chunk)

    contents = b"".join(chunks)

    # 生成唯一文件名，保留原始扩展名
    ext = os.path.splitext(file.filename)[1] if file.filename else ".png"
    filename = f"{uuid.uuid4().hex}{ext}"

    # 写入磁盘
    file_path = os.path.join(UPLOAD_DIR, filename)
    with open(file_path, "wb") as f:
        f.write(contents)

    # 拼接访问 URL
    avatar_url = f"/static/avatars/{filename}"

    # 返回更新数据
    return UserUpdateRequest(avatar=avatar_url)