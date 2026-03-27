from decimal import Decimal

from pydantic import BaseModel


class KPIReport(BaseModel):
    booking_success_rate: float
    average_assignment_time_seconds: int
    average_wait_time_minutes: int
    trip_completion_rate: float
    driver_acceptance_rate: float
    cancellation_rate: float
    payment_success_rate: float
    monthly_active_riders: int
    monthly_active_drivers: int
    revenue_current_month: Decimal
