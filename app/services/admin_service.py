from decimal import Decimal

from app.schemas.admin import AdminDashboardSummary, PricingConfigResponse
from app.services.pricing_service import PricingService


class AdminService:
    def __init__(self) -> None:
        self.pricing_service = PricingService()

    def get_dashboard_summary(self) -> AdminDashboardSummary:
        return AdminDashboardSummary(
            active_trips=128,
            online_drivers=342,
            active_riders=1789,
            daily_revenue=Decimal("2450000.00"),
            cancellation_rate=4.2,
            completion_rate=91.8,
        )

    def list_pricing(self) -> list[PricingConfigResponse]:
        return [
            PricingConfigResponse(
                city="Douala",
                ride_type=name,
                base_fare=config.base_fare,
                per_km_rate=config.per_km_rate,
                per_minute_rate=config.per_minute_rate,
                minimum_fare=config.minimum_fare,
                cancellation_fee=config.cancellation_fee,
            )
            for name, config in self.pricing_service.PRICING.items()
        ]
