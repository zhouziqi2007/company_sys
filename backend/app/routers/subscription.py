from fastapi import APIRouter
from pydantic import BaseModel

from app.subscription import build_subscription_reply

router = APIRouter(prefix="/api/subscription", tags=["订阅"])


class SubscriptionRequest(BaseModel):
    message: str


@router.post("/reply")
def reply(req: SubscriptionRequest):
    intent, text = build_subscription_reply(req.message)
    return {"intent": intent, "reply": text}
