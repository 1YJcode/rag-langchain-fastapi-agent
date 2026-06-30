from datetime import datetime

from sqlalchemy import UniqueConstraint, Index, Integer, ForeignKey, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from FastAPIUserService.models.news import News
from FastAPIUserService.models.users import User



class Base(DeclarativeBase):
    pass



class History(Base):
    """
    历史浏览表ORM模型
    """
    __tablename__ = 'history'

    # 创建索引
    # UniqueConstraint: 唯一约束，当前用户，当前新闻只能浏览记录一次
    __table_args__ = (
        UniqueConstraint('user_id', 'news_id', name='user_news_unique'),
        Index('fk_history_user_idx', 'user_id'),
        Index('fk_history_news_idx', 'news_id')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment='历史浏览ID')
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey(User.id), nullable=False, comment='用户ID')
    news_id: Mapped[int] = mapped_column(Integer, ForeignKey(News.id), nullable=False, comment='新闻ID')
    view_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False, comment='浏览时间')

    def __repr__(self):
        return f"<Favorite(id={self.id}, user_id={self.user_id}, news_id={self.news_id}, created_at={self.view_time})>"