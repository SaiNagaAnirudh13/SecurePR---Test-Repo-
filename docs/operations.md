# Operations

## Local container run

Copy `.env.example` to `.env`, set a unique development `SECRET_KEY`, then run:

```sh
docker compose up --build
```

The UI is at `http://localhost:5173`, the API at `http://localhost:8000`, and OpenAPI at `/docs`. After startup, create an administrator with `docker compose exec api python /app/infrastructure/scripts/bootstrap_admin.py --email admin@example.com --name "Platform Admin" --password "Choose-A-Long-Password!"`. Load demo catalog data with `docker compose exec api python /app/infrastructure/scripts/seed_demo.py`. The initial Compose database password is for local use only.

## Deployment and configuration

Set `APP_ENV=production`, `DATABASE_URL`, a random `SECRET_KEY` (32+ characters), and explicit `CORS_ORIGINS`. The API refuses the development secret in production. Build images in CI, pin reviewed base image versions, apply Alembic migrations as a release step, and use managed PostgreSQL with encrypted connections and automated backups.

Run multiple stateless API instances behind TLS termination. Run the notification worker separately and monitor its pending/failed notification counts. Add a dead-letter/retry policy and delivery provider before using the outbox for external delivery.

## Monitoring and recovery

`GET /health` is a liveness endpoint. Production readiness probes should additionally verify a database connection. Export structured application logs to a centralized system; monitor request latency/error rates, connection pool saturation, order conflicts, worker lag, database storage, and low-stock inventory.

Back up PostgreSQL and test restoration regularly. Review audit records with restricted administrative access. Define retention and privacy policies for customer and audit data before production. Graceful shutdown is supported by the worker; deployments should allow time for in-flight database work to finish.

## Known simplifications

This starter platform uses an illustrative fixed tax rate, a single default warehouse per order reservation, log-only notification delivery, provider-neutral pending payments, and a minimal reporting model. It is an engineering test target, not a production-certified ERP, tax engine, payment processor, or messaging service.
