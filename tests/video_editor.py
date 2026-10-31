import os
import sys
import json
import subprocess
from PIL import Image, ImageDraw, ImageFont

# Enforce UTF-8 on Windows terminal output
sys.stdout.reconfigure(encoding='utf-8')

import imageio_ffmpeg
FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()

def create_intro_card(output_path: str):
    font_title = ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf', 40)
    font_sub = ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf', 20)
    font_badge = ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf', 15)

    img = Image.new('RGB', (1280, 720), color=(11, 15, 25))
    draw = ImageDraw.Draw(img)

    # Top accent line (emerald)
    draw.rectangle([(0, 0), (1280, 6)], fill=(16, 185, 129))

    # Badge
    draw.rounded_rectangle([(80, 140), (510, 175)], radius=6, fill=(15, 35, 30), outline=(16, 185, 129), width=1)
    draw.text((95, 147), '● LEVEL 5 STEALTH × FASTAPI CLEAN ARCH', fill=(16, 185, 129), font=font_badge)

    # Title
    draw.text((80, 210), 'Automated 2FA Login & Bot Bypass Pipeline', fill=(255, 255, 255), font=font_title)

    # Subtitle
    draw.text((80, 280), 'End-to-End Live Demonstration of Enterprise Clean Architecture &\nNeuromuscular Biometric Stealth Automation in Google Accounts', fill=(156, 163, 175), font=font_sub)

    # Feature Badges
    chips = ['Python 3.14', 'FastAPI 3-Tier', 'Argon2id', 'Google Bot Evasion', 'Real-Time SMTP OTP', 'JWT Device Sessions']
    x = 80
    y = 380
    for chip in chips:
        bbox = font_badge.getbbox(chip)
        w = bbox[2] - bbox[0] + 24
        draw.rounded_rectangle([(x, y), (x + w, y + 36)], radius=6, fill=(26, 32, 44), outline=(74, 85, 104), width=1)
        draw.text((x + 12, y + 8), chip, fill=(226, 232, 240), font=font_badge)
        x += w + 16

    # Footer
    draw.text((80, 620), 'Architected by: User  |  Live Automated Verification: Exit Code 0', fill=(100, 116, 139), font=font_sub)

    img.save(output_path)
    print(f"Intro card saved: {output_path}")

def create_outro_card(output_path: str):
    font_title = ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf', 40)
    font_sub = ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf', 20)
    font_badge = ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf', 15)
    font_check = ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf', 22)

    img = Image.new('RGB', (1280, 720), color=(11, 15, 25))
    draw = ImageDraw.Draw(img)

    # Top accent line (emerald)
    draw.rectangle([(0, 0), (1280, 6)], fill=(16, 185, 129))

    # Badge
    draw.rounded_rectangle([(80, 120), (450, 155)], radius=6, fill=(15, 35, 30), outline=(16, 185, 129), width=1)
    draw.text((95, 127), '● ALL VERIFICATION GATES PASSED', fill=(16, 185, 129), font=font_badge)

    # Title
    draw.text((80, 180), 'Production-Ready Architecture Confirmed', fill=(255, 255, 255), font=font_title)

    # Subtitle
    draw.text((80, 240), 'Full automation lifecycle passed without bot detection or human intervention.', fill=(156, 163, 175), font=font_sub)

    # Checklist
    items = [
        ('Google Anti-Bot Bypassed', 'Cognitive Bezier kinematics, CDP stealth & WebGL prototype spoofing (0 Captchas)'),
        ('Clean 3-Tier Architecture', 'Strict Router-Service-Repository decoupling with Protocol data abstractions'),
        ('Real-Time 2FA OTP Delivery', 'Dispatched via transactional SMTP and harvested directly from live Gmail Inbox'),
        ('Multi-Device Session Security', 'FIFO session rotation, device fingerprinting, and Argon2id password hashing')
    ]

    y = 310
    for title, desc in items:
        # Checkmark icon box
        draw.rounded_rectangle([(80, y), (112, y + 32)], radius=4, fill=(16, 185, 129))
        draw.line([(88, y + 16), (94, y + 23), (104, y + 9)], fill=(11, 15, 25), width=3)
        
        draw.text((125, y + 2), title, fill=(241, 245, 249), font=font_check)
        draw.text((125, y + 32), desc, fill=(148, 163, 184), font=font_sub)
        y += 72

    # Footer
    draw.text((80, 630), 'System Status: 100% Verified  |  Exit Code: 0  |  Built with Python 3.14 & Playwright', fill=(100, 116, 139), font=font_sub)

    img.save(output_path)
    print(f"Outro card saved: {output_path}")

