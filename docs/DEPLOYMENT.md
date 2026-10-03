# ReVivo Platform Deployment & Operations Guide

> **Important Deployment Notice**:
> Production readiness must not be claimed until the deployment has been staged and verified with automated integration tests, connectivity healthchecks, and live smoke tests in a dedicated staging environment.

This guide provides step-by-step procedures for deploying and operating the ReVivo ecosystem across the Backend API, PostgreSQL database, Redis caching layer, Next.js Admin Dashboard, and React Native (Expo) Mobile Application.

---

## 1. Environment Variables Reference

All runtime secrets must be passed via environment variables or a secure key management service (e.g. AWS Secrets Manager, HashiCorp Vault, Doppler). **Never hardcode secrets in code or Dockerfiles.**

### Backend & Core Services (`.env.production`)

| Variable Name | Required | Default / Example | Purpose / Description |
| :--- | :---: | :--- | :--- |
| `ENVIRONMENT` | **Yes** | `production` | Enables strict production security checks and error masks. |
| `PROJECT_NAME` | No | `ReVivo Platform` | Human-readable service identifier. |
| `API_V1_STR` | No | `/api/v1` | URL prefix for REST API endpoints. |
| `DATABASE_URL` | **Yes** | `postgresql+psycopg://user:pass@host:5432/dbname` | Connection string for PostgreSQL database. |
| `REDIS_URL` | **Yes** | `redis://:pass@host:6379/0` | Connection string for Redis cache & rate-limiter. |
| `JWT_SECRET` | **Yes** | *(32+ random hex chars)* | Cryptographic key used to sign and verify JWT tokens. |
| `ALGORITHM` | No | `HS256` | JWT signing algorithm. |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | `30` | Access token lifespan in minutes. |
| `REFRESH_TOKEN_EXPIRE_MINUTES`| No | `10080` (7 days) | Refresh token lifespan. |
| `PAYMENT_PROVIDER` | **Yes** | `stripe` / `sandbox` | Active payment gateway adapter. |
| `PAYMENT_SANDBOX_MODE` | **Yes** | `false` (in prod) | Disables sandbox test tokens and activates live processor. |
| `PLATFORM_FEE_PERCENTAGE` | No | `15.0` | Commission rate percentage deducted from technician payouts. |
| `STRIPE_SECRET_KEY` | Conditional| `sk_live_...` | Live Stripe API secret key. |
| `STRIPE_WEBHOOK_SECRET` | Conditional| `whsec_...` | Webhook verification signing secret. |
| `BACKEND_CORS_ORIGINS` | **Yes** | `["https://admin.revivo.internal"]` | Whitelisted frontend origins. |
| `RUN_MIGRATIONS` | No | `true` | Runs `alembic upgrade head` on container entrypoint. |
| `LOG_LEVEL` | No | `INFO` | Logging granularity (`DEBUG`, `INFO`, `WARNING`, `ERROR`). |
| `SENTRY_DSN` | No | `https://...@sentry.io/...` | Application exception & crash reporting. |

### Next.js Admin Dashboard (`admin/.env.production`)

| Variable Name | Required | Default / Example | Purpose |
| :--- | :---: | :--- | :--- |
| `NEXT_PUBLIC_API_URL` | **Yes** | `https://api.revivo.internal` | Root URL of backend FastAPI service. |
| `NODE_ENV` | **Yes** | `production` | Optimizes Next.js bundle for runtime execution. |

### Mobile Application (`mobile/.env`)

| Variable Name | Required | Default / Example | Purpose |
| :--- | :---: | :--- | :--- |
| `EXPO_PUBLIC_API_URL` | **Yes** | `https://api.revivo.internal` | Target API gateway endpoint for mobile app. |

---

## 2. Database Setup

ReVivo uses **PostgreSQL 15+** with relational constraints and JSON data types.

### A. Managed PostgreSQL (e.g., AWS RDS, Supabase, Neon)
1. Provision a PostgreSQL 15 or 16 instance.
2. Create the production user and database:
   ```sql
   CREATE USER revivo_prod_admin WITH ENCRYPTED PASSWORD 'your_strong_password';
   CREATE DATABASE revivo_production OWNER revivo_prod_admin;
   GRANT ALL PRIVILEGES ON DATABASE revivo_production TO revivo_prod_admin;
   ```
