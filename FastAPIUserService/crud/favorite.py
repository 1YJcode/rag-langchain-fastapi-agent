from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from FastAPIUserService.models.favorite import Favorite
from FastAPIUserService.models.news import News


async def is_favorite_news(
        db: AsyncSession,
        user_id: int,
        news_id: int
) -> bool:
    stmt = select(Favorite).where(Favorite.user_id == user_id, Favorite.news_id == news_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none() is not None


async def toggle_favorite(
        db: AsyncSession,
        user_id: int,
        news_id: int
) -> bool:
    """切换收藏状态，返回 True=已收藏, False=已取消"""
    stmt = select(Favorite).where(Favorite.user_id == user_id, Favorite.news_id == news_id)
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()

    if existing:
        await db.delete(existing)
        await db.commit()
        return False
    else:
        fav = Favorite(user_id=user_id, news_id=news_id)
        db.add(fav)
        await db.commit()
        return True


async def get_favorite_news(
        db: AsyncSession,
        user_id: int
):
    """获取用户收藏的新闻列表（按收藏时间倒序）"""
    stmt = (
        select(News)
        .join(Favorite, Favorite.news_id == News.id)
        .where(Favorite.user_id == user_id)
        .order_by(Favorite.created_at.desc())
    )
    result = await db.execute(stmt)
    return result.scalars().all()


async def clear_all_favorite_news(
        db: AsyncSession,
        user_id: int
):
    stmt = delete(Favorite).where(Favorite.user_id == user_id)
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount if result.rowcount else 0
