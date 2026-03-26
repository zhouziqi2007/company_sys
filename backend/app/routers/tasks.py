import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Task, TaskLog, User, Company
from app.schemas import TaskCreate, TaskUpdate, TaskOut, TaskLogOut, PageResponse
from app.auth import get_current_user

router = APIRouter(prefix="/api/tasks", tags=["任务管理"])


def _task_to_out(task: Task) -> dict:
    d = TaskOut.model_validate(task).model_dump()
    d["company_name"] = task.company.name if task.company else ""
    d["assignee_name"] = task.assignee.real_name if task.assignee else ""
    d["creator_name"] = task.creator.real_name if task.creator else ""
    return d


@router.get("", response_model=PageResponse)
def list_tasks(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: str = "",
    status: str = "",
    task_type: str = "",
    assignee_id: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(Task)
    if keyword:
        query = query.filter(Task.title.contains(keyword))
    if status:
        query = query.filter(Task.status == status)
    if task_type:
        query = query.filter(Task.task_type == task_type)
    if assignee_id:
        query = query.filter(Task.assignee_id == assignee_id)
    # 普通员工只看自己的任务
    if current_user.role == "staff":
        query = query.filter(
            (Task.assignee_id == current_user.id) | (Task.creator_id == current_user.id)
        )
    total = query.count()
    items = query.order_by(Task.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return PageResponse(
        items=[_task_to_out(t) for t in items],
        total=total, page=page, page_size=page_size
    )


@router.get("/{task_id}")
def get_task(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    return _task_to_out(task)


@router.post("")
def create_task(req: TaskCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    company = db.query(Company).filter(Company.id == req.company_id).first()
    if not company:
        raise HTTPException(status_code=400, detail="关联公司不存在")
    task = Task(**req.model_dump(), creator_id=current_user.id, status="pending")
    db.add(task)
    db.flush()
    # 记录日志
    log = TaskLog(task_id=task.id, operator_id=current_user.id, action="create", content="创建任务")
    db.add(log)
    db.commit()
    db.refresh(task)
    return _task_to_out(task)


@router.put("/{task_id}")
def update_task(task_id: int, req: TaskUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    changes = []
    for field, value in req.model_dump(exclude_unset=True).items():
        old_val = getattr(task, field)
        if old_val != value:
            changes.append(f"{field}: {old_val} -> {value}")
            setattr(task, field, value)
    if task.status == "completed" and task.completed_at is None:
        task.completed_at = datetime.datetime.utcnow()
    if changes:
        log = TaskLog(task_id=task.id, operator_id=current_user.id, action="update", content="; ".join(changes))
        db.add(log)
    db.commit()
    db.refresh(task)
    return _task_to_out(task)


@router.post("/{task_id}/assign")
def assign_task(task_id: int, assignee_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    assignee = db.query(User).filter(User.id == assignee_id, User.is_active == True).first()
    if not assignee:
        raise HTTPException(status_code=400, detail="指定员工不存在")
    task.assignee_id = assignee_id
    task.status = "in_progress"
    log = TaskLog(task_id=task.id, operator_id=current_user.id, action="assign", content=f"分配给 {assignee.real_name}")
    db.add(log)
    db.commit()
    return {"message": "分配成功"}


@router.get("/{task_id}/logs", response_model=list[TaskLogOut])
def task_logs(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    logs = db.query(TaskLog).filter(TaskLog.task_id == task_id).order_by(TaskLog.created_at.desc()).all()
    result = []
    for l in logs:
        d = TaskLogOut.model_validate(l).model_dump()
        d["operator_name"] = l.operator.real_name if l.operator else ""
        result.append(d)
    return result


@router.delete("/{task_id}")
def delete_task(task_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    db.delete(task)
    db.commit()
    return {"message": "已删除"}


@router.get("/stats/overview")
def task_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """仪表盘统计"""
    from sqlalchemy import func
    total = db.query(func.count(Task.id)).scalar()
    pending = db.query(func.count(Task.id)).filter(Task.status == "pending").scalar()
    in_progress = db.query(func.count(Task.id)).filter(Task.status == "in_progress").scalar()
    completed = db.query(func.count(Task.id)).filter(Task.status == "completed").scalar()
    company_count = db.query(func.count(Company.id)).scalar()
    user_count = db.query(func.count(User.id)).filter(User.is_active == True).scalar()
    return {
        "task_total": total,
        "task_pending": pending,
        "task_in_progress": in_progress,
        "task_completed": completed,
        "company_count": company_count,
        "user_count": user_count,
    }
