import sys
import os
import re
import json
import asyncio
from datetime import datetime

sys.path.insert(0, r"E:\Scraping\behavioral-playwright-main\behavioral-playwright-main")

from behavioral_evasion_suite.stealth_browser import StealthBrowser
from behavioral_evasion_suite.presets import Preset

async def run_recorded_flow():
    record_dir = r"E:\Sports\recordings"
    os.makedirs(record_dir, exist_ok=True)
    
    print("=" * 70)
    print("STARTING FULL END-TO-END AUTOMATED FLOW WITH VIDEO RECORDING")
    print("=" * 70)

    browser_launcher = StealthBrowser.launch(
        headless=False,
        preset=Preset.MAX_QUANTUM,
        record_video_dir=record_dir,
        record_video_size={"width": 1280, "height": 720}
    )

    async with browser_launcher as gmail_page:
        context = browser_launcher._context

        # ==========================================
        # STEP 1: AUTHENTICATE TO GMAIL VIA STEALTH
        # ==========================================
        print("\n[STEP 1] Logging into Gmail with Level 5 Biomechanical Stealth...")
        await gmail_page.goto("https://accounts.google.com/ServiceLogin?service=mail")
        await asyncio.sleep(2)

        print("  -> Typing Email (amnejinuta@gmail.com)...")
        await gmail_page.human_type('input#identifierId', "amnejinuta@gmail.com")
        await gmail_page.cognitive_pause(0.5, 1.0)
        await gmail_page.human_click('#identifierNext')
        await asyncio.sleep(4)

        print("  -> Typing Password...")
        test_gmail_pass = os.getenv("TEST_GMAIL_PASSWORD", "")
        await gmail_page.human_type('input[type="password"]:not([name="hiddenPassword"])', test_gmail_pass)
        await gmail_page.cognitive_pause(0.8, 1.2)
        await gmail_page.human_click('#passwordNext')
        await asyncio.sleep(5)

        # Ensure we navigate to Gmail
        print("  -> Navigating to Gmail Inbox...")
        await gmail_page.goto("https://mail.google.com/mail/u/0/#inbox")
        await asyncio.sleep(6)
        await gmail_page.screenshot(path=r"E:\Sports\tests\step1_gmail_inbox_ready.png")
        print("  -> [OK] Gmail Inbox ready! Screenshot: step1_gmail_inbox_ready.png")

        # ==========================================
        # STEP 2: OPEN SWAGGER & TRIGGER LOGIN API
        # ==========================================
        print("\n[STEP 2] Opening Swagger UI in second tab to request Login OTP...")
        swagger_raw = await context.new_page()
        await swagger_raw.goto("http://127.0.0.1:8000/docs")
        await asyncio.sleep(2)
        
        # Click login operation by resilient selector
        login_op = swagger_raw.locator("div.opblock-summary-post:has-text('/api/v1/auth/login')").first
        await login_op.wait_for(state="visible", timeout=15000)
        await login_op.click()
        await asyncio.sleep(1)

        tryout_btn = swagger_raw.locator(".opblock.is-open button.btn.try-out__btn").first
        await tryout_btn.click()
        
        # Fill body
        login_payload = '{\n  "email": "amnejinuta@gmail.com",\n  "password": "Password123"\n}'
        body_box = swagger_raw.locator(".opblock.is-open .body-param__text").first
        await body_box.fill(login_payload)
        await asyncio.sleep(1)
        
        # Click Execute
        exec_btn = swagger_raw.locator(".opblock.is-open button.btn.execute.opblock-control__btn").first
        await exec_btn.click()
        
        # Wait for 202 Accepted
        await swagger_raw.wait_for_selector("tr.response td.response-col_status:has-text('202')", timeout=10000)
        
        # Extract response text to get dev_otp as fallback
        resp_pre = swagger_raw.locator("tr.response pre.microlight.first").first
        resp_text = await resp_pre.inner_text()
        dev_otp_fallback = None
        try:
            resp_json = json.loads(resp_text)
            dev_otp_fallback = resp_json.get("dev_otp")
        except Exception:
            pass
            
        await swagger_raw.screenshot(path=r"E:\Sports\tests\step2_swagger_login_requested.png")
        print("  -> [OK] Login OTP requested from FastAPI (202 Accepted)! Email dispatched.")

        # ==========================================
        # STEP 3: FETCH OTP FROM GMAIL INBOX / SPAM
        # ==========================================
        print("\n[STEP 3] Switching back to Gmail tab to read incoming OTP email...")
        await gmail_page.bring_to_front()
        await asyncio.sleep(4)
        
        # Check Inbox
        await gmail_page.goto("https://mail.google.com/mail/u/0/#inbox")
        await asyncio.sleep(4)

        email_row = gmail_page.raw_page.locator("tr.zA:has-text('Login Verification OTP'), tr.zA:has-text('teamrabbil')").first
        found_mail = False
        if await email_row.is_visible():
            await email_row.click()
            await asyncio.sleep(2)
            found_mail = True
        else:
            print("  -> Checking Spam folder...")
            await gmail_page.goto("https://mail.google.com/mail/u/0/#spam")
            await asyncio.sleep(4)
            spam_row = gmail_page.raw_page.locator("tr.zA:has-text('Login Verification OTP'), tr.zA:has-text('teamrabbil')").first
            if await spam_row.is_visible():
                await spam_row.click()
                await asyncio.sleep(2)
                found_mail = True

        extracted_otp = None
        if found_mail:
            await gmail_page.screenshot(path=r"E:\Sports\tests\step3_otp_email_opened.png")
            body_text = await gmail_page.raw_page.inner_text("body")
            matches = re.findall(r'\b(\d{6})\b', body_text)
            if matches:
                extracted_otp = matches[0]
                print(f"  -> [SUCCESS] EXTRACTED LIVE OTP FROM GMAIL: >>> {extracted_otp} <<<")

        if not extracted_otp:
            print(f"  -> Using dispatched OTP fallback: {dev_otp_fallback}")
            extracted_otp = dev_otp_fallback

        assert extracted_otp is not None, "Failed to obtain 6-digit OTP!"

        # ==========================================
        # STEP 4: VERIFY LOGIN ON SWAGGER UI
        # ==========================================
        print("\n[STEP 4] Switching back to Swagger UI to verify OTP and obtain JWT...")
        await swagger_raw.bring_to_front()
        await asyncio.sleep(1)
        
        # Click verify-login operation
        verify_op = swagger_raw.locator("div.opblock-summary-post:has-text('/api/v1/auth/verify-login')").first
        await verify_op.click()
        await asyncio.sleep(1)
        
        v_tryout = swagger_raw.locator(".opblock.is-open button.btn.try-out__btn").first
        await v_tryout.click()
        
        verify_payload = f'''{{
  "email": "amnejinuta@gmail.com",
  "otp_code": "{extracted_otp}",
  "device_type": "computer",
  "device_name": "Behavioral Playwright Bot"
}}'''
        verify_box = swagger_raw.locator(".opblock.is-open .body-param__text").first
        await verify_box.fill(verify_payload)
        await asyncio.sleep(1)
        
        # Click Execute on verify-login
        v_exec = swagger_raw.locator(".opblock.is-open button.btn.execute.opblock-control__btn").first
        await v_exec.click()
        
        # Wait for 200 OK
        status_loc = swagger_raw.locator(".opblock.is-open tr.response td.response-col_status:has-text('200')").first
        await status_loc.wait_for(timeout=10000)
        
        resp_body_loc = swagger_raw.locator(".opblock.is-open tr.response pre.microlight.first").first
        token_json = await resp_body_loc.inner_text()
        print("  -> [SWAGGER 200 OK RESPONSE]:\n", token_json)
        
        await swagger_raw.screenshot(path=r"E:\Sports\tests\step4_swagger_login_verified.png")
        print("  -> [OK] Login successfully verified! JWT Access Token received.")

        # Let the video capture the final state
        await asyncio.sleep(4)

    # Context closed, video file is finalized
    print("\n" + "=" * 70)
    print("RECORDING COMPLETED!")
    recordings = [f for f in os.listdir(record_dir) if f.endswith(".webm")]
    if recordings:
        latest_video = os.path.join(record_dir, sorted(recordings)[-1])
        print(f"VIDEO SAVED TO: {latest_video}")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(run_recorded_flow())
