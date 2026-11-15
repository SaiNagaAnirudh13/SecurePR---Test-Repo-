from fastapi import APIRouter

from app.api.routes import admin, auth, catalog, inventory, orders, reports

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(catalog.customers_router, prefix="/customers", tags=["customers"])
api_router.include_router(catalog.products_router, prefix="/products", tags=["products"])
api_router.include_router(inventory.router, prefix="/inventory", tags=["inventory"])
api_router.include_router(orders.router, prefix="/orders", tags=["orders"])
api_router.include_router(reports.router, prefix="/reports", tags=["reporting"])
api_router.include_router(admin.router, prefix="/admin", tags=["administration"])
