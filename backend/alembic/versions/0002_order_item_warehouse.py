"""Persist the warehouse selected for each order-line allocation.

Revision ID: 0002_order_item_warehouse
Revises: 0001_initial
"""

import sqlalchemy as sa
from sqlalchemy import inspect, text

from alembic import op

revision = "0002_order_item_warehouse"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    columns = {column["name"] for column in inspect(bind).get_columns("order_items")}
    if "warehouse_code" not in columns:
        op.add_column("order_items", sa.Column("warehouse_code", sa.String(length=30)))
    bind.execute(
        text(
            "UPDATE order_items "
            "SET warehouse_code = ("
            "SELECT inventory_items.warehouse_code "
            "FROM inventory_items "
            "WHERE inventory_items.product_id = order_items.product_id "
            "ORDER BY inventory_items.warehouse_code "
            "LIMIT 1"
            ") "
            "WHERE warehouse_code IS NULL"
        )
    )


def downgrade() -> None:
    columns = {column["name"] for column in inspect(op.get_bind()).get_columns("order_items")}
    if "warehouse_code" in columns:
        op.drop_column("order_items", "warehouse_code")
