from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from FastAPIUserService.config.db_config import get_db
from FastAPIUserService.crud.news import get_categories, get_list, get_total, get_detail, increment_views, get_related_news


# 创建一个新的APIRouter实例
router = APIRouter(prefix="/api/news", tags=["news"])

@router.get("/categories")
async def get_news_categories(db: AsyncSession = Depends(get_db), skip: int = 0, limit: int = 100):
    categories = await get_categories(db, skip, limit)
    return {
        "code": 200,
        "message": "获取新闻分类成功",
        "data": categories
    }


# 获取新闻列表接口
@router.get("/list")
async def get_news_list(
    db: AsyncSession = Depends(get_db), 
    category_id: int = Query(..., alias="categoryId", description="分类ID"),
    page: int = 1,
    page_size: int = Query(..., alias="pageSize", le=100, description="每页数量")
):
    offset = (page - 1) * page_size
    news_list = await get_list(db, category_id, offset, page_size)
    total = await get_total(db, category_id)
    has_more = (offset + len(news_list)) < total
    return {
        "code": 200,
        "message": "获取新闻列表成功",
        "data": {
            "list": news_list,
            "total": total,
            "hasMore": has_more
        }
    }

@router.get("/detail")
async def get_news_detail(
    db: AsyncSession = Depends(get_db),
    news_id: int = Query(..., alias="id", description="新闻ID")
):
    news_detail = await get_detail(db, news_id)

    # 如果新闻详情不存在，返回404错误
    if news_detail is None:
        raise HTTPException(status_code=404, detail="新闻未找到")
    
    # 增加新闻浏览量
    views_res = await increment_views(db, news_detail.id)
    if not views_res:
        raise HTTPException(status_code=404, detail="新闻未找到")

    # 获取相关的新闻列表
    related_news = await get_related_news(db, news_detail.category_id, news_detail.id)
    return {
        "code": 200,
        "message": "获取新闻详情成功",
        "data": {
            "id": news_detail.id,
            "title": news_detail.title,
            "content": news_detail.content,
            "image": news_detail.image,
            "author": news_detail.author,
            "publish_time": news_detail.publish_time,
            "categoryId": news_detail.category_id,
            "views": news_detail.views,
            "relatedNews": related_news
        }
    }
