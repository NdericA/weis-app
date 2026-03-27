from decimal import Decimal

from app.schemas.report import KPIReport


class ReportingService:
    def get_kpis(self) -> KPIReport:
        return KPIReport(
            booking_success_rate=96.3,
            average_assignment_time_seconds=34,
            average_wait_time_minutes=6,
            trip_completion_rate=92.1,
            driver_acceptance_rate=88.5,
            cancellation_rate=4.8,
            payment_success_rate=93.7,
            monthly_active_riders=25340,
            monthly_active_drivers=4120,
            revenue_current_month=Decimal("68500000.00"),
        )
