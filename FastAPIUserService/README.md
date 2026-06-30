# FastAPIUserService — 用户微服务

用户管理、新闻资讯、收藏与历史记录服务。

## 技术栈

| 组件 | 说明 |
|---|---|
| FastAPI | Web 框架，端口 8000 |
| SQLAlchemy | ORM (异步) |
| MySQL / MariaDB | 数据库 |
| Redis | 缓存 / 会话 |
| python-docx | DOCX 头像处理 |
| JWT | 用户认证 |

## 项目结构

```
FastAPIUserService/
├── routers/
│   ├── auth.py              # 注册 / 登录 / Token 验证
│   ├── users.py             # 用户信息 / 头像上传
│   ├── news.py              # 新闻分类 / 列表 / 详情
│   ├── favorite.py          # 收藏 / 取消收藏
│   └── history.py           # 浏览历史
├── crud/
│   ├── users.py             # 用户 DB 操作
│   ├── news.py              # 新闻 DB 操作
│   ├── favorite.py          # 收藏 DB 操作
│   └── history.py           # 历史 DB 操作
├── models/
│   ├── users.py             # 用户模型
│   ├── news.py              # 新闻模型
│   ├── favorite.py          # 收藏模型
│   └── history.py           # 历史模型
├── schemas/                 # Pydantic 数据模型
├── utils/
│   ├── auth.py              # Token 验证依赖
│   ├── upload_avatar.py     # 头像上传 (python-docx)
│   ├── cache.py             # Redis 缓存
│   └── exception.py         # 全局异常处理
├── config/
│   ├── db_config.py         # 数据库连接
│   └── cache_conf.py        # 缓存配置
├── static/avatars/          # 头像文件存储
└── main.py                  # 服务入口
```

## API 接口

### 用户认证

| 方法 | 路径 | 说明 |
|---|---|---|
| POST | `/api/user/register` | 注册 |
| POST | `/api/user/login` | 登录 |
| POST | `/api/v1/auth/verify` | Token 验证 |
| PUT | `/api/user/password` | 修改密码 |

### 用户信息

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/user/info` | 获取用户信息 |
| PUT | `/api/user/update` | 更新资料 |
| POST | `/api/user/upload-avatar` | 上传头像 |

### 新闻

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/news/categories` | 新闻分类列表 |
| GET | `/api/news/list` | 新闻列表 (分页) |
| GET | `/api/news/detail` | 新闻详情 (含相关推荐) |

### 收藏

| 方法 | 路径 | 说明 |
|---|---|---|
| POST | `/api/favorite/add` | 添加收藏 |
| DELETE | `/api/favorite/remove` | 取消收藏 |
| GET | `/api/favorite/check` | 检查收藏状态 |
| GET | `/api/favorite/list` | 收藏列表 |

### 历史

| 方法 | 路径 | 说明 |
|---|---|---|
| POST | `/api/history/add` | 添加浏览记录 |
| GET | `/api/history/list` | 历史记录列表 |
| DELETE | `/api/history/clear` | 清除历史 |

## 静态文件

头像文件存储在 `static/avatars/`，通过 FastAPI `StaticFiles` 挂载在 `/static` 路径下。
