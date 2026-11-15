from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

from app.api.deps import AdminOperationsUser, CurrentUser, DbSession
from app.models import InventoryItem, Product
from app.schemas.catalog import InventoryAdjustment, InventoryRead
from app.services.audit import record_audit

router = APIRouter()


@router.get("", response_model=list[InventoryRead])
def list_inventory(
    db: DbSession, user: CurrentUser, low_stock_only: bool = False
) -> list[InventoryRead]:
    query = (
        select(InventoryItem)
        .options(joinedload(InventoryItem.product))
        .order_by(InventoryItem.warehouse_code)
    )
    rows = db.scalars(query).unique().all()
    return [
        InventoryRead(
            id=row.id,
            product_id=row.product_id,
            sku=row.product.sku,
            product_name=row.product.name,
            warehouse_code=row.warehouse_code,
            quantity_on_hand=row.quantity_on_hand,
            quantity_reserved=row.quantity_reserved,
            available_quantity=row.available_quantity,
            reorder_point=row.reorder_point,
        )
        for row in rows
        if not low_stock_only or row.available_quantity <= row.reorder_point
    ]


@router.post("/adjustments", response_model=InventoryRead, status_code=status.HTTP_200_OK)
def adjust_inventory(
    payload: InventoryAdjustment,
    db: DbSession,
    user: AdminOperationsUser,
) -> InventoryRead:
    product = db.get(Product, payload.product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product was not found")
    row = db.scalar(
        select(InventoryItem)
        .where(
            InventoryItem.product_id == payload.product_id,
            InventoryItem.warehouse_code == payload.warehouse_code,
        )
        .with_for_update()
    )
    if row is None:
        row = InventoryItem(
            product_id=payload.product_id,
            warehouse_code=payload.warehouse_code,
            quantity_on_hand=0,
            quantity_reserved=0,
        )
        db.add(row)
        db.flush()
    if row.quantity_on_hand + payload.quantity_delta < row.quantity_reserved:
        raise HTTPException(
            status_code=409, detail="Adjustment would reduce stock below reserved quantity"
        )
    row.quantity_on_hand += payload.quantity_delta
    row.reorder_point = payload.reorder_point
    record_audit(
        db,
        actor_id=user.id,
        action="inventory.adjusted",
        resource_type="inventory",
        resource_id=str(row.id),
        details={"delta": payload.quantity_delta, "warehouse": payload.warehouse_code},
    )
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(
            status_code=409, detail="Inventory adjustment conflicted with another update"
        ) from error
    db.refresh(row)
    return InventoryRead(
        id=row.id,
        product_id=row.product_id,
        sku=product.sku,
        product_name=product.name,
        warehouse_code=row.warehouse_code,
        quantity_on_hand=row.quantity_on_hand,
        quantity_reserved=row.quantity_reserved,
        available_quantity=row.available_quantity,
        reorder_point=row.reorder_point,
    )
