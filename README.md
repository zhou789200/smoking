# CampusGuard · 校园吸烟检测系统

基于 **Vue 3 + FastAPI** 的校园吸烟检测系统 — 前端展示 + 后端 API 完整架构。

## 项目结构

```
smoking01/
├── backend/                 # FastAPI 后端
│   ├── app/
│   │   ├── main.py          # 应用入口
│   │   ├── config.py        # 配置
│   │   ├── database.py      # 数据库连接
│   │   ├── models/          # SQLAlchemy 数据模型
│   │   ├── schemas/         # Pydantic 请求/响应模型
│   │   ├── routers/         # API 路由
│   │   └── services/        # 业务逻辑层
│   └── requirements.txt
└── frontend/                # Vue 3 前端
    ├── src/
    │   ├── api/             # API 请求封装
    │   ├── router/          # Vue Router 路由
    │   ├── views/           # 页面组件
    │   ├── components/      # 公共组件
    │   ├── App.vue
    │   └── main.ts
    ├── package.json
    └── vite.config.ts
```

## 启动方式

### 1. 后端

```bash
cd backend

# 创建虚拟环境（推荐）
python -m venv .venv
.venv\Scripts\activate      # Windows
# source .venv/bin/activate # macOS/Linux

# 安装依赖
pip install -r requirements.txt

# 启动
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

后端运行在 `http://localhost:8000`
API 文档：`http://localhost:8000/docs`

### 2. 前端

```bash
cd frontend

# 安装依赖
npm i

# 启动开发服务器
npm run dev
```

前端运行在 `http://localhost:5173`，已配置代理转发 `/api` 请求到后端。

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/cameras/` | 获取摄像头列表 |
| POST | `/api/cameras/` | 新增摄像头 |
| GET | `/api/alerts/` | 获取告警列表 |
| POST | `/api/alerts/` | 创建告警记录 |
| PATCH | `/api/alerts/{id}` | 更新告警状态 |
| GET | `/api/stats/` | 获取系统统计 |
| GET | `/api/alerts/daily` | 获取每日告警统计 |

## 技术栈

- **前端**: Vue 3 + TypeScript + Vite + TailwindCSS v4 + Vue Router + Axios + Lucide Icons
- **后端**: FastAPI + SQLAlchemy (async) + PostgreSQL (asyncpg) + Pydantic
- **数据库**: PostgreSQL（推荐本地安装或使用 Docker 运行）

## PostgreSQL 配置

### 使用 Docker 快速启动

```bash
docker run -d --name campus-pg -p 5432:5432 -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=campus_guard postgres:17
```

### 本地安装

1. 安装 PostgreSQL 15+
2. 创建数据库：`CREATE DATABASE campus_guard;`
3. 通过环境变量自定义连接：
   ```bash
   set CG_DATABASE_URL=postgresql+asyncpg://user:pass@host:port/dbname
   ```
   或
   ```bash
   export CG_DATABASE_URL=postgresql+asyncpg://user:pass@host:port/dbname
   ```

