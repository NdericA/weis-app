from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import DriverStatus, PaymentMethod, PaymentStatus, TicketStatus, TicketType, TripStatus, UserRole
from app.db.base import Base


def new_uuid() -> str:
    return str(uuid4())


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    phone_number: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True, unique=True)
    full_name: Mapped[str] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(Enum(UserRole))
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    preferred_language: Mapped[str] = mapped_column(String(5), default="en")


class RiderProfile(TimestampMixin, Base):
    __tablename__ = "rider_profiles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), unique=True)
    emergency_contact: Mapped[str | None] = mapped_column(String(64), nullable=True)
    profile_photo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    home_address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    work_address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    user: Mapped["User"] = relationship()


class FleetOwnerProfile(TimestampMixin, Base):
    __tablename__ = "fleet_owner_profiles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), unique=True)
    company_name: Mapped[str] = mapped_column(String(255))
    user: Mapped["User"] = relationship()


class DriverProfile(TimestampMixin, Base):
    __tablename__ = "driver_profiles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), unique=True)
    fleet_owner_id: Mapped[str | None] = mapped_column(ForeignKey("fleet_owner_profiles.id"), nullable=True)
    license_number: Mapped[str | None] = mapped_column(String(64), nullable=True)
    national_id_number: Mapped[str | None] = mapped_column(String(64), nullable=True)
    rating: Mapped[Decimal] = mapped_column(Numeric(3, 2), default=Decimal("5.00"))
    status: Mapped[DriverStatus] = mapped_column(Enum(DriverStatus), default=DriverStatus.UNDER_REVIEW)
    approval_status: Mapped[str] = mapped_column(String(32), default="pending")
    user: Mapped["User"] = relationship()
    fleet_owner: Mapped["FleetOwnerProfile | None"] = relationship()


class Vehicle(TimestampMixin, Base):
    __tablename__ = "vehicles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    driver_id: Mapped[str | None] = mapped_column(ForeignKey("driver_profiles.id"), nullable=True)
    fleet_owner_id: Mapped[str | None] = mapped_column(ForeignKey("fleet_owner_profiles.id"), nullable=True)
    make: Mapped[str] = mapped_column(String(100))
    model: Mapped[str] = mapped_column(String(100))
    color: Mapped[str] = mapped_column(String(50))
    plate_number: Mapped[str] = mapped_column(String(32), unique=True)
    seat_count: Mapped[int] = mapped_column(default=4)
    is_active: Mapped[bool] = mapped_column(default=True)


class DriverDocument(TimestampMixin, Base):
    __tablename__ = "driver_documents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    driver_id: Mapped[str] = mapped_column(ForeignKey("driver_profiles.id"))
    document_type: Mapped[str] = mapped_column(String(64))
    document_url: Mapped[str] = mapped_column(String(500))
    verification_status: Mapped[str] = mapped_column(String(32), default="pending")


class City(TimestampMixin, Base):
    __tablename__ = "cities"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    country_code: Mapped[str] = mapped_column(String(2), default="CM")
    currency_code: Mapped[str] = mapped_column(String(3), default="XAF")
    is_active: Mapped[bool] = mapped_column(default=True)


class RideType(TimestampMixin, Base):
    __tablename__ = "ride_types"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    city_id: Mapped[str] = mapped_column(ForeignKey("cities.id"))
    name: Mapped[str] = mapped_column(String(64))
    base_fare: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("1000.00"))
    per_km_rate: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("250.00"))
    per_minute_rate: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("50.00"))
    minimum_fare: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("1500.00"))
    cancellation_fee: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("500.00"))
    driver_commission_rate: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("20.00"))


