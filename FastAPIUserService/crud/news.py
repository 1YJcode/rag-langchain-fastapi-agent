from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select, update
from FastAPIUserService.models.news import Category, News

# 获取新闻分类列表
async def get_categories(db: AsyncSession, skip: int = 0, limit: int = 100):
    stmt = select(Category).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

# 获取新闻列表
async def get_list(db: AsyncSession, category_id: int, skip: int = 0, limit: int = 10):
    stmt = select(News).where(News.category_id == category_id).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


# 获取新闻总数
async def get_total(db: AsyncSession, category_id: int):
    # 查询的指定分类下的新闻数量
    stmt = select(func.count(News.id)).where(News.category_id == category_id)
    result = await db.execute(stmt)
    return result.scalar_one()


# 获取新闻详情
async def get_detail(db: AsyncSession, news_id: int):
    stmt = select(News).where(News.id == news_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


# 增加新闻浏览量
async def increment_views(db: AsyncSession, news_id: int):
    stmt = update(News).where(News.id == news_id).values(views=News.views + 1)
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount > 0


# 获取相关的新闻列表
async def get_related_news(db: AsyncSession, category_id: int, news_id: int, limit: int = 5):
    stmt = select(News).where(
        News.category_id == category_id,
        News.id != news_id
    ).order_by(
        News.publish_time.desc(),
        News.views.desc()  
               ).limit(limit)
    result = await db.execute(stmt)
    related_news = result.scalars().all()
    return [
        {"id": news.id,
            "title": news.title,
            "content": news.content,
            "image": news.image,
            "author": news.author,
            "publish_time": news.publish_time,
            "categoryId": news.category_id,
            "views": news.views
        } for news in related_news
            ]