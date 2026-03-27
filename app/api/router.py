from fastapi import APIRouter

from app.api.routes import admin, auth, drivers, live, payments, reports, riders, support, trips, wallets

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(riders.router, prefix="/riders", tags=["riders"])
api_router.include_router(drivers.router, prefix="/drivers", tags=["drivers"])
api_router.include_router(trips.router, prefix="/trips", tags=["trips"])
api_router.include_router(payments.router, prefix="/payments", tags=["payments"])
api_router.include_router(wallets.router, prefix="/wallets", tags=["wallets"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(support.router, prefix="/support", tags=["support"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(live.router, prefix="/live", tags=["live"])
