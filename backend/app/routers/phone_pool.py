"""电话号码库"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.database import get_db
from app.auth import get_current_user, require_role
from app.models.models import PhoneNumber, User, Company, BankAccount
from app.schemas import (
    PhoneNumberCreate, PhoneNumberBatchCreate, PhoneNumberClaim,
    PhoneNumberOut, PageResponse,
)

router = APIRouter(prefix="/api/phone-pool", tags=["电话库"])


def _to_out(p: PhoneNumber) -> dict:
    d = {
        "id": p.id,
        "phone_number": p.phone_number,
        "sms_api": p.sms_api or "",
        "status": p.status,
        "claimed_by": p.claimed_by,
        "claimer_name": p.claimer.real_name if p.claimer else "",
        "company_id": p.company_id,
        "company_name": p.company.name if p.company else "",
        "bank_account_id": p.bank_account_id,
        "bank_label": p.bank_label or "",
        "remark": p.remark or "",
        "created_at": p.created_at,
    }
    return d


@router.get("", response_model=PageResponse)
def list_phones(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: str = "",
    status: str = "",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    q = db.query(PhoneNumber)
    if keyword:
        q = q.filter(
            or_(
                PhoneNumber.phone_number.contains(keyword),
                PhoneNumber.bank_label.contains(keyword),
                PhoneNumber.remark.contains(keyword),
            )
        )
    if status:
        q = q.filter(PhoneNumber.status == status)
    total = q.count()
    items = q.order_by(PhoneNumber.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return {"items": [_to_out(i) for i in items], "total": total, "page": page, "page_size": page_size}


@router.post("")
def create_phone(
    data: PhoneNumberCreate,
    current_user: User = Depends(require_role("admin", "manager")),
    db: Session = Depends(get_db),
):
    if db.query(PhoneNumber).filter(PhoneNumber.phone_number == data.phone_number).first():
        raise HTTPException(400, "该电话号码已存在")
    p = PhoneNumber(
        phone_number=data.phone_number,
        sms_api=data.sms_api,
        remark=data.remark,
        created_by=current_user.id,
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    return _to_out(p)


@router.post("/batch")
def batch_create_phones(
    data: PhoneNumberBatchCreate,
    current_user: User = Depends(require_role("admin", "manager")),
    db: Session = Depends(get_db),
):
    created = 0
    skipped = 0
    for phone in data.phones:
        phone = phone.strip()
        if not phone:
            continue
        if db.query(PhoneNumber).filter(PhoneNumber.phone_number == phone).first():
            skipped += 1
            continue
        p = PhoneNumber(
            phone_number=phone,
            sms_api=data.sms_api,
            created_by=current_user.id,
        )
        db.add(p)
        created += 1
    db.commit()
    return {"created": created, "skipped": skipped}


@router.post("/{phone_id}/claim")
def claim_phone(
    phone_id: int,
    data: PhoneNumberClaim,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    p = db.query(PhoneNumber).filter(PhoneNumber.id == phone_id).first()
    if not p:
        raise HTTPException(404, "号码不存在")
    if p.status == "claimed":
        raise HTTPException(400, "该号码已被领用")
    # 验证公司
    company = db.query(Company).filter(Company.id == data.company_id).first()
    if not company:
        raise HTTPException(404, "公司不存在")
    # 验证银行（可选）
    if data.bank_account_id:
        ba = db.query(BankAccount).filter(
            BankAccount.id == data.bank_account_id,
            BankAccount.company_id == data.company_id,
        ).first()
        if not ba:
            raise HTTPException(404, "银行账户不存在或不属于该公司")
    p.status = "claimed"
    p.claimed_by = current_user.id
    p.company_id = data.company_id
    p.bank_account_id = data.bank_account_id
    p.bank_label = data.bank_label
    db.commit()
    db.refresh(p)
    return _to_out(p)


@router.post("/{phone_id}/release")
def release_phone(
    phone_id: int,
    current_user: User = Depends(require_role("admin", "manager")),
    db: Session = Depends(get_db),
):
    p = db.query(PhoneNumber).filter(PhoneNumber.id == phone_id).first()
    if not p:
        raise HTTPException(404, "号码不存在")
    if p.status != "claimed":
        raise HTTPException(400, "该号码未被领用")
    p.status = "available"
    p.claimed_by = None
    p.company_id = None
    p.bank_account_id = None
    p.bank_label = ""
    db.commit()
    db.refresh(p)
    return _to_out(p)


@router.put("/{phone_id}")
def update_phone(
    phone_id: int,
    data: PhoneNumberCreate,
    current_user: User = Depends(require_role("admin", "manager")),
    db: Session = Depends(get_db),
):
    p = db.query(PhoneNumber).filter(PhoneNumber.id == phone_id).first()
    if not p:
        raise HTTPException(404, "号码不存在")
    # 如果修改号码，检查唯一性
    if data.phone_number != p.phone_number:
        existing = db.query(PhoneNumber).filter(PhoneNumber.phone_number == data.phone_number).first()
        if existing:
            raise HTTPException(400, "该电话号码已存在")
        p.phone_number = data.phone_number
    p.sms_api = data.sms_api
    p.remark = data.remark
    db.commit()
    db.refresh(p)
    return _to_out(p)


@router.delete("/{phone_id}")
def delete_phone(
    phone_id: int,
    current_user: User = Depends(require_role("admin", "manager")),
    db: Session = Depends(get_db),
):
    p = db.query(PhoneNumber).filter(PhoneNumber.id == phone_id).first()
    if not p:
        raise HTTPException(404, "号码不存在")
    if p.status == "claimed":
        raise HTTPException(400, "已领用的号码不能删除，请先释放")
    db.delete(p)
    db.commit()
    return {"detail": "已删除"}