class Trip(TimestampMixin, Base):
    __tablename__ = "trips"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    rider_id: Mapped[str] = mapped_column(ForeignKey("rider_profiles.id"))
    driver_id: Mapped[str | None] = mapped_column(ForeignKey("driver_profiles.id"), nullable=True)
    ride_type_id: Mapped[str | None] = mapped_column(ForeignKey("ride_types.id"), nullable=True)
    city_id: Mapped[str | None] = mapped_column(ForeignKey("cities.id"), nullable=True)
    pickup_address: Mapped[str] = mapped_column(String(255))
    destination_address: Mapped[str] = mapped_column(String(255))
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[TripStatus] = mapped_column(Enum(TripStatus), default=TripStatus.SEARCHING)
    distance_km: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0.00"))
    duration_minutes: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0.00"))
    estimated_fare: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0.00"))
    final_fare: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    payment_method: Mapped[PaymentMethod] = mapped_column(Enum(PaymentMethod), default=PaymentMethod.CASH)


class TripStatusHistory(TimestampMixin, Base):
    __tablename__ = "trip_status_history"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    trip_id: Mapped[str] = mapped_column(ForeignKey("trips.id"))
    status: Mapped[TripStatus] = mapped_column(Enum(TripStatus))
    actor_role: Mapped[str] = mapped_column(String(32))
    note: Mapped[str | None] = mapped_column(Text, nullable=True)


class Wallet(TimestampMixin, Base):
    __tablename__ = "wallets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), unique=True)
    currency_code: Mapped[str] = mapped_column(String(3), default="XAF")
    balance: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"))
    ledger_hold: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"))


class WalletTransaction(TimestampMixin, Base):
    __tablename__ = "wallet_transactions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    wallet_id: Mapped[str] = mapped_column(ForeignKey("wallets.id"))
    transaction_type: Mapped[str] = mapped_column(String(32))
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    reference: Mapped[str] = mapped_column(String(64), unique=True)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)


class Payment(TimestampMixin, Base):
    __tablename__ = "payments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    trip_id: Mapped[str | None] = mapped_column(ForeignKey("trips.id"), nullable=True)
    rider_wallet_id: Mapped[str | None] = mapped_column(ForeignKey("wallets.id"), nullable=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    currency_code: Mapped[str] = mapped_column(String(3), default="XAF")
    method: Mapped[PaymentMethod] = mapped_column(Enum(PaymentMethod))
    status: Mapped[PaymentStatus] = mapped_column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    provider_reference: Mapped[str | None] = mapped_column(String(128), nullable=True)


class Promotion(TimestampMixin, Base):
    __tablename__ = "promotions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    code: Mapped[str] = mapped_column(String(32), unique=True)
    discount_amount: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    discount_percent: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)


class Rating(TimestampMixin, Base):
    __tablename__ = "ratings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    trip_id: Mapped[str] = mapped_column(ForeignKey("trips.id"))
    rider_id: Mapped[str] = mapped_column(ForeignKey("rider_profiles.id"))
    driver_id: Mapped[str] = mapped_column(ForeignKey("driver_profiles.id"))
    score: Mapped[int] = mapped_column(default=5)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)


class SupportTicket(TimestampMixin, Base):
    __tablename__ = "support_tickets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    trip_id: Mapped[str | None] = mapped_column(ForeignKey("trips.id"), nullable=True)
    created_by_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    ticket_type: Mapped[TicketType] = mapped_column(Enum(TicketType))
    status: Mapped[TicketStatus] = mapped_column(Enum(TicketStatus), default=TicketStatus.OPEN)
    subject: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)


class Notification(TimestampMixin, Base):
    __tablename__ = "notifications"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    channel: Mapped[str] = mapped_column(String(32))
    title: Mapped[str] = mapped_column(String(255))
    body: Mapped[str] = mapped_column(Text)
    delivery_status: Mapped[str] = mapped_column(String(32), default="queued")


class AdminLog(TimestampMixin, Base):
    __tablename__ = "admin_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    admin_user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    action: Mapped[str] = mapped_column(String(128))
    entity_type: Mapped[str] = mapped_column(String(64))
    entity_id: Mapped[str] = mapped_column(String(64))
    details: Mapped[str | None] = mapped_column(Text, nullable=True)
