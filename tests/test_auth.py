import pytest
from fastapi import status

def test_signup_and_verify_flow(client):
    # 1. Signup
    signup_data = {
        "name": "Integration User",
        "email": "integration_user@sports.com",
        "address": "Dhaka, Bangladesh",
        "password": "SecurePassword123!"
    }
    resp = client.post("/api/v1/auth/signup", json=signup_data)
    assert resp.status_code == status.HTTP_202_ACCEPTED
    body = resp.json()
    assert body["status"] == "otp_sent"
    otp = body.get("dev_otp")
    assert otp is not None
    assert len(otp) == 6

    # 2. Duplicate signup should be handled or blocked
    # Try invalid OTP verification
    verify_bad = client.post("/api/v1/auth/verify-signup", json={
        "email": "integration_user@sports.com",
        "otp_code": "000000"
    })
    assert verify_bad.status_code == status.HTTP_400_BAD_REQUEST

    # 3. Valid OTP verification
    verify_good = client.post("/api/v1/auth/verify-signup", json={
        "email": "integration_user@sports.com",
        "otp_code": otp
    })
    assert verify_good.status_code == status.HTTP_200_OK
    assert verify_good.json()["status"] == "verified"


def test_login_and_device_limit_enforcement(client):
    # Setup verified user
    email = "device_tester@sports.com"
    pwd = "DevicePassword123!"
    s_resp = client.post("/api/v1/auth/signup", json={
        "name": "Device Tester",
        "email": email,
        "address": "Gulshan",
        "password": pwd
    })
    otp = s_resp.json()["dev_otp"]
    client.post("/api/v1/auth/verify-signup", json={"email": email, "otp_code": otp})

    # Helper function to perform login & return access_token
    def login_device(dev_type: str, dev_name: str) -> str:
        login_res = client.post("/api/v1/auth/login", json={"email": email, "password": pwd})
        assert login_res.status_code == status.HTTP_202_ACCEPTED
        l_otp = login_res.json()["dev_otp"]
        verify_res = client.post("/api/v1/auth/verify-login", json={
            "email": email,
            "otp_code": l_otp,
            "device_type": dev_type,
            "device_name": dev_name
        })
        assert verify_res.status_code == status.HTTP_200_OK
        return verify_res.json()["access_token"]

    # --- Test Computer Limit (Max 2 computers) ---
    pc1_token = login_device("computer", "PC-1")
    pc2_token = login_device("computer", "PC-2")

    # Both PC-1 and PC-2 should be able to access /me
    me1 = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {pc1_token}"})
    me2 = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {pc2_token}"})
    assert me1.status_code == status.HTTP_200_OK
    assert me2.status_code == status.HTTP_200_OK

    # Log in 3rd Computer -> PC-1 MUST be auto-logged out
    pc3_token = login_device("computer", "PC-3")
    me3 = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {pc3_token}"})
    assert me3.status_code == status.HTTP_200_OK

    # PC-1 must now fail with 401 (Session revoked)
    me1_revoked = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {pc1_token}"})
    assert me1_revoked.status_code == status.HTTP_401_UNAUTHORIZED

    # PC-2 should still be valid
    me2_active = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {pc2_token}"})
    assert me2_active.status_code == status.HTTP_200_OK

    # --- Test Phone Limit (Max 1 phone) ---
    phone1_token = login_device("phone", "iPhone 15")
    phone1_me = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {phone1_token}"})
    assert phone1_me.status_code == status.HTTP_200_OK

    # Log in 2nd Phone -> iPhone 15 MUST be auto-logged out
    phone2_token = login_device("phone", "Samsung Galaxy S24")
    phone2_me = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {phone2_token}"})
    assert phone2_me.status_code == status.HTTP_200_OK

    # Phone 1 must now be revoked
    phone1_revoked = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {phone1_token}"})
    assert phone1_revoked.status_code == status.HTTP_401_UNAUTHORIZED


def test_forgot_and_reset_password_security(client):
    email = "reset_tester@sports.com"
    pwd = "OldPassword123!"
    new_pwd = "BrandNewPassword789!"
    
    # 1. Signup & verify
    s_resp = client.post("/api/v1/auth/signup", json={
        "name": "Reset Tester",
        "email": email,
        "address": "Dhanmondi",
        "password": pwd
    })
    otp = s_resp.json()["dev_otp"]
    client.post("/api/v1/auth/verify-signup", json={"email": email, "otp_code": otp})

    # 2. Log in and get active session
    l_resp = client.post("/api/v1/auth/login", json={"email": email, "password": pwd})
    l_otp = l_resp.json()["dev_otp"]
    v_resp = client.post("/api/v1/auth/verify-login", json={
        "email": email,
        "otp_code": l_otp,
        "device_type": "computer",
        "device_name": "Laptop"
    })
    token_before_reset = v_resp.json()["access_token"]
    assert client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token_before_reset}"}).status_code == 200

    # 3. Request forgot password OTP
    f_resp = client.post("/api/v1/auth/forgot-password", json={"email": email})
    assert f_resp.status_code == status.HTTP_202_ACCEPTED
    reset_otp = f_resp.json()["dev_otp"]

    # 4. Reset password
    r_resp = client.post("/api/v1/auth/reset-password", json={
        "email": email,
        "otp_code": reset_otp,
        "new_password": new_pwd
    })
    assert r_resp.status_code == status.HTTP_200_OK

    # 5. Security invariant: Old active session must now be REVOKED
    me_revoked = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token_before_reset}"})
    assert me_revoked.status_code == status.HTTP_401_UNAUTHORIZED

    # 6. Old password must fail
    assert client.post("/api/v1/auth/login", json={"email": email, "password": pwd}).status_code == 401

    # 7. New password must succeed
    new_login = client.post("/api/v1/auth/login", json={"email": email, "password": new_pwd})
    assert new_login.status_code == status.HTTP_202_ACCEPTED

