from fastapi import APIRouter

from app.schemas.report import KPIReport
from app.services.reporting_service import ReportingService

router = APIRouter()
service = ReportingService()


@router.get("/kpis", response_model=KPIReport)
def get_kpis() -> KPIReport:
    return service.get_kpis()
