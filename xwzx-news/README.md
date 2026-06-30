# 前端 — Vue 3 新闻与 AI 问答

基于 Vue 3 + Vant 4 的移动端新闻与 AI 问答应用。

## 技术栈

| 组件 | 说明 |
|---|---|
| Vue 3 | Composition API + `<script setup>` |
| Vant 4 | 移动端 UI 组件库 |
| Vite | 构建工具 |
| Pinia | 状态管理 |
| Vue Router | 路由 |
| marked + DOMPurify | Markdown 渲染与安全过滤 |
| Axios (fetch) | HTTP 请求 |

## 项目结构

```
xwzx-news/
├── src/
│   ├── views/
│   │   ├── Home.vue           # 首页 (新闻列表)
│   │   ├── Detail.vue         # 新闻详情 (含相关推荐)
│   │   ├── Category.vue       # 分类页
│   │   ├── AiChat.vue         # AI 问答 (核心 RAG 交互页面)
│   │   ├── Profile.vue        # 个人中心 (头像、资料编辑)
│   │   ├── Login.vue          # 登录 / 注册
│   │   ├── Favorites.vue      # 收藏列表
│   │   └── History.vue        # 浏览历史
│   ├── api/
│   │   ├── chat.js            # Agent 聊天 API
│   │   ├── vector.js          # 文档上传 API
│   │   ├── user.js            # 用户 API
│   │   ├── news.js            # 新闻 API
│   │   ├── favorite.js        # 收藏 API
│   │   └── history.js         # 历史 API
│   ├── store/
│   │   ├── index.js           # Pinia 实例
│   │   └── theme.js           # 主题状态
│   ├── router/
│   │   └── index.js           # 路由配置
│   ├── i18n/
│   │   └── index.js           # 国际化
│   ├── App.vue                # 根组件
│   └── main.js                # 入口
├── vite.config.js             # Vite 配置 (代理)
├── index.html
└── package.json
```

## 页面功能

### AI 问答 (`AiChat.vue`)

- **流式问答**：SSE 逐字符流式响应
- **Markdown 渲染**：回答以 Markdown 格式展示（标题、列表、代码块等）
- **文档上传**：支持 TXT / PDF / DOCX / MD / PPTX，按会话隔离
- **会话管理**：历史会话列表、切换、删除
- **会话自动恢复**：刷新页面自动加载上次对话
- **工具调用提示**：显示 Agent 当前正在调用的工具

### 新闻 (`Home.vue`, `Detail.vue`)

- 分类切换
- 分页加载
- 新闻详情（含相关推荐，可点击切换）
- 收藏 / 取消收藏
- 浏览历史记录

### 个人中心 (`Profile.vue`)

- 头像编辑（预设头像 / 本地相册 / 自定义链接）
- 昵称、简介、性别修改
- 密码修改
- 退出登录

## 路由

| 路径 | 页面 |
|---|---|
| `/` | 首页 |
| `/home` | 首页 |
| `/category` | 分类 |
| `/category/:id` | 分类详情 |
| `/ai-chat` | AI 问答 |
| `/detail/:id` | 新闻详情 |
| `/profile` | 个人中心 |
| `/login` | 登录 |
| `/favorites` | 收藏列表 |
| `/history` | 浏览历史 |

## Vite 代理配置

`vite.config.js` 中配置了 API 代理：

| 前缀 | 目标 |
|---|---|
| `/api` | `http://127.0.0.1:8000` (用户服务) |
| `/static` | `http://127.0.0.1:8000` (静态文件) |

Agent 问答 API 直连 `http://localhost:8001`（不经过 Vite 代理）。

## 开发

```bash
# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 构建
npm run build
```
