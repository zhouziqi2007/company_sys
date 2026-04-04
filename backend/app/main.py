from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from app.database import engine, Base
from app.models.models import User, Company, Task, TaskLog, Document, BankAccount, PhoneNumber, EmailAccount, Product, ProductBarcode
from app.routers import auth, users, companies, tasks, documents, bank_accounts, phone_pool, email_pool, products
from app.auth import hash_password

app = FastAPI(title="任务分发及资料管理系统", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件(本地存储用)
uploads_dir = os.path.join(os.path.dirname(__file__), "..", "uploads")
os.makedirs(uploads_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

# 注册路由
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(companies.router)
app.include_router(tasks.router)
app.include_router(documents.router)
app.include_router(bank_accounts.router)
app.include_router(phone_pool.router)
app.include_router(email_pool.router)
app.include_router(products.router)


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    # 创建默认管理员
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        if not db.query(User).filter(User.username == "admin").first():
            admin = User(
                username="admin",
                password_hash=hash_password("admin123"),
                real_name="系统管理员",
                role="admin",
            )
            db.add(admin)
            db.commit()
    finally:
        db.close()


@app.get("/api/health")
def health():
    return {"status": "ok"}