3. Ensure SSL mode is enabled (`sslmode=require`).

### B. Self-Hosted / Docker PostgreSQL
Using the provided `docker-compose.prod.yml`:
```bash
# Verify directory permissions for volume mounts
mkdir -p /opt/revivo/data/postgres
chmod 700 /opt/revivo/data/postgres

# Launch DB and Redis
docker compose -f docker-compose.prod.yml up -d db redis
```

---

## 3. Migration Commands

Database migrations are managed using **Alembic**.

### Apply Migrations to Latest Schema (Upgrade)
```bash
# Running on host or inside container
cd backend
alembic upgrade head
```

### Rollback the Most Recent Migration (Downgrade)
```bash
alembic downgrade -1
```

### Revert to Specific Migration Revision
```bash
alembic downgrade <revision_id>
```

### Inspect Migration History & Current Version
```bash
# View current database version
alembic current

# View all applied and pending migration history
alembic history --verbose
```

### Creating New Schema Migrations
```bash
alembic revision --autogenerate -m "describe_schema_change"
```

---

## 4. Backend Deployment

### A. Local Development (Docker Compose)
To start all services locally with hot-reloading:
```bash
# Start Postgres, Redis, and FastAPI backend
docker compose up --build
```
Access backend API documentation at: `http://localhost:8000/docs`

### B. Production Container Deployment (Docker Compose)
1. Create and configure `.env.production` on the target host:
   ```bash
   cp .env.production.example .env.production
   nano .env.production
   chmod 600 .env.production
   ```
2. Build and launch production containers with Gunicorn + Uvicorn workers:
   ```bash
   docker compose -f docker-compose.prod.yml up -d --build
   ```
3. Check container status:
   ```bash
   docker compose -f docker-compose.prod.yml ps
   ```

### C. Systemd / Native Linux Deployment
If running without Docker:
1. Setup Python virtual environment:
   ```bash
   cd /opt/revivo/backend
   python3 -m venv venv
   source venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
2. Run migrations:
   ```bash
   alembic upgrade head
   ```
3. Configure systemd service (`/etc/systemd/system/revivo-backend.service`):
   ```ini
   [Unit]
   Description=ReVivo FastAPI Backend
   After=network.target postgresql.service redis.service

   [Service]
   User=revivouser
   Group=revivogroup
   WorkingDirectory=/opt/revivo/backend
   EnvironmentFile=/opt/revivo/backend/.env.production
   ExecStart=/opt/revivo/backend/venv/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000 --timeout 120
   Restart=always
   RestartSec=5

   [Install]
   WantedBy=multi-user.target
   ```
4. Enable and start service:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable --now revivo-backend
   ```

---

## 5. Admin Deployment (Next.js Dashboard)

The Next.js Admin Dashboard (`admin/`) provides user management, dispute moderation, and repair monitoring.

### A. Production Build & Start (Node.js)
```bash
cd admin

# 1. Install dependencies
npm ci

# 2. Typecheck and build standalone production bundle
npm run build

# 3. Start production server on port 3000
npm start -- -p 3000
```

### B. Deploying to Vercel / Cloudflare Pages
1. Link GitHub repository to Vercel.
2. Set Root Directory to `admin`.
3. Configure Environment Variables:
   * `NEXT_PUBLIC_API_URL`: `https://api.revivo.internal`
4. Trigger production deploy.

---

## 6. Mobile Build Process (React Native / Expo)

The customer & technician mobile client is built using **Expo**.

### A. Local Development Testing
```bash
cd mobile
npm install
npx expo start
```

### B. Production Mobile Application Builds (EAS - Expo Application Services)
1. Install EAS CLI:
   ```bash
   npm install -g eas-cli
   eas login
   ```
2. Configure `eas.json` build profiles:
   ```json
   {
     "cli": { "version": ">= 12.0.0" },
     "build": {
       "development": {
         "developmentClient": true,
         "distribution": "internal"
       },
       "preview": {
         "distribution": "internal"
       },
       "production": {
         "env": {
           "EXPO_PUBLIC_API_URL": "https://api.revivo.internal"
         }
       }
     }
   }
   ```
