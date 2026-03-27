from app.workers.celery_app import celery_app


@celery_app.task(name="notifications.send_sms")
def send_sms(phone_number: str, message: str) -> dict[str, str]:
    return {"phone_number": phone_number, "message": message, "status": "queued"}


@celery_app.task(name="notifications.send_push")
def send_push(user_id: str, title: str, body: str) -> dict[str, str]:
    return {"user_id": user_id, "title": title, "body": body, "status": "queued"}
