"""邮箱库"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.database import get_db
from app.auth import get_current_user, require_role
from app.models.models import EmailAccount, User, Company, BankAccount
from app.schemas import (
    EmailAccountCreate, EmailAccountBatchCreate, EmailAccountClaim,
    EmailAccountOut, PageResponse,
)

router = APIRouter(prefix="/api/email-pool", tags=["邮箱库"])


def _to_out(e: EmailAccount) -> dict:
    return {
        "id": e.id,
        "email": e.email,
        "password": e.password or "",
        "status": e.status,
        "claimed_by": e.claimed_by,
        "claimer_name": e.claimer.real_name if e.claimer else "",
        "company_id": e.company_id,
        "company_name": e.company.name if e.company else "",
        "bank_account_id": e.bank_account_id,
        "bank_label": e.bank_label or "",
        "remark": e.remark or "",
        "created_at": e.created_at,
    }


@router.get("", response_model=PageResponse)
def list_emails(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: str = "",
    status: str = "",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    q = db.query(EmailAccount)
    if keyword:
        q = q.filter(
            or_(
                EmailAccount.email.contains(keyword),
                EmailAccount.bank_label.contains(keyword),
                EmailAccount.remark.contains(keyword),
            )
        )
    if status:
        q = q.filter(EmailAccount.status == status)
    total = q.count()
    items = q.order_by(EmailAccount.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return {"items": [_to_out(i) for i in items], "total": total, "page": page, "page_size": page_size}


@router.post("")
def create_email(
    data: EmailAccountCreate,
    current_user: User = Depends(require_role("admin", "manager")),
    db: Session = Depends(get_db),
):
    if db.query(EmailAccount).filter(EmailAccount.email == data.email).first():
        raise HTTPException(400, "该邮箱已存在")
    e = EmailAccount(
        email=data.email,
        password=data.password,
        remark=data.remark,
        created_by=current_user.id,
    )
    db.add(e)
    db.commit()
    db.refresh(e)
    return _to_out(e)


@router.post("/batch")
def batch_create_emails(
    data: EmailAccountBatchCreate,
    current_user: User = Depends(require_role("admin", "manager")),
    db: Session = Depends(get_db),
):
    created = 0
    skipped = 0
    for item in data.emails:
        email = item.get("email", "").strip()
        password = item.get("password", "")
        if not email:
            continue
        if db.query(EmailAccount).filter(EmailAccount.email == email).first():
            skipped += 1
            continue
        e = EmailAccount(
            email=email,
            password=password,
            created_by=current_user.id,
        )
        db.add(e)
        created += 1
    db.commit()
    return {"created": created, "skipped": skipped}


@router.post("/{email_id}/claim")
def claim_email(
    email_id: int,
    data: EmailAccountClaim,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    e = db.query(EmailAccount).filter(EmailAccount.id == email_id).first()
    if not e:
        raise HTTPException(404, "邮箱不存在")
    if e.status == "claimed":
        raise HTTPException(400, "该邮箱已被领用")
    company = db.query(Company).filter(Company.id == data.company_id).first()
    if not company:
        raise HTTPException(404, "公司不存在")
    if data.bank_account_id:
        ba = db.query(BankAccount).filter(
            BankAccount.id == data.bank_account_id,
            BankAccount.company_id == data.company_id,
        ).first()
        if not ba:
            raise HTTPException(404, "银行账户不存在或不属于该公司")
    e.status = "claimed"
    e.claimed_by = current_user.id
    e.company_id = data.company_id
    e.bank_account_id = data.bank_account_id
    e.bank_label = data.bank_label
    db.commit()
    db.refresh(e)
    return _to_out(e)


@router.post("/{email_id}/release")
def release_email(
    email_id: int,
    current_user: User = Depends(require_role("admin", "manager")),
    db: Session = Depends(get_db),
):
    e = db.query(EmailAccount).filter(EmailAccount.id == email_id).first()
    if not e:
        raise HTTPException(404, "邮箱不存在")
    if e.status != "claimed":
        raise HTTPException(400, "该邮箱未被领用")
    e.status = "available"
    e.claimed_by = None
    e.company_id = None
    e.bank_account_id = None
    e.bank_label = ""
    db.commit()
    db.refresh(e)
    return _to_out(e)


@router.put("/{email_id}")
def update_email(
    email_id: int,
    data: EmailAccountCreate,
    current_user: User = Depends(require_role("admin", "manager")),
    db: Session = Depends(get_db),
):
    e = db.query(EmailAccount).filter(EmailAccount.id == email_id).first()
    if not e:
        raise HTTPException(404, "邮箱不存在")
    if data.email != e.email:
        existing = db.query(EmailAccount).filter(EmailAccount.email == data.email).first()
        if existing:
            raise HTTPException(400, "该邮箱已存在")
        e.email = data.email
    e.password = data.password
    e.remark = data.remark
    db.commit()
    db.refresh(e)
    return _to_out(e)


@router.delete("/{email_id}")
def delete_email(
    email_id: int,
    current_user: User = Depends(require_role("admin", "manager")),
    db: Session = Depends(get_db),
):
    e = db.query(EmailAccount).filter(EmailAccount.id == email_id).first()
    if not e:
        raise HTTPException(404, "邮箱不存在")
    if e.status == "claimed":
        raise HTTPException(400, "已领用的邮箱不能删除，请先释放")
    db.delete(e)
    db.commit()
    return {"detail": "已删除"}
