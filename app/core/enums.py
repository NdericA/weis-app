from enum import StrEnum


class UserRole(StrEnum):
    RIDER = "rider"
    DRIVER = "driver"
    FLEET_OWNER = "fleet_owner"
    ADMIN = "admin"
    SUPPORT = "support"


class DriverStatus(StrEnum):
    OFFLINE = "offline"
    ONLINE = "online"
    PAUSED = "paused"
    UNDER_REVIEW = "under_review"


class TripStatus(StrEnum):
    SEARCHING = "searching"
    DRIVER_ASSIGNED = "driver_assigned"
    DRIVER_ARRIVING = "driver_arriving"
    DRIVER_ARRIVED = "driver_arrived"
    TRIP_STARTED = "trip_started"
    TRIP_COMPLETED = "trip_completed"
    TRIP_CANCELLED = "trip_cancelled"


class PaymentMethod(StrEnum):
    CASH = "cash"
    WALLET = "wallet"
    CARD = "card"
    MOBILE_MONEY = "mobile_money"


class PaymentStatus(StrEnum):
    PENDING = "pending"
    AUTHORIZED = "authorized"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class TicketType(StrEnum):
    COMPLAINT = "complaint"
    LOST_ITEM = "lost_item"
    SAFETY = "safety"
    INCIDENT = "incident"


class TicketStatus(StrEnum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"
