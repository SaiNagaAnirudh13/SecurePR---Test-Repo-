from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.api.deps import AdminOperationsUser, CurrentUser, DbSession
from app.models import Customer, Product
from app.schemas.catalog import CustomerCreate, CustomerRead, ProductCreate, ProductRead
from app.services.audit import record_audit

customers_router = APIRouter()
products_router = APIRouter()


@customers_router.get("", response_model=list[CustomerRead])
def list_customers(
    db: DbSession, user: CurrentUser, offset: int = 0, limit: int = 50
) -> list[Customer]:
    return list(
        db.scalars(
            select(Customer).order_by(Customer.company_name).offset(offset).limit(min(limit, 100))
        ).all()
    )


@customers_router.post("", response_model=CustomerRead, status_code=status.HTTP_201_CREATED)
def create_customer(
    payload: CustomerCreate,
    db: DbSession,
    user: AdminOperationsUser,
) -> Customer:
    customer = Customer(**payload.model_dump())
    db.add(customer)
    db.flush()
    record_audit(
        db,
        actor_id=user.id,
        action="customer.created",
        resource_type="customer",
        resource_id=str(customer.id),
    )
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(
            status_code=409, detail="Customer account number or email already exists"
        ) from error
    db.refresh(customer)
    return customer


@products_router.get("", response_model=list[ProductRead])
def list_products(
    db: DbSession,
    user: CurrentUser,
    category: str | None = None,
    offset: int = 0,
    limit: int = 50,
) -> list[Product]:
    query = select(Product).order_by(Product.name)
    if category:
        query = query.where(Product.category == category)
    return list(db.scalars(query.offset(offset).limit(min(limit, 100))).all())


@products_router.post("", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
def create_product(
    payload: ProductCreate,
    db: DbSession,
    user: AdminOperationsUser,
) -> Product:
    product = Product(**payload.model_dump())
    db.add(product)
    db.flush()
    record_audit(
        db,
        actor_id=user.id,
        action="product.created",
        resource_type="product",
        resource_id=str(product.id),
    )
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(status_code=409, detail="Product SKU already exists") from error
    db.refresh(product)
    return product
