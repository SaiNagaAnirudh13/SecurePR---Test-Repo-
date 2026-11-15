from decimal import Decimal

from fastapi import APIRouter
from sqlalchemy import func, select

from app.api.deps import DbSession, ReportingUser
from app.models import InventoryItem, Order
from app.schemas.reports import SalesSummary

router = APIRouter()


@router.get("/sales-summary", response_model=SalesSummary)
def sales_summary(
    db: DbSession,
    user: ReportingUser,
) -> SalesSummary:
    rows = db.execute(
        select(
            Order.status, func.count(Order.id), func.coalesce(func.sum(Order.total_amount), 0)
        ).group_by(Order.status)
    ).all()
    active_rows = [row for row in rows if row[0] != "cancelled"]
    order_count = sum(row[1] for row in active_rows)
    gross_sales = sum((Decimal(str(row[2])) for row in active_rows), start=Decimal("0"))
    low_stock = db.scalar(
        select(func.count(InventoryItem.id)).where(
            InventoryItem.quantity_on_hand - InventoryItem.quantity_reserved
            <= InventoryItem.reorder_point
        )
    )
    return SalesSummary(
        order_count=order_count,
        gross_sales=gross_sales,
        average_order_value=(gross_sales / order_count if order_count else Decimal("0")),
        status_counts={row[0]: row[1] for row in rows},
        low_stock_items=low_stock or 0,
    )
