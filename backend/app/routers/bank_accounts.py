from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.models.models import BankAccount, Document, User, Company
from app.schemas import BankAccountCreate, BankAccountUpdate, BankAccountOut, DocumentOut, PageResponse
from app.auth import get_current_user
from app.storage import get_storage, generate_storage_key

router = APIRouter(prefix="/api/bank-accounts", tags=["银行资料"])


@router.get("", response_model=PageResponse)
def list_bank_accounts(
    company_id: int = 0,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: str = "",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(BankAccount)
    if company_id:
        query = query.filter(BankAccount.company_id == company_id)
    if keyword:
        query = query.filter(
            (BankAccount.bank_name.contains(keyword))
            | (BankAccount.account_number.contains(keyword))
            | (BankAccount.label.contains(keyword))
        )
    total = query.count()
    items = query.order_by(BankAccount.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return PageResponse(
        items=[BankAccountOut.model_validate(b) for b in items],
        total=total, page=page, page_size=page_size
    )


@router.get("/{bank_id}", response_model=BankAccountOut)
def get_bank_account(bank_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    bank = db.query(BankAccount).filter(BankAccount.id == bank_id).first()
    if not bank:
        raise HTTPException(status_code=404, detail="银行资料不存在")
    return bank


@router.post("", response_model=BankAccountOut)
def create_bank_account(req: BankAccountCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    company = db.query(Company).filter(Company.id == req.company_id).first()
    if not company:
        raise HTTPException(status_code=400, detail="关联公司不存在")
    bank = BankAccount(**req.model_dump(), created_by=current_user.id)
    db.add(bank)
    db.commit()
    db.refresh(bank)
    return bank


@router.put("/{bank_id}", response_model=BankAccountOut)
def update_bank_account(bank_id: int, req: BankAccountUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    bank = db.query(BankAccount).filter(BankAccount.id == bank_id).first()
    if not bank:
        raise HTTPException(status_code=404, detail="银行资料不存在")
    for field, value in req.model_dump(exclude_unset=True).items():
        setattr(bank, field, value)
    db.commit()
    db.refresh(bank)
    return bank


@router.delete("/{bank_id}")
def delete_bank_account(bank_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    bank = db.query(BankAccount).filter(BankAccount.id == bank_id).first()
    if not bank:
        raise HTTPException(status_code=404, detail="银行资料不存在")
    db.delete(bank)
    db.commit()
    return {"message": "已删除"}


@router.post("/{bank_id}/upload", response_model=DocumentOut)
async def upload_bank_document(
    bank_id: int,
    file: UploadFile = File(...),
    category: str = Form("bank_doc"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """上传银行相关附件（截图、密钥文件等）"""
    bank = db.query(BankAccount).filter(BankAccount.id == bank_id).first()
    if not bank:
        raise HTTPException(status_code=404, detail="银行资料不存在")

    content = await file.read()
    if len(content) > 50 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="文件大小不能超过50MB")

    storage_key = generate_storage_key(file.filename, prefix=f"bank/{bank_id}")
    storage = get_storage()
    file_url = storage.upload(content, storage_key, file.content_type or "")

    doc = Document(
        filename=file.filename,
        storage_key=storage_key,
        file_url=file_url,
        file_size=len(content),
        file_type=file.content_type or "",
        category=category,
        company_id=bank.company_id,
        bank_account_id=bank_id,
        uploaded_by=current_user.id,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


@router.get("/{bank_id}/documents", response_model=list[DocumentOut])
def list_bank_documents(bank_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """获取银行账户关联的附件"""
    docs = db.query(Document).filter(Document.bank_account_id == bank_id).order_by(Document.created_at.desc()).all()
    return [DocumentOut.model_validate(d) for d in docs]
