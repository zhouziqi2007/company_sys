"""产品及条码管理"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import or_
from app.database import get_db
from app.auth import get_current_user, require_role
from app.models.models import Product, ProductBarcode, User, Company
from app.schemas import (
    ProductCreate, ProductUpdate, ProductOut, ProductBarcodeOut, PageResponse,
)

router = APIRouter(prefix="/api/products", tags=["产品条码"])


def _to_out(p: Product) -> dict:
    return {
        "id": p.id,
        "name": p.name,
        "description": p.description or "",
        "company_id": p.company_id,
        "company_name": p.company.name if p.company else "",
        "remark": p.remark or "",
        "barcodes": [
            {
                "id": b.id,
                "barcode": b.barcode,
                "label": b.label or "",
                "created_at": b.created_at,
            }
            for b in p.barcodes
        ],
        "created_at": p.created_at,
    }


@router.get("", response_model=PageResponse)
def list_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: str = "",
    company_id: int = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    q = db.query(Product).options(selectinload(Product.barcodes), selectinload(Product.company))
    if keyword:
        # 同时搜索产品名称和条码
        barcode_product_ids = (
            db.query(ProductBarcode.product_id)
            .filter(ProductBarcode.barcode.contains(keyword))
            .subquery()
        )
        q = q.filter(
            or_(
                Product.name.contains(keyword),
                Product.description.contains(keyword),
                Product.id.in_(barcode_product_ids),
            )
        )
    if company_id:
        q = q.filter(Product.company_id == company_id)
    total = q.count()
    items = (
        q.order_by(Product.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return {
        "items": [_to_out(i) for i in items],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/scan")
def scan_barcode(
    barcode: str = Query(..., min_length=1),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """扫描条码查找产品 - 输入任意一个条码即可找到对应产品及其所有条码"""
    bc = (
        db.query(ProductBarcode)
        .filter(ProductBarcode.barcode == barcode)
        .first()
    )
    if not bc:
        raise HTTPException(404, "未找到该条码对应的产品")
    product = (
        db.query(Product)
        .options(selectinload(Product.barcodes), selectinload(Product.company))
        .filter(Product.id == bc.product_id)
        .first()
    )
    return _to_out(product)


@router.post("")
def create_product(
    data: ProductCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if data.company_id:
        company = db.query(Company).filter(Company.id == data.company_id).first()
        if not company:
            raise HTTPException(404, "公司不存在")
    # 检查条码唯一性
    for bc_item in data.barcodes:
        existing = db.query(ProductBarcode).filter(ProductBarcode.barcode == bc_item.barcode).first()
        if existing:
            raise HTTPException(400, f"条码 '{bc_item.barcode}' 已被其他产品使用")
    product = Product(
        name=data.name,
        description=data.description,
        company_id=data.company_id,
        remark=data.remark,
        created_by=current_user.id,
    )
    db.add(product)
    db.flush()
    for bc_item in data.barcodes:
        bc = ProductBarcode(
            product_id=product.id,
            barcode=bc_item.barcode,
            label=bc_item.label,
        )
        db.add(bc)
    db.commit()
    db.refresh(product)
    # reload with relationships
    product = (
        db.query(Product)
        .options(selectinload(Product.barcodes), selectinload(Product.company))
        .filter(Product.id == product.id)
        .first()
    )
    return _to_out(product)


@router.get("/{product_id}")
def get_product(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    product = (
        db.query(Product)
        .options(selectinload(Product.barcodes), selectinload(Product.company))
        .filter(Product.id == product_id)
        .first()
    )
    if not product:
        raise HTTPException(404, "产品不存在")
    return _to_out(product)


@router.put("/{product_id}")
def update_product(
    product_id: int,
    data: ProductUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(404, "产品不存在")
    if data.name is not None:
        product.name = data.name
    if data.description is not None:
        product.description = data.description
    if data.company_id is not None:
        if data.company_id:
            company = db.query(Company).filter(Company.id == data.company_id).first()
            if not company:
                raise HTTPException(404, "公司不存在")
        product.company_id = data.company_id
    if data.remark is not None:
        product.remark = data.remark
    # 更新条码列表：全量替换
    if data.barcodes is not None:
        # 检查新条码是否被其他产品占用
        for bc_item in data.barcodes:
            existing = (
                db.query(ProductBarcode)
                .filter(
                    ProductBarcode.barcode == bc_item.barcode,
                    ProductBarcode.product_id != product_id,
                )
                .first()
            )
            if existing:
                raise HTTPException(400, f"条码 '{bc_item.barcode}' 已被其他产品使用")
        # 删除旧条码
        db.query(ProductBarcode).filter(ProductBarcode.product_id == product_id).delete()
        # 添加新条码
        for bc_item in data.barcodes:
            bc = ProductBarcode(
                product_id=product_id,
                barcode=bc_item.barcode,
                label=bc_item.label,
            )
            db.add(bc)
    db.commit()
    # reload
    product = (
        db.query(Product)
        .options(selectinload(Product.barcodes), selectinload(Product.company))
        .filter(Product.id == product_id)
        .first()
    )
    return _to_out(product)


@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    current_user: User = Depends(require_role("admin", "manager")),
    db: Session = Depends(get_db),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(404, "产品不存在")
    db.delete(product)
    db.commit()
    return {"detail": "已删除"}
