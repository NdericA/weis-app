from fastapi import APIRouter

from app.schemas.admin import AdminDashboardSummary, PricingConfigResponse
from app.services.admin_service import AdminService

router = APIRouter()
service = AdminService()


@router.get("/dashboard", response_model=AdminDashboardSummary)
def get_dashboard() -> AdminDashboardSummary:
    return service.get_dashboard_summary()


@router.get("/pricing", response_model=list[PricingConfigResponse])
def list_pricing_configs() -> list[PricingConfigResponse]:
    return service.list_pricing()