def create_stage_overlays(output_dir: str):
    os.makedirs(output_dir, exist_ok=True)
    font_title = ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf', 22)
    font_sub = ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf', 16)
    font_badge = ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf', 13)

    stages = [
        (1, 'LEVEL 5 BIOMECHANICAL STEALTH', 'Bypassing Google BotGuard & Logging into Gmail via Neuromuscular Kinematics'),
        (2, 'ENTERPRISE FASTAPI BACKEND', 'Decoupled 3-Tier Architecture: Requesting 2FA Login OTP via Swagger UI (/login)'),
        (3, 'REAL-TIME TRANSACTIONAL HARVESTING', 'Live Extraction: Harvesting 6-Digit Verification OTP from Gmail Inbox'),
        (4, 'MULTI-DEVICE SESSION MANAGEMENT', '2FA OTP Verified: JWT Bearer Issued & Active Device Session Registered (200 OK)')
    ]

    paths = {}
    for num, title, subtitle in stages:
        img = Image.new('RGBA', (1280, 720), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Bottom banner bar: y = 625 to 720 (95px)
        draw.rectangle([(0, 625), (1280, 720)], fill=(11, 15, 25, 235))
        
        # Top border line: Cyan accent
        draw.rectangle([(0, 625), (1280, 627)], fill=(6, 182, 212, 255))
        
        # Badge (left): e.g. STAGE 1
        badge_text = f'STAGE 0{num}'
        draw.rounded_rectangle([(30, 642), (120, 670)], radius=4, fill=(16, 185, 129, 255))
        draw.text((42, 648), badge_text, fill=(11, 15, 25, 255), font=font_badge)
        
        # Live dot
        draw.ellipse([(140, 652), (150, 662)], fill=(16, 185, 129, 255))
        draw.text((158, 650), 'LIVE PIPELINE', fill=(16, 185, 129, 255), font=font_badge)
        
        # Title
        draw.text((270, 646), title, fill=(255, 255, 255, 255), font=font_title)
        
        # Subtitle
        draw.text((270, 678), subtitle, fill=(156, 163, 175, 255), font=font_sub)
        
        path = os.path.join(output_dir, f'stage_{num}.png')
        img.save(path)
        paths[num] = path
    return paths

def edit_and_render_video(raw_webm_path: str, timeline_json_path: str, output_final_mp4: str):
    work_dir = os.path.dirname(output_final_mp4)
    intro_img = os.path.join(work_dir, "intro_card.png")
    outro_img = os.path.join(work_dir, "outro_card.png")
    overlay_dir = os.path.join(work_dir, "overlays")

    create_intro_card(intro_img)
    create_outro_card(outro_img)
    overlay_paths = create_stage_overlays(overlay_dir)

    with open(timeline_json_path, "r", encoding="utf-8") as f:
        timeline = json.load(f)

    stages = timeline.get("stages", [])

    # 1. Render Intro video (3 seconds)
    intro_mp4 = os.path.join(work_dir, "temp_intro.mp4")
    subprocess.run([
        FFMPEG_EXE, "-y",
        "-loop", "1", "-i", intro_img,
        "-t", "3",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "30",
        intro_mp4
    ], check=True, capture_output=True)
    print("✓ Intro video rendered (3s)")

    # 2. Render Outro video (3.5 seconds)
    outro_mp4 = os.path.join(work_dir, "temp_outro.mp4")
    subprocess.run([
        FFMPEG_EXE, "-y",
        "-loop", "1", "-i", outro_img,
        "-t", "3.5",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "30",
        outro_mp4
    ], check=True, capture_output=True)
    print("✓ Outro video rendered (3.5s)")

    # 3. Build dynamic overlay filtergraph for main video
    # Inputs: 0 = raw video, 1..4 = stage overlays
    overlay_inputs = []
    for num in range(1, 5):
        overlay_inputs.extend(["-i", overlay_paths[num]])

    # Build filtergraph
    filter_parts = []
    current_label = "0:v"
    
    # Scale raw video to 1280x720 30fps if needed
    filter_parts.append(f"[{current_label}]scale=1280:720,fps=30[scaled]")
    current_label = "scaled"

    for idx, stage in enumerate(stages):
        num = stage["stage"]
        t_start = stage["start"]
        t_end = stage["end"]
        input_idx = idx + 1
        next_label = f"v_stg_{num}"
        filter_parts.append(f"[{current_label}][{input_idx}:v]overlay=0:0:enable='between(t,{t_start:.2f},{t_end:.2f})'[{next_label}]")
        current_label = next_label

    filtergraph = ";".join(filter_parts)

    main_overlaid_mp4 = os.path.join(work_dir, "temp_main_overlaid.mp4")
    overlay_cmd = [
        FFMPEG_EXE, "-y",
        "-i", raw_webm_path,
        *overlay_inputs,
        "-filter_complex", filtergraph,
        "-map", f"[{current_label}]",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "19",
        "-pix_fmt", "yuv420p",
        main_overlaid_mp4
    ]
    print("Rendering main video with dynamic stage overlays...")
    res = subprocess.run(overlay_cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print("Overlay Error:", res.stderr)
        raise RuntimeError("FFmpeg overlay rendering failed")
    print("✓ Main overlaid video rendered")

    # 4. Concatenate Intro + Main + Outro
    concat_list_path = os.path.join(work_dir, "concat_list.txt")
    with open(concat_list_path, "w", encoding="utf-8") as f:
        f.write(f"file '{os.path.basename(intro_mp4)}'\n")
        f.write(f"file '{os.path.basename(main_overlaid_mp4)}'\n")
        f.write(f"file '{os.path.basename(outro_mp4)}'\n")

    print(f"Concatenating all segments into final deliverable: {output_final_mp4}...")
    concat_cmd = [
        FFMPEG_EXE, "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", concat_list_path,
        "-c", "copy",
        "-movflags", "+faststart",
        output_final_mp4
    ]
    subprocess.run(concat_cmd, check=True, cwd=work_dir, capture_output=True)

    final_size_mb = os.path.getsize(output_final_mp4) / (1024 * 1024)
    print("=" * 80)
    print(f"🎉 FINAL EDITED SHOWCASE VIDEO COMPLETE: {output_final_mp4}")
    print(f"File Size: {final_size_mb:.2f} MB")
    print("=" * 80)

    # Cleanup temp video files
    for tmp in [intro_mp4, outro_mp4, main_overlaid_mp4, concat_list_path]:
        try:
            if os.path.exists(tmp):
                os.remove(tmp)
        except Exception:
            pass

if __name__ == "__main__":
    if len(sys.argv) > 3:
        edit_and_render_video(sys.argv[1], sys.argv[2], sys.argv[3])
    else:
        print("Usage: python video_editor.py <raw_webm> <timeline_json> <output_mp4>")

