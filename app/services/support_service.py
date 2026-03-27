from uuid import uuid4

from app.core.enums import TicketStatus
from app.schemas.support import SupportTicketCreate, SupportTicketResponse


class SupportService:
    def create_ticket(self, payload: SupportTicketCreate) -> SupportTicketResponse:
        return SupportTicketResponse(
            ticket_id=str(uuid4()),
            ticket_type=payload.ticket_type,
            status=TicketStatus.OPEN,
            subject=payload.subject,
            description=payload.description,
        )
