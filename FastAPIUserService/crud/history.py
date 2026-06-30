from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from FastAPIUserService.models.history import History
from FastAPIUserService.models.news import News





async def check_history(
        news_id: int,
        user_id: int,
        db: AsyncSession
) -> bool:
    stmt = select(History).where(History.user_id == user_id, History.news_id == news_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none() is not None

# 添加浏览或取消浏览记录
async def toggling_view_news(
        user_id: int,
        news_id: int,
        db: AsyncSession
):
    stmt = select(History).where(History.user_id == user_id, History.news_id == news_id)
    result = await db.execute(stmt)
    exiting = result.scalar_one_or_none()
    if exiting:
        await db.delete(exiting)
        await db.commit()
        return False
    else:
        add_view = History(user_id=user_id, news_id=news_id)
        db.add(add_view)
        await db.commit()
        return True

    

# 获得浏览历史记录列表
async def getting_news_history(
        user_id: int,
        db: AsyncSession
):
    stmt = select(News).join(History, History.news_id == News.id).where(History.user_id == user_id).order_by(History.view_time.desc())
    result = await db.execute(stmt)
    return result.scalars().all()


# 添加浏览记录（只添加，不会取消）
async def add_view_news(
        user_id: int,
        news_id: int,
        db: AsyncSession
):
    stmt = select(History).where(History.user_id == user_id, History.news_id == news_id)
    result = await db.execute(stmt)
    if not result.scalar_one_or_none():
        add_view = History(user_id=user_id, news_id=news_id)
        db.add(add_view)
        await db.commit()
        return True
    return False


# 清除浏览历史记录
async def clearing_news_history(
        user_id: int,
        db: AsyncSession
):
    stmt = delete(History).where(History.user_id==user_id)
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount if result.rowcount else 0

