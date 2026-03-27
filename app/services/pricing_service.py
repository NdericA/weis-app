from dataclasses import dataclass
from decimal import Decimal

from app.schemas.trip import FareEstimateRequest, FareEstimateResponse


@dataclass(frozen=True)
class RideTypePricing:
    base_fare: Decimal
    per_km_rate: Decimal
    per_minute_rate: Decimal
    minimum_fare: Decimal
    cancellation_fee: Decimal


class PricingService:
    PRICING: dict[str, RideTypePricing] = {
        "economy": RideTypePricing(
            base_fare=Decimal("1000.00"),
            per_km_rate=Decimal("225.00"),
            per_minute_rate=Decimal("45.00"),
            minimum_fare=Decimal("1500.00"),
            cancellation_fee=Decimal("500.00"),
        ),
        "standard": RideTypePricing(
            base_fare=Decimal("1500.00"),
            per_km_rate=Decimal("300.00"),
            per_minute_rate=Decimal("55.00"),
            minimum_fare=Decimal("2200.00"),
            cancellation_fee=Decimal("750.00"),
        ),
        "premium": RideTypePricing(
            base_fare=Decimal("2500.00"),
            per_km_rate=Decimal("450.00"),
            per_minute_rate=Decimal("80.00"),
            minimum_fare=Decimal("4000.00"),
            cancellation_fee=Decimal("1000.00"),
        ),
        "xl": RideTypePricing(
            base_fare=Decimal("2200.00"),
            per_km_rate=Decimal("400.00"),
            per_minute_rate=Decimal("75.00"),
            minimum_fare=Decimal("3500.00"),
            cancellation_fee=Decimal("1000.00"),
        ),
        "moto": RideTypePricing(
            base_fare=Decimal("700.00"),
            per_km_rate=Decimal("150.00"),
            per_minute_rate=Decimal("30.00"),
            minimum_fare=Decimal("1000.00"),
            cancellation_fee=Decimal("400.00"),
        ),
        "intercity": RideTypePricing(
            base_fare=Decimal("5000.00"),
            per_km_rate=Decimal("600.00"),
            per_minute_rate=Decimal("90.00"),
            minimum_fare=Decimal("10000.00"),
            cancellation_fee=Decimal("2500.00"),
        ),
    }

    def estimate_fare(self, payload: FareEstimateRequest) -> FareEstimateResponse:
        pricing = self.PRICING.get(payload.ride_type, self.PRICING["economy"])
        distance_fare = payload.distance_km * pricing.per_km_rate
        time_fare = payload.duration_minutes * pricing.per_minute_rate
        subtotal = pricing.base_fare + distance_fare + time_fare
        surged_total = subtotal * payload.surge_multiplier
        estimated_fare = max(surged_total, pricing.minimum_fare)
        return FareEstimateResponse(
            ride_type=payload.ride_type,
            estimated_fare=estimated_fare.quantize(Decimal("0.01")),
            base_fare=pricing.base_fare,
            distance_fare=distance_fare.quantize(Decimal("0.01")),
            time_fare=time_fare.quantize(Decimal("0.01")),
            surge_multiplier=payload.surge_multiplier,
        )
