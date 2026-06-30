from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

# 数据库URL，格式：数据库类型+数据库驱动名称://用户名:密码@地址:端口/数据库名
DATABASE_URL = "mysql+aiomysql://root:root@localhost:3306/news_app?charset=utf8mb4"

# 创建异步引擎
async_engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # 打印SQL语句
    pool_size=10,  # 连接池大小
    max_overflow=20,  # 超出连接池大小的最大连接数
    pool_recycle=3600,  # 每小时回收连接，防止 MySQL 断开空闲连接
    pool_pre_ping=True,  # 使用连接前先验证是否有效
)

# 创建异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,  # 提交后不失效对象
)

# 依赖项，用于获取数据库会话
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

