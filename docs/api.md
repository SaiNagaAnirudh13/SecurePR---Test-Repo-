# API Design

All business endpoints are under `/api/v1`. Interactive OpenAPI documentation is available at `/docs` when the service is running.

## Authentication

`POST /api/v1/auth/token` accepts `{ "email": "...", "password": "..." }` and returns a short-lived bearer token. `GET /api/v1/auth/me` returns the authenticated profile. There is no public self-registration endpoint.

## Resources

| Method | Path | Purpose | Authorization |
|---|---|---|---|
| GET, POST | `/customers` | List or create customer accounts | Authenticated / operations or admin |
| GET, POST | `/products` | List or create catalog products | Authenticated / operations or admin |
| GET | `/inventory` | Read warehouse balances; optionally `low_stock_only=true` | Authenticated |
| POST | `/inventory/adjustments` | Apply an audited stock adjustment | Operations or admin |
| GET, POST | `/orders` | List or place customer orders | Authenticated |
| GET | `/orders/{id}` | Read order, lines and shipment | Authenticated |
| PATCH | `/orders/{id}/status` | Advance or cancel order lifecycle | Operations or admin |
| POST | `/orders/{id}/payments` | Create provider-neutral payment intent | Operations or admin |
| GET | `/reports/sales-summary` | Sales and stock summary | Authenticated |
| GET | `/admin/audit-logs` | Paginated audit history | Admin |

List endpoints use bounded pagination (`offset`, `limit`). Validation errors follow FastAPI's structured 422 response. Domain conflicts return 409, missing resources 404, and failed authentication 401. API errors never include stack traces.

## Order creation

`POST /orders` accepts a customer ID, one or more product/quantity lines, and optional notes. The backend snapshots unit prices, computes an 8.25% illustrative tax, reserves stock and returns an order number. The tax rate is an intentionally simplified example and must be replaced with a jurisdiction-aware tax integration before real use.

## Compatibility

JSON request/response fields use `snake_case`; amounts are decimal strings in responses. UUIDs are used for business identifiers except role IDs. API changes should be additive where possible and documented before removing or renaming fields.
