from fastapi import APIRouter, BackgroundTasks, status
from app.schemas.email import EmailRequest, EmailResponse
from app.services.email_service import EmailService

router = APIRouter()

@router.post(
    "/send",
    response_model=EmailResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Dispatch async non-blocking transactional email"
)
async def send_email_endpoint(
    payload: EmailRequest,
    background_tasks: BackgroundTasks
):
    # Enqueue background email delivery task without blocking HTTP thread
    background_tasks.add_task(
        EmailService.send_welcome_email,
        recipient=payload.recipient_email,
        subject=payload.subject,
        user_name=payload.user_name,
        message_body=payload.message
    )
    
    return EmailResponse(
        status="queued",
        message=f"Email delivery for {payload.recipient_email} has been queued successfully."
    )
