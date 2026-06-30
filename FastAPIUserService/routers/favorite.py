from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from FastAPIUserService.config.db_config import get_db
from FastAPIUserService.crud.favorite import clear_all_favorite_news, get_favorite_news, is_favorite_news, toggle_favorite
from FastAPIUserService.models.users import User
from FastAPIUserService.schemas.favorite import FavoriteCheckResponse
from FastAPIUserService.utils.success_response import success_response
from FastAPIUserService.utils.auth import get_current_user


router = APIRouter(prefix="/api/favorite", tags=["favorite"])


@router.get("/check")
async def check_favorite(
    news_id: int = Query(..., alias="newsId"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    is_favorited = await is_favorite_news(db, user.id, news_id)
    return success_response(message="检查收藏状态成功", data=FavoriteCheckResponse(isFavorite=is_favorited))


@router.post("/toggle")
async def toggle_favorite_endpoint(
    news_id: int = Query(..., alias="newsId"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    is_fav = await toggle_favorite(db, user.id, news_id)
    return success_response(
        message="收藏成功" if is_fav else "已取消收藏",
        data={"isFavorite": is_fav}
    )


@router.get("/list")
async def list_favorites(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    news_list = await get_favorite_news(db, user.id)
    result = [
        {
            "id": n.id,
            "title": n.title,
            "image": n.image,
            "author": n.author,
            "publish_time": n.publish_time,
            "views": n.views,
            "categoryId": n.category_id
        }
        for n in news_list
    ]
    return success_response(message="获取收藏列表成功", data=result)


# 清空收藏列表
@router.delete("/clear")
async def clear_favorite(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    count = await clear_all_favorite_news(db, user.id)
    return success_response(message=f"清空了{count}收藏列表")