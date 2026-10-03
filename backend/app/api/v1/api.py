from fastapi import APIRouter
from app.api.v1.endpoints import health, auth, devices, diagnostics, decisions, technicians, repairs, quotes, parts, notifications, payments, ml


api_router = APIRouter()
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(devices.router, prefix="/devices", tags=["Devices"])
api_router.include_router(diagnostics.router, prefix="/diagnostics", tags=["Diagnostics"])
api_router.include_router(decisions.router, prefix="/decisions", tags=["Decisions"])
api_router.include_router(technicians.router, prefix="/technicians", tags=["Technicians"])
api_router.include_router(repairs.router, prefix="/repairs", tags=["Repairs"])
api_router.include_router(quotes.router, tags=["Quotes"])
api_router.include_router(parts.router, prefix="/parts", tags=["Spare Parts"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])
api_router.include_router(payments.router, prefix="/payments", tags=["Payments"])
api_router.include_router(ml.router, prefix="/ml", tags=["AI & Machine Learning"])


