"""Load deterministic demo catalog data for local development."""

from decimal import Decimal
import sys
from pathlib import Path

backend_path = Path(__file__).resolve().parents[2] / "backend"
if backend_path.exists():
    sys.path.insert(0, str(backend_path))

from sqlalchemy import select

from app.core.db import SessionLocal
from app.models import Customer, InventoryItem, Product, Role


def main() -> None:
    with SessionLocal() as db:
        for name, description in [
            ("operations", "Order and inventory operations"),
            ("analyst", "Read-only reporting access"),
        ]:
            if db.scalar(select(Role).where(Role.name == name)) is None:
                db.add(Role(name=name, description=description))

        if db.scalar(select(Customer).where(Customer.account_number == "ACCT-1000")) is None:
            db.add(
                Customer(
                    account_number="ACCT-1000",
                    company_name="Northwind Distribution",
                    contact_name="Morgan Lee",
                    email="procurement@example.com",
                    phone="+1-555-0100",
                    billing_address="100 Market Street, Boston, MA 02110",
                    shipping_address="200 Harbor Road, Boston, MA 02110",
                )
            )
        if db.scalar(select(Product).where(Product.sku == "NW-DOCK-01")) is None:
            product = Product(
                sku="NW-DOCK-01",
                name="USB-C Docking Station",
                description="Enterprise dual-display dock with 100W power delivery.",
                category="Peripherals",
                unit_price=Decimal("125.00"),
            )
            db.add(product)
            db.flush()
            db.add(
                InventoryItem(
                    product_id=product.id,
                    warehouse_code="BOS-01",
                    quantity_on_hand=48,
                    quantity_reserved=0,
                    reorder_point=10,
                )
            )
        db.commit()
    print("Demo catalog data is ready.")


if __name__ == "__main__":
    main()
