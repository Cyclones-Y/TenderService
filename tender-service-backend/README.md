# Tender Service Backend（招投标系统后端）

基于 FastAPI 的招投标业务后端，采用分层架构与模块化设计，支持 MySQL/PostgreSQL 双数据库、Redis 缓存、JWT 认证、定时任务、代码生成等能力。项目以 uv 管理依赖，使用 SQLAlchemy + Alembic 进行数据库访问与迁移，具备完善的中间件、异常处理与自动路由注册机制。


## 项目定位
- 面向招投标业务的后台服务，提供用户、角色、菜单、部门、岗位、通知、日志、在线用户、缓存与服务监控等通用管理能力
- 支持多环境运行和容器化部署，内置 .env.* 环境文件与 Dockerfile
- 适配 MySQL 与 PostgreSQL，支持异步 SQLAlchemy 引擎与 Alembic 自动迁移


## 技术栈
- Web 框架：FastAPI
- ORM 与数据库迁移：SQLAlchemy（异步）、Alembic
- 认证与安全：JWT（OAuth2）、权限依赖
- 缓存与任务：Redis（aioredis）、APScheduler
- 依赖管理与锁定：uv（pyproject.toml、uv.lock）
- 日志与工具：loguru、pydantic、jinja2、openpyxl、pandas、ruff 等


## 快速开始
- 环境要求：Python 3.12、Redis、MySQL 或 PostgreSQL、uv
- 安装依赖：
  ```bash
  uv sync
  ```
- 运行开发环境：
  ```bash
  uv run python app.py --env=dev
  ```
- 接口文档：默认根路径为 `/dev-api`
  - Swagger UI: http://localhost:9099/dev-api/docs
  - ReDoc: http://localhost:9099/dev-api/redoc


## 运行与部署
- 本地运行：
  ```bash
  uv run python app.py --env=dev
  ```
- Docker（PostgreSQL 版示例）：
  ```bash
  docker build -f Dockerfile.pg -t tender-backend:pg .
  docker run -p 9099:9099 tender-backend:pg
  ```
- Docker（MySQL 版示例）：
  ```bash
  docker build -f Dockerfile.my -t tender-backend:my .
  docker run -p 9099:9099 tender-backend:my
  ```


## 目录结构
```
tender-service-backend/
├─ app.py                      # 入口，启动 uvicorn，加载 create_app
├─ server.py                   # 应用工厂，生命周期、中间件、异常、路由注册
├─ common/                     # 公共基础设施与横切模块
│  ├─ annotation/              # 自定义注解（日志等）
│  ├─ aspect/                  # 依赖、权限、数据范围、DB 会话等横切能力
│  ├─ router.py                # APIRouterPro 扩展与自动路由注册
│  ├─ context.py               # 请求上下文管理
│  ├─ constant.py/enums.py     # 常量与枚举
│  └─ vo.py                    # 响应模型基类、通用 VO
├─ config/                     # 配置与基础设施
│  ├─ env.py                   # App/JWT/DB/Redis/Upload 等配置模型与 .env 加载
│  ├─ database.py              # 异步 SQLAlchemy 引擎与 Base
│  ├─ get_db.py                # DB 依赖与建表初始化
│  ├─ get_redis.py             # Redis 连接池与系统字典/配置初始化
│  └─ get_scheduler.py         # APScheduler 初始化、存储与触发器
├─ exceptions/                 # 异常定义与全局异常处理
├─ middlewares/                # 中间件：CORS、GZip、Trace、上下文清理
├─ module_admin/               # 管理后台模块（招投标系统通用管理域）
│  ├─ controller/              # Web 层：FastAPI 控制器
│  ├─ service/                 # 业务层：领域逻辑
│  └─ entity/
│     ├─ do/                   # 数据对象（SQLAlchemy 模型）
│     └─ vo/                   # 视图对象（Pydantic 模型）
├─ module_generator/           # 代码生成器（前后端模板与生成逻辑）
├─ module_task/                # 定时任务实现示例
├─ sub_applications/           # 子应用挂载（静态文件等）
├─ utils/                      # 工具库（响应、日志、Excel、模板、分页等）
├─ sql/                        # 初始化 SQL（MySQL/PostgreSQL）
├─ pyproject.toml              # 项目依赖与开发依赖声明（uv 管理）
├─ uv.lock                     # 依赖锁文件（uv lock 生成）
├─ requirements*.txt           # pip 需求文件（可用于迁移或对照）
├─ Dockerfile.pg / Dockerfile.my  # 容器化构建（PostgreSQL/MySQL）
└─ .env.*                      # 多环境配置文件
```


## 核心架构与层次
- Web 层（Controller）
  - 位置：`module_admin/controller/*`
  - 机制：使用 `APIRouterPro`，并由 `common/router.py` 自动发现与注册，统一前缀、排序与分组标签
  - 示例：`server_controller.py`、`login_controller.py` 等

- 业务层（Service）
  - 位置：`module_admin/service/*`
  - 职责：承载核心领域逻辑、参数校验与组合调用，统一返回通用响应模型
  - 横切能力：`common/aspect` 提供 `PreAuthDependency`（认证）、`DBSessionDependency`（数据库会话）、`data_scope`（数据范围）与 `interface_auth`（接口权限）

