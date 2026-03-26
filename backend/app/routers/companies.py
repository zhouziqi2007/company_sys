from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Company, User
from app.schemas import CompanyCreate, CompanyUpdate, CompanyOut, PageResponse
from app.auth import get_current_user

router = APIRouter(prefix="/api/companies", tags=["公司资料"])


@router.get("", response_model=PageResponse)
def list_companies(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: str = "",
    license_status: str = "",
    bank_account_status: str = "",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(Company)
    if keyword:
        query = query.filter(
            (Company.name.contains(keyword))
            | (Company.first_name.contains(keyword))
            | (Company.last_name.contains(keyword))
            | (Company.unified_code.contains(keyword))
            | (Company.ssn.contains(keyword))
            | (Company.email.contains(keyword))
        )
    if license_status:
        query = query.filter(Company.license_status == license_status)
    if bank_account_status:
        query = query.filter(Company.bank_account_status == bank_account_status)
    total = query.count()
    items = query.order_by(Company.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return PageResponse(
        items=[CompanyOut.model_validate(c) for c in items],
        total=total, page=page, page_size=page_size
    )


@router.get("/{company_id}", response_model=CompanyOut)
def get_company(company_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="公司不存在")
    return company


@router.post("", response_model=CompanyOut)
def create_company(req: CompanyCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    company = Company(**req.model_dump(), created_by=current_user.id)
    db.add(company)
    db.commit()
    db.refresh(company)
    return company


@router.put("/{company_id}", response_model=CompanyOut)
def update_company(company_id: int, req: CompanyUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="公司不存在")
    for field, value in req.model_dump(exclude_unset=True).items():
        setattr(company, field, value)
    db.commit()
    db.refresh(company)
    return company


@router.delete("/{company_id}")
def delete_company(company_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="公司不存在")
    db.delete(company)
    db.commit()
    return {"message": "已删除"}
