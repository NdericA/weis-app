class NotificationService:
    def queue_sms(self, phone_number: str, message: str) -> dict[str, str]:
        return {"channel": "sms", "recipient": phone_number, "message": message, "status": "queued"}

    def queue_push(self, user_id: str, title: str, body: str) -> dict[str, str]:
        return {"channel": "push", "recipient": user_id, "title": title, "body": body, "status": "queued"}
