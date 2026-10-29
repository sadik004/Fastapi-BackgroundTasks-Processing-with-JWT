from fastapi import APIRouter, BackgroundTasks, status
from app.schemas.email import EmailRequest, EmailResponse
from app.services.email_service import EmailService

router = APIRouter()

@router.post(
    "/send",
    response_model=EmailResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="ইমেইল পাঠানোর এপিআই"
)
async def send_email_endpoint(
    payload: EmailRequest,
    background_tasks: BackgroundTasks
):
    # payload.message-ও সাথে পাঠিয়ে দেওয়া হলো
    background_tasks.add_task(
        EmailService.send_welcome_email,
        recipient=payload.recipient_email,
        subject=payload.subject,
        user_name=payload.user_name,
        message_body=payload.message  # <-- পাস করা হলো
    )
    
    return EmailResponse(
        status="queued",
        message=f"{payload.recipient_email} ঠিকানায় ইমেইল পাঠানোর কাজ কিউতে নেওয়া হয়েছে।"
    )