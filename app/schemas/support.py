from pydantic import BaseModel


class SupportTicketCreate(BaseModel):
    ticket_type: str
    subject: str
    description: str
    trip_id: str | None = None


class SupportTicketResponse(BaseModel):
    ticket_id: str
    ticket_type: str
    status: str
    subject: str
    description: str
