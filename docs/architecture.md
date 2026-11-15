# Architecture

EOMP is a modular monolith with a versioned FastAPI boundary and a separately deployed React operations console. The service layer owns business rules, repositories encapsulate common persistence queries, and SQLAlchemy models map to PostgreSQL. The same backend image can run the API or the notification worker.

## Business domains

- **Identity:** users are assigned one role (`admin`, `operations`, or `analyst`). JWTs identify the user; authorization is evaluated against the current database role on each request.
- **Customer and catalog:** business accounts own orders; product SKUs and prices are snapshotted onto order lines to preserve historical order values.
- **Inventory:** stock is tracked per product and warehouse. Orders reserve available quantity; cancellation releases reservations; shipment dispatch consumes on-hand stock and clears reservations.
- **Order lifecycle:** orders move through confirmed → processing → shipped → delivered, with cancellation permitted before shipment. Invalid transitions are rejected.
- **Payments and fulfillment:** payment intents are provider-neutral records only; shipment records are created at dispatch. No payment credentials or card data are collected.
- **Audit and notifications:** business mutations produce audit records. Order confirmation writes a transactional notification to an outbox table; a worker processes pending messages.
- **Reporting:** summary metrics aggregate orders and low-stock inventory at query time.

## Request and persistence flow

`API route → request schema validation → service/repository → SQLAlchemy unit of work → PostgreSQL`

Order creation validates the customer, product and available inventory, writes order lines, reserves inventory, records an audit event and queues a notification in one database transaction. Conditional inventory updates protect against concurrent overselling. PostgreSQL row locks are used where supported.

The UI reads live API data and keeps the access token in browser storage for this representative internal console. Production deployments should prefer a same-site secure cookie and a CSRF strategy. There is no client-side mock-data fallback.

## Runtime topology

Docker Compose starts PostgreSQL, the API, a notification worker and a static frontend container. Alembic migrations run before API startup. The API and worker share configuration and the relational store. The worker currently dispatches to structured logs; external email/SMS delivery is an integration point.