3. Trigger Android App Bundle (AAB / APK) build:
   ```bash
   eas build --platform android --profile production
   ```
4. Trigger iOS IPA build (requires Apple Developer Program):
   ```bash
   eas build --platform ios --profile production
   ```
5. Submit to app stores:
   ```bash
   eas submit --platform android
   eas submit --platform ios
   ```

---

## 7. Logging & Monitoring

### A. Centralized Application Logging
* FastAPI uses structured Python standard logging configured for JSON output in production.
* View live container logs:
  ```bash
  docker compose -f docker-compose.prod.yml logs -f --tail=100 backend
  ```
* Standard log formats include timestamp, level, module, request ID, and client IP.

### B. Healthcheck Endpoint
* Health check URL: `GET /api/v1/health`
* Returns:
  ```json
  {
    "status": "healthy",
    "timestamp": "2026-10-04T00:00:00.000000Z",
    "services": {
      "database": "connected",
      "redis": "connected",
      "version": "1.0.0"
    }
  }
  ```

### C. Error Tracking
* Configure `SENTRY_DSN` in `.env.production` for automatic unhandled exception tracing, performance monitoring, and release health analytics.

---

## 8. Backup Procedures

### A. Automated PostgreSQL Daily Backup Script
Save as `/opt/revivo/scripts/backup_db.sh`:
```bash
#!/bin/bash
set -eo pipefail

BACKUP_DIR="/opt/revivo/backups/postgres"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/revivo_backup_${TIMESTAMP}.sql.gz"

mkdir -p "${BACKUP_DIR}"

# Execute compressed pg_dump
docker exec revivo_prod_db pg_dump -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" | gzip > "${BACKUP_FILE}"

# Retention policy: Remove backups older than 14 days
find "${BACKUP_DIR}" -type f -name "revivo_backup_*.sql.gz" -mtime +14 -delete

echo "Backup created successfully: ${BACKUP_FILE}"
```
Schedule via Cron (`crontab -e`):
```cron
0 2 * * * /opt/revivo/scripts/backup_db.sh >> /var/log/revivo_backup.log 2>&1
```

### B. Redis Persistence Backup
Redis is configured with Append-Only File (`AOF`) and RDB snapshots saved in volume `prod_redis_data`.
To trigger an immediate snapshot:
```bash
docker exec revivo_prod_redis redis-cli -a "${REDIS_PASSWORD}" BGSAVE
```

---

## 9. Rollback Procedures

If a critical defect or failure occurs post-deployment:

### A. Backend Code Rollback
1. Re-tag or pull the previous known stable Docker image tag:
   ```bash
   docker pull ghcr.io/revivo/backend:v1.0.4
   docker tag ghcr.io/revivo/backend:v1.0.4 ghcr.io/revivo/backend:latest
   docker compose -f docker-compose.prod.yml up -d backend
   ```
2. Verify service health:
   ```bash
   curl -f http://localhost:8000/api/v1/health
   ```

### B. Database Migration Rollback
If the failed release introduced a database schema change:
1. Check current migration revision:
   ```bash
   alembic current
   ```
2. Step back 1 migration:
   ```bash
   alembic downgrade -1
   ```

### C. Database Disaster Recovery (Restore from Backup)
To restore the database from a compressed snapshot:
```bash
gunzip -c /opt/revivo/backups/postgres/revivo_backup_20261004_020000.sql.gz | docker exec -i revivo_prod_db psql -U "${POSTGRES_USER}" -d "${POSTGRES_DB}"
```

---

## 10. Pre-Production Verification Checklist

Before officially declaring production readiness:

- [ ] All 85 automated test suites pass cleanly (`pytest tests/`).
- [ ] Database migrations execute cleanly on a fresh PostgreSQL instance.
- [ ] `.env.production` configured with strong secrets (>=32 characters for JWT secret).
- [ ] Non-root execution verified inside Docker container (`revivouser` UID 10001).
- [ ] Rate limiting and security headers verified against live endpoints.
- [ ] HTTPS/TLS terminates properly at the reverse proxy (Nginx / Cloudflare / ALB).
- [ ] Database backup and restore cycle verified in staging.
