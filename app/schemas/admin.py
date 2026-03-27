from decimal import Decimal

from pydantic import BaseModel


class AdminDashboardSummary(BaseModel):
    active_trips: int
    online_drivers: int
    active_riders: int
    daily_revenue: Decimal
    cancellation_rate: float
    completion_rate: float


class PricingConfigResponse(BaseModel):
    city: str
    ride_type: str
    base_fare: Decimal
    per_km_rate: Decimal
    per_minute_rate: Decimal
    minimum_fare: Decimal
    cancellation_fee: Decimal
