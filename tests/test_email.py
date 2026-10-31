import pytest
from fastapi import status

def test_send_email_endpoint(client):
    payload = {
        "recipient_email": "hello@sports.com",
        "user_name": "Test Fan",
        "subject": "Welcome to Sports Portal",
        "message": "Welcome to our enterprise sports platform!"
    }
    resp = client.post("/api/v1/emails/send", json=payload)
    assert resp.status_code == status.HTTP_202_ACCEPTED
    data = resp.json()
    assert data["status"] == "queued"
    assert "hello@sports.com" in data["message"]

