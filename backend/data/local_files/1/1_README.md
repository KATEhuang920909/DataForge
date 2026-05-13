# DataForge ⚡

专业级数据管理工具 — 前后端分离架构

## 技术栈

| 层级 | 技术 |
|------|------|
| **后端** | Python 3.9+ / FastAPI / SQLAlchemy / SQLite |
| **前端** | Vue 3 / TypeScript / Vite / TailwindCSS |
| **特性** | RESTful API / CORS / 分页 / 软删除 / 操作日志 / JSON 数据存储 |

## 项目结构

```


PyCharmMiscProject/
├── backend/
│   ├── main.py              # 入口
│   ├── requirements.txt     # Python 依赖
│   ├── venv/                # 虚拟环境
│   └── app/
│       ├── api/             # 路由层 (Sources / Records / Logs)
│       ├── core/            # 配置 & 数据库连接
│       ├── models/          # SQLAlchemy ORM 模型
│       ├── schemas/         # Pydantic 请求/响应模型
│       └── services/        # 业务逻辑层
├── frontend/
│   ├── src/
│   │   ├── api/             # Axios HTTP 客户端
│   │   ├── components/      # 通用组件 (Modal / Pagination / Toast)
│   │   ├── views/           # 页面 (Sources / Records / Logs)
│   │   └── types/           # TypeScript 类型定义
│   └── package.json
└── start.sh                 # 一键启动脚本
```

## 快速启动

```bash
# 一键启动（后端 + 前端）
chmod +x start.sh && ./start.sh
```

或手动启动：

```bash
# 后端 (http://localhost:8000)
cd backend
source venv/bin/activate
python main.py

# 前端 (http://localhost:5173)
cd frontend
npm install
npm run dev
```

## API 文档

启动后端后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 功能

- **数据源管理** — 创建/编辑/删除/启停数据集合
- **数据记录** — JSON 格式数据的 CRUD，支持标签和搜索
- **操作日志** — 所有写操作自动记录审计日志
- **分页** — 全接口分页支持
- **软删除** — 数据记录支持安全删除与恢复
## Docker 部署

我们提供了一个基于 Docker Compose 的一键部署方案，可以轻松地在任何支持 Docker 的环境中启动整个应用。

### 先决条件

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

### 快速启动

1.  **构建并启动服务**

    在项目根目录下，执行以下命令：

    ```bash
    docker-compose up --build
    ```

    该命令会：
    -   构建后端和前端的 Docker 镜像。
    -   启动数据库、后端和前端三个服务。
    -   在后台持续运行。

2.  **访问应用**

    -   前端应用将在 [http://localhost:5173](http://localhost:5173) 上可用。
    -   后端 API 将在 [http://localhost:8000](http://localhost:8000) 上可用。

3.  **停止服务**

    要停止所有正在运行的服务，请在项目根目录下执行：

    ```bash
    docker-compose down
    ```