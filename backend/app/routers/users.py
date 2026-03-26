from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import User
from app.schemas import UserCreate, UserUpdate, UserOut, PageResponse
from app.auth import hash_password, get_current_user, require_role

router = APIRouter(prefix="/api/users", tags=["员工管理"])


@router.get("", response_model=PageResponse)
def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: str = "",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(User)
    if keyword:
        query = query.filter(
            (User.real_name.contains(keyword)) | (User.username.contains(keyword))
        )
    total = query.count()
    items = query.order_by(User.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return PageResponse(
        items=[UserOut.model_validate(u) for u in items],
        total=total, page=page, page_size=page_size
    )


@router.post("", response_model=UserOut)
def create_user(
    req: UserCreate,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    if db.query(User).filter(User.username == req.username).first():
        raise HTTPException(status_code=400, detail="用户名已存在")
    user = User(
        username=req.username,
        password_hash=hash_password(req.password),
        real_name=req.real_name,
        phone=req.phone or "",
        role=req.role or "staff",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.put("/{user_id}", response_model=UserOut)
def update_user(
    user_id: int,
    req: UserUpdate,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    for field, value in req.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="不能删除自己")
    user.is_active = False
    db.commit()
    return {"message": "已禁用"}


@router.get("/options")
def user_options(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """获取员工下拉选项"""
    users = db.query(User).filter(User.is_active == True).all()
    return [{"id": u.id, "real_name": u.real_name, "role": u.role} for u in users]