- 数据访问层（DAO）
  - 位置：`module_admin/dao/*`
  - 机制：使用异步 SQLAlchemy 会话（`Depends(get_db)`），封装增删改查与分页
  - 初始化：应用启动时通过 `init_create_table()` 自动建表，可使用 Alembic 进行迁移管理

- 实体与模型（DO / VO）
  - DO：`module_admin/entity/do/*`，继承 `config/database.Base`，定义表结构与关系
  - VO：`module_admin/entity/vo/*`，基于 Pydantic，使用 `alias_generator=to_camel` 与 `from_attributes=True`，对外响应模型保持与前端约定的驼峰命名


## 中间件与异常
- 中间件：`middlewares/handle.py` 统一加载
  - CORS：`middlewares/cors_middleware.py`
  - GZip：`middlewares/gzip_middleware.py`
  - Trace：`middlewares/trace_middleware/*`（记录请求响应信息）
  - 上下文清理：`middlewares/context_middleware.py`（请求结束清理 `RequestContext`）
- 异常处理：`exceptions/handle.py` 注册全局异常处理器，覆盖认证、权限、服务、模型校验与通用 HTTP/Exception


## 配置管理
- `config/env.py` 使用 Pydantic Settings + dotenv 加载 `.env.<env>`，通过命令行参数 `--env` 设置运行环境
- 关键配置：
  - `AppSettings`：应用名称、版本、端口、根路径、热重载、IP 查询等
  - `JwtSettings`：`jwt_secret_key`、`jwt_algorithm`、过期时间等
  - `DataBaseSettings`：`db_type`（mysql/postgresql）、连接信息、连接池参数
  - `RedisSettings`：连接配置
  - `UploadSettings`：上传目录、允许文件类型、下载目录


## 认证与权限
- 登录与令牌：`module_admin/service/login_service.py`，支持 OAuth2 与 JWT
- 认证依赖：`common/aspect/pre_auth.py` 编译排除路由、设置当前用户
- 接口权限：`common/aspect/interface_auth.py` 提供 `UserInterfaceAuthDependency`/`RoleInterfaceAuthDependency`
- 数据范围：`common/aspect/data_scope.py` 按部门/角色控制数据访问


## 数据库与迁移
- 异步引擎：`config/database.py` 根据 `db_type` 切换 `asyncmy` / `asyncpg`
- 自动建表：应用启动执行 `init_create_table()`
- Alembic：`alembic/env.py` 配置异步引擎与模型自动发现（`utils/import_util.py`），常用命令：
  ```bash
  alembic revision --autogenerate -m "init tables"
  alembic upgrade head
  ```
- 初始化 SQL：`sql/ruoyi-fastapi.sql`（MySQL）、`sql/ruoyi-fastapi-pg.sql`（PostgreSQL）


## 定时任务（APScheduler）
- 配置：`config/get_scheduler.py`，内置 Memory/SQLAlchemy/Redis 三种 JobStore，支持 OrTrigger、CronTrigger 等
- Cron 扩展：`MyCronTrigger.from_crontab()` 支持 6/7 字段表达式与工作日处理
- 白名单与拦截：`common/constant.JobConstant` 定义任务目标白名单与违规字符串拦截
- 任务示例：`module_task/scheduler_test.py`，任务注册与启停由 `SchedulerUtil`


## 缓存与监控
- Redis：`config/get_redis.py` 管理连接池，启动加载系统字典与配置
- 监控接口：
  - 缓存监控：`module_admin/controller/cache_controller.py`
  - 服务监控：`module_admin/controller/server_controller.py`
  - 在线用户、操作日志、登录日志等：`module_admin/controller/*`


## 代码生成器
- 位置：`module_generator/*`
- 模板：`templates/python/*`、`templates/js/*`、`templates/vue/*`、`templates/sql/*`
- 目的：基于库表元数据，生成后端 CRUD、前端页面与接口，提升招投标业务的模块交付效率


## 响应与日志
- 响应封装：`utils/response_util.py` 提供统一的 `success/failure/error` 等结构化返回
- 日志：`utils/log_util.py` 初始化目录与每日错误日志，统一入口处记录生命周期与启动状态


## 依赖管理与常用命令（uv）
- 项目依赖：`pyproject.toml` 的 `[project.dependencies]`
- 开发依赖：`[dependency-groups.dev]`（如 `ruff`）
- 常用命令：
  ```bash
  # 安装/同步依赖
  uv sync
  # 锁定依赖
  uv lock
  # 新增依赖（运行时）
  uv add <package>
  # 新增依赖（开发组）
  uv add --dev <package>
  # 运行应用
  uv run python app.py --env=dev
  # 代码检查
  ruff check .
  ```


## 环境与配置文件
- `.env.dev`、`.env.prod`、`.env.dockermy`、`.env.dockerpg` 提供示例环境变量
- 通过 `--env=<env>` 切换（如 `--env=dockerpg` 与容器内环境对应）


## 招投标业务建议实践
- 按领域拆分模块（如项目、标段、投标单位、资质、评标、公告等），遵循 Controller → Service → DAO → DO/VO 分层
- 使用 `VO` 层规范对外响应结构，结合 `pydantic` 校验输入输出
- 充分利用 `APScheduler` 处理公告发布提醒、投标截止提醒、评标进度任务等
- 通过 `data_scope` 与接口权限控制不同角色（投标单位、评标专家、管理员）的数据可见性与操作权限


## 版权与许可
- 仅用于学习与企业内部项目参考，若需开源许可请根据企业政策与第三方依赖协议评估与配置
