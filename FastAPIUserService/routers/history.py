from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from FastAPIUserService.config.db_config import get_db
from FastAPIUserService.crud.history import check_history, clearing_news_history, getting_news_history, toggling_view_news, add_view_news
from FastAPIUserService.schemas.history import HistoryCheckResponse
from FastAPIUserService.models.users import User
from FastAPIUserService.utils.auth import get_current_user
from FastAPIUserService.utils.success_response import success_response

router = APIRouter(prefix="/api/history", tags=["history"])


# 检查用户是否浏览了新闻
@router.get("/check")
async def check_viewed_history(
    news_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    is_viewed = await check_history(news_id, user.id, db)
    return success_response(message="检查历史浏览记录获取成功", data=HistoryCheckResponse(isView=is_viewed))


# 浏览新闻时添加到新闻历史浏览记录
@router.post("/toggle_view")
async def toggle_view_news(
    news_id: int,
    user: User =  Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    is_viewed = await toggling_view_news(user.id, news_id, db)
    return success_response(message="浏览新闻成功", data=HistoryCheckResponse(isView=is_viewed))


# 获取新闻历史浏览记录列表
@router.get("/history_list")
async def get_history_list(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    view_news_history_list = await getting_news_history(user.id, db)
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
    for n in view_news_history_list
    ]
    return success_response(message="获取收藏列表成功", data=result)



# 浏览新闻时添加浏览记录
@router.post("/add_view")
async def add_view_news_endpoint(
    news_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    is_viewed = await add_view_news(user.id, news_id, db)
    return success_response(message="浏览新闻成功", data=HistoryCheckResponse(isView=is_viewed))


# 清除浏览历史记录路由
@router.delete("/clear_history")
async def clear_news_history(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    count = await clearing_news_history(user.id, db)
    return success_response(message=f"清除了{count}历史浏览记录成功")