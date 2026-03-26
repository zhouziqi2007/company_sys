from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Document, User
from app.schemas import DocumentOut, PageResponse
from app.auth import get_current_user
from app.storage import get_storage, generate_storage_key

router = APIRouter(prefix="/api/documents", tags=["文件管理"])

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB


@router.post("", response_model=DocumentOut)
async def upload_document(
    file: UploadFile = File(...),
    category: str = Form("other"),
    company_id: int = Form(0),
    task_id: int = Form(0),
    bank_account_id: int = Form(0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="文件大小不能超过50MB")

    storage_key = generate_storage_key(file.filename, prefix=f"docs/{category}")
    storage = get_storage()
    file_url = storage.upload(content, storage_key, file.content_type or "")

    doc = Document(
        filename=file.filename,
        storage_key=storage_key,
        file_url=file_url,
        file_size=len(content),
        file_type=file.content_type or "",
        category=category,
        company_id=company_id if company_id else None,
        task_id=task_id if task_id else None,
        bank_account_id=bank_account_id if bank_account_id else None,
        uploaded_by=current_user.id,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


@router.get("", response_model=PageResponse)
def list_documents(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    company_id: int = 0,
    task_id: int = 0,
    category: str = "",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(Document)
    if company_id:
        query = query.filter(Document.company_id == company_id)
    if task_id:
        query = query.filter(Document.task_id == task_id)
    if category:
        query = query.filter(Document.category == category)
    total = query.count()
    items = query.order_by(Document.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return PageResponse(
        items=[DocumentOut.model_validate(d) for d in items],
        total=total, page=page, page_size=page_size
    )


@router.delete("/{doc_id}")
def delete_document(doc_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="文件不存在")
    try:
        storage = get_storage()
        storage.delete(doc.storage_key)
    except Exception:
        pass
    db.delete(doc)
    db.commit()
    return {"message": "已删除"}
