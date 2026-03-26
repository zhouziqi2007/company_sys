# 任务分发及资料管理系统

代理注册登记公司专用的任务分发与公司资料管理系统，支持多员工协同操作。

## 系统功能

### 核心模块
| 模块 | 功能说明 |
|------|---------|
| **工作台** | 数据统计概览、待办任务、最近公司资料 |
| **公司资料** | 公司信息CRUD、营业执照状态跟踪、银行公户状态跟踪 |
| **任务管理** | 创建/分配/流转任务、关联公司、任务日志追踪 |
| **文件管理** | 上传/下载/分类管理文件（身份证、营业执照、银行资料、合同等） |
| **员工管理** | 用户管理、角色权限（管理员/主管/员工） |

### 任务流转
```
待处理 → 进行中 → 已提交 → 已审核 → 已完成
                          ↘ 已驳回 ↗
```

### 角色权限
- **管理员(admin)**: 所有权限，包括员工管理
- **主管(manager)**: 查看所有任务和公司，分配任务
- **员工(staff)**: 只能查看自己负责/创建的任务

## 技术栈

- **前端**: Vue 3 + Element Plus + Pinia + Vue Router
- **后端**: Python FastAPI + SQLAlchemy
- **数据库**: MySQL 8.0
- **文件存储**: 阿里云OSS / 腾讯云COS / 七牛云（可切换）

## 项目结构

```
company_sys/
├── backend/                 # Python后端
│   ├── app/
│   │   ├── main.py         # FastAPI入口
│   │   ├── config.py       # 配置管理
│   │   ├── database.py     # 数据库连接
│   │   ├── auth.py         # JWT认证
│   │   ├── storage.py      # 云存储抽象层
│   │   ├── schemas.py      # Pydantic数据模型
│   │   ├── models/
│   │   │   └── models.py   # SQLAlchemy数据表模型
│   │   └── routers/        # API路由
│   │       ├── auth.py     # 认证接口
│   │       ├── users.py    # 员工管理
│   │       ├── companies.py# 公司资料
│   │       ├── tasks.py    # 任务管理
│   │       └── documents.py# 文件管理
│   ├── requirements.txt
│   └── .env.example
└── frontend/                # Vue3前端
    ├── src/
    │   ├── main.js
    │   ├── App.vue
    │   ├── router/         # 路由配置
    │   ├── stores/         # Pinia状态管理
    │   ├── utils/          # API封装
    │   ├── layout/         # 布局组件
    │   └── views/          # 页面
    │       ├── Login.vue
    │       ├── Dashboard.vue
    │       ├── Companies.vue
    │       ├── Tasks.vue
    │       ├── Documents.vue
    │       └── Users.vue
    ├── package.json
    └── vite.config.js
```

## 快速开始

### 1. 数据库准备
```sql
CREATE DATABASE company_sys DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 2. 后端启动
```bash
cd backend
cp .env.example .env      # 编辑.env填写数据库密码和云存储配置
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
> 首次启动会自动建表和创建管理员账号: `admin / admin123`

### 3. 前端启动
```bash
cd frontend
npm install
npm run dev
```
访问 http://localhost:3000

## 云存储配置

在 `.env` 中设置 `STORAGE_PROVIDER` 来切换存储后端：

| 值 | 说明 |
|----|------|
| `aliyun` | 阿里云OSS |
| `tencent` | 腾讯云COS |
| `qiniu` | 七牛云 |
| `local` | 本地存储（开发测试用） |

开发阶段可使用 `STORAGE_PROVIDER=local`，文件存储在 `backend/uploads/` 目录。

## API文档

启动后端后访问: http://localhost:8000/docs （Swagger自动生成）

## 默认账号

| 用户名 | 密码 | 角色 |
|--------|------|------|
| admin | admin123 | 管理员 |

> ⚠️ 生产环境请务必修改默认密码和 SECRET_KEY