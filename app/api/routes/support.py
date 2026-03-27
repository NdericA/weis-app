from fastapi import APIRouter

from app.schemas.support import SupportTicketCreate, SupportTicketResponse
from app.services.support_service import SupportService

router = APIRouter()
service = SupportService()


@router.post("/tickets", response_model=SupportTicketResponse)
def create_ticket(payload: SupportTicketCreate) -> SupportTicketResponse:
    return service.create_ticket(payload)
