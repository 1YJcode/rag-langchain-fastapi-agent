from fastapi import FastAPI
from FastAPIUserService.routers import auth, favorite, history, news, users
from fastapi.middleware.cors import CORSMiddleware
from FastAPIUserService.utils.exception import global_exception_handlers
import logging


# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()


from fastapi.staticfiles import StaticFiles
import os

# 使用绝对路径挂载静态文件，避免 CWD 不同导致路径不一致
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")


# 解决跨域问题
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有HTTP方法
    allow_headers=["*"],  # 允许所有HTTP头
)

# ✅ 一行代码注册所有异常处理器
logger.info("注册全局异常处理器...")
global_exception_handlers(app)
logger.info("全局异常处理器注册完成")

@app.get("/")
async def root():
    return {"message": "Hello World!"}


app.include_router(auth.router)
app.include_router(news.router)
app.include_router(users.router)
app.include_router(favorite.router)
app.include_router(history.router)