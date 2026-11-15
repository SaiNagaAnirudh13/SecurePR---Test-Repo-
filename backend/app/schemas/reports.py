from decimal import Decimal

from pydantic import BaseModel


class SalesSummary(BaseModel):
    order_count: int
    gross_sales: Decimal
    average_order_value: Decimal
    status_counts: dict[str, int]
    low_stock_items: int
