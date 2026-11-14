import os
import sys
import math
import subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1920, 1080
FPS = 30
DURATION = 16
TOTAL_FRAMES = FPS * DURATION  # 480 frames

FFMPEG_EXE = r"C:\Users\conta\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.2-full_build\bin\ffmpeg.exe"
OUTPUT_MP4 = r"C:\DEV\SirDeep\assets\branding\demo.mp4"
CARD_IMG_PATH = r"C:\Users\conta\.gemini\antigravity\brain\ff67f1b1-167a-4b31-92f4-89c1759b60a2\owner_contributor_card.png"
if not os.path.exists(CARD_IMG_PATH):
    CARD_IMG_PATH = r"C:\DEV\SirDeep\assets\branding\sample_card.png"

FONT_DIR = r"C:\Windows\Fonts"
font_hero = ImageFont.truetype(os.path.join(FONT_DIR, "segoeuib.ttf"), 52)
font_title = ImageFont.truetype(os.path.join(FONT_DIR, "segoeuib.ttf"), 34)
font_subtitle = ImageFont.truetype(os.path.join(FONT_DIR, "segoeui.ttf"), 22)
font_badge = ImageFont.truetype(os.path.join(FONT_DIR, "segoeuib.ttf"), 14)
font_mono_lg = ImageFont.truetype(os.path.join(FONT_DIR, "consolab.ttf"), 24)
font_mono = ImageFont.truetype(os.path.join(FONT_DIR, "consola.ttf"), 19)
font_mono_sm = ImageFont.truetype(os.path.join(FONT_DIR, "consola.ttf"), 15)

card_raw = Image.open(CARD_IMG_PATH).convert("RGBA") if os.path.exists(CARD_IMG_PATH) else None

def draw_pill(draw, x, y, text, border_col=(56, 189, 248, 180), bg_col=(15, 23, 42, 220), text_col=(0, 229, 255)):
    bbox = font_badge.getbbox(text)
    pw = (bbox[2] - bbox[0]) + 24
    ph = 28
    draw.rounded_rectangle([x, y, x + pw, y + ph], radius=6, fill=bg_col, outline=border_col, width=1)
    draw.text((x + 12, y + 6), text, fill=text_col, font=font_badge)
    return pw

def render_frame(f: int) -> Image.Image:
    t = f / FPS
    # Deep obsidian background
    img = Image.new("RGB", (W, H), (6, 8, 12))
    draw = ImageDraw.Draw(img)

    # Ambient radial background lighting (cold icy glow)
    center_glow_radius = 500
    for r in range(12, 0, -1):
        rad = r * 45
        alpha = int(18 * (r / 12))
        draw.ellipse([W//2 - rad, H//2 - rad // 2, W//2 + rad, H//2 + rad // 2], outline=(0, 210, 255, alpha), width=3)

    # Top Minimal Header (Persistent across whole video)
    draw.line([140, 70, W - 140, 70], fill=(26, 32, 44), width=1)
    draw.text((140, 36), "OPENWINTER", fill=(255, 255, 255), font=font_badge)
    draw.text((250, 36), "//", fill=(71, 85, 105), font=font_badge)
    draw.text((275, 36), "SIRDEEP AUTONOMOUS CORE ENGINE", fill=(148, 163, 184), font=font_badge)

    time_str = f"{t:05.2f}s / {DURATION:02d}.00s"
    draw.text((W - 260, 36), time_str, fill=(71, 85, 105), font=font_mono_sm)
    # Green pulse dot
    pulse = 0.5 + 0.5 * math.sin(t * 6)
    dot_alpha = int(150 + 105 * pulse)
    draw.ellipse([W - 155, 41, W - 143, 53], fill=(16, 185, 129, dot_alpha))

    # Bottom status bar
    draw.line([140, H - 70, W - 140, H - 70], fill=(26, 32, 44), width=1)
    draw.text((140, H - 52), "ZERO TELEMETRY • HIGH-DPI PIL RENDERER • ASYNC DISCORD GATEWAY V10", fill=(71, 85, 105), font=font_badge)
    draw.text((W - 350, H - 52), "GITHUB.COM/OPENWINTER/SIRDEEP", fill=(0, 229, 255), font=font_badge)

    # -------------------------------------------------------------
    # ACT 1: Core Daemon Initialization (0.0s - 3.8s / frames 0 - 114)
    # -------------------------------------------------------------
    if f < 114:
        panel_x, panel_y, panel_w, panel_h = 240, 140, 1440, 760
        # Dark glass panel
        draw.rounded_rectangle([panel_x, panel_y, panel_x + panel_w, panel_y + panel_h], radius=10, fill=(10, 13, 20), outline=(30, 41, 59), width=1)
        # Inner top bar
        draw.rectangle([panel_x, panel_y, panel_x + panel_w, panel_y + 46], fill=(15, 20, 30))
        draw.line([panel_x, panel_y + 46, panel_x + panel_w, panel_y + 46], fill=(30, 41, 59), width=1)
        draw.text((panel_x + 24, panel_y + 14), "CORE DAEMON BOOT // CONTAINER INITIALIZATION", fill=(148, 163, 184), font=font_badge)
        draw_pill(draw, panel_x + panel_w - 180, panel_y + 9, "HEALTH: OK", border_col=(16, 185, 129, 200), text_col=(52, 211, 153))

        cy = panel_y + 80
        cx = panel_x + 36

        # Monospace execution stream
        cmd = "$ docker compose up -d --build"
        char_c = min(len(cmd), int(f * 0.9))
        draw.text((cx, cy), cmd[:char_c] + ("_" if (f // 6) % 2 == 0 else ""), fill=(0, 229, 255), font=font_mono_lg)

        if f >= 30:
            cy += 48
            draw.text((cx, cy), "[+] Running 2/2", fill=(148, 163, 184), font=font_mono)
            cy += 28
            draw.text((cx, cy), " ✔ Network sirdeep_network    Created", fill=(52, 211, 153), font=font_mono)
            cy += 28
            draw.text((cx, cy), " ✔ Container sirdeep-core     Started [Process Daemon]", fill=(52, 211, 153), font=font_mono)

        if f >= 55:
            cy += 48
            draw.line([cx, cy - 10, cx + panel_w - 72, cy - 10], fill=(26, 32, 44), width=1)
            draw.text((cx, cy), "[18:24:00.104] [INIT] SirDeep Gateway Daemon v1.0.0 initializing...", fill=(100, 116, 139), font=font_mono)
            cy += 30
            draw.text((cx, cy), "[18:24:00.320] [GATEWAY] WebSocket connected to Gateway v10 (Heartbeat: 41.25ms)", fill=(226, 232, 240), font=font_mono)
            cy += 30
            draw.text((cx, cy), "[18:24:00.412] [SERVICES] Loaded: AuditSentinel, AIInference, RadioStreamer, Leveling", fill=(56, 189, 248), font=font_mono)
            cy += 30
            draw.text((cx, cy), "[18:24:00.589] [SECURITY] Anti-Nuke rate limiter engaged (Threshold: 3 ops/min)", fill=(245, 158, 11), font=font_mono)
            cy += 30
            draw.text((cx, cy), "[18:24:00.702] [DISCORD] Logged in as SirDeep#1316 (Guild: OpenWinter)", fill=(16, 185, 129), font=font_mono_lg)

        if f >= 80:
            # Bottom highlight card inside panel
            hy = panel_y + panel_h - 120
            draw.rounded_rectangle([cx, hy, cx + panel_w - 72, hy + 85], radius=8, fill=(15, 23, 42), outline=(56, 189, 248, 120), width=1)
            draw.text((cx + 24, hy + 18), "⚡ SYSTEM READY FOR COMMUNITY ORCHESTRATION", fill=(0, 229, 255), font=font_mono_lg)
            draw.text((cx + 24, hy + 48), "All Gateway intents validated • SQLite WAL storage verified • Audio transcoder loaded", fill=(148, 163, 184), font=font_mono_sm)

    # -------------------------------------------------------------
    # ACT 2: AI Cognitive Pipeline (3.8s - 7.6s / frames 114 - 228)
    # -------------------------------------------------------------
    elif f < 228:
        panel_x, panel_y, panel_w, panel_h = 240, 140, 1440, 760
        draw.rounded_rectangle([panel_x, panel_y, panel_x + panel_w, panel_y + panel_h], radius=10, fill=(10, 13, 20), outline=(30, 41, 59), width=1)
        draw.rectangle([panel_x, panel_y, panel_x + panel_w, panel_y + 46], fill=(15, 20, 30))
        draw.line([panel_x, panel_y + 46, panel_x + panel_w, panel_y + 46], fill=(30, 41, 59), width=1)
        draw.text((panel_x + 24, panel_y + 14), "AI COGNITIVE PIPELINE // ASYNC CODE REASONING", fill=(148, 163, 184), font=font_badge)
        draw_pill(draw, panel_x + panel_w - 220, panel_y + 9, "MODEL: CLAUDE / OLLAMA", border_col=(0, 229, 255, 180), text_col=(0, 229, 255))

        # User Query Box
        qy = panel_y + 75
        qx = panel_x + 36
        draw.rounded_rectangle([qx, qy, qx + panel_w - 72, qy + 80], radius=8, fill=(14, 18, 28), outline=(30, 41, 59), width=1)
        draw.text((qx + 20, qy + 16), "DEVELOPER QUERY", fill=(0, 229, 255), font=font_badge)
        draw.text((qx + 20, qy + 40), "\"How to achieve zero lock contention in SQLite with multi-threaded Python services?\"", fill=(255, 255, 255), font=font_subtitle)

        # AI Stream Response
        ry = qy + 105
        draw.text((qx, ry), "SIRDEEP RESPONSE [STREAMING GENERATION]", fill=(52, 211, 153), font=font_badge)
        ry += 28

        # Code Block
        code_box_h = 360
        draw.rounded_rectangle([qx, ry, qx + panel_w - 72, ry + code_box_h], radius=8, fill=(7, 9, 14), outline=(30, 41, 59), width=1)
        
        # Code lines
        code_lines = [
            ("# Enable Write-Ahead Logging to decouple readers from writers", (100, 116, 139)),
            ("conn = sqlite3.connect('database.db', timeout=30.0)", (226, 232, 240)),
            ("conn.execute('PRAGMA journal_mode = WAL;')", (56, 189, 248)),
            ("conn.execute('PRAGMA synchronous = NORMAL;')", (56, 189, 248)),
            ("conn.execute('PRAGMA busy_timeout = 5000;')", (56, 189, 248)),
            ("", (0, 0, 0)),
            ("# Dedicated WAL checkpoint thread prevents write stall spikes", (100, 116, 139)),
            ("def checkpoint_worker():", (0, 229, 255)),
            ("    while not stop_signal.is_set():", (226, 232, 240)),
            ("        conn.execute('PRAGMA wal_checkpoint(PASSIVE);')", (52, 211, 153)),
            ("        time.sleep(30)", (226, 232, 240))
        ]

        # Progressive typing of code lines
        lines_to_show = min(len(code_lines), int((f - 114) / 7))
        ly = ry + 24
        for idx in range(lines_to_show):
            txt, col = code_lines[idx]
            if txt:
                draw.text((qx + 24, ly), txt, fill=col, font=font_mono)
            ly += 28

        # Bottom pills
        py = ry + code_box_h + 20
        px = qx
        px += draw_pill(draw, px, py, "OLLAMA LOCAL GPU") + 12
        px += draw_pill(draw, px, py, "OPENROUTER API") + 12
        px += draw_pill(draw, px, py, "TTL MEMORY PRUNING") + 12
        px += draw_pill(draw, px, py, "INJECTION SHIELD ACTIVE", border_col=(16, 185, 129), text_col=(52, 211, 153)) + 12

    # -------------------------------------------------------------
    # ACT 3: Audio Transcoder & Continuous Radio (7.6s - 11.4s / frames 228 - 342)
    # -------------------------------------------------------------
    elif f < 342:
        panel_x, panel_y, panel_w, panel_h = 240, 140, 1440, 760
        draw.rounded_rectangle([panel_x, panel_y, panel_x + panel_w, panel_y + panel_h], radius=10, fill=(10, 13, 20), outline=(30, 41, 59), width=1)
        draw.rectangle([panel_x, panel_y, panel_x + panel_w, panel_y + 46], fill=(15, 20, 30))
        draw.line([panel_x, panel_y + 46, panel_x + panel_w, panel_y + 46], fill=(30, 41, 59), width=1)
        draw.text((panel_x + 24, panel_y + 14), "LOW-LATENCY AUDIO ENGINE // 24/7 CODING RADIO", fill=(148, 163, 184), font=font_badge)
        draw_pill(draw, panel_x + panel_w - 200, panel_y + 9, "LIVE PIPELINE", border_col=(16, 185, 129), text_col=(52, 211, 153))

        cy = panel_y + 80
        cx = panel_x + 36

        # Station Title
        draw.text((cx, cy), "STATION 02 // SYNTHWAVE & CYBERPUNK", fill=(0, 229, 255), font=font_title)
        draw.text((cx, cy + 44), "Hardware-accelerated continuous audio demuxing via FFmpeg 9.0.2 • Voice Gateway Opus Transcoder", fill=(148, 163, 184), font=font_subtitle)

        # Smooth Liquid Oscilloscope Wave
        wave_y = cy + 220
        wave_pts_glow = []
        wave_pts_sharp = []
        wave_pts_ref = []
        
        for wx in range(cx, cx + panel_w - 72, 4):
            # Complex smooth multi-harmonic wave
            prog = (wx - cx) / (panel_w - 72)
            envelope = math.sin(prog * math.pi)  # Zero at edges
            w1 = math.sin(wx * 0.02 + t * 9) * 55
            w2 = math.sin(wx * 0.04 - t * 6) * 25
            w3 = math.sin(wx * 0.08 + t * 12) * 12
            total_y = wave_y + (w1 + w2 + w3) * envelope

            wave_pts_sharp.append((wx, total_y))
            wave_pts_ref.append((wx, wave_y - (w1 + w2) * envelope * 0.4))

        # Draw glowing wave lines
        draw.line(wave_pts_sharp, fill=(0, 229, 255), width=3)
        draw.line(wave_pts_ref, fill=(16, 185, 129, 140), width=1)

        # Telemetry metrics row
        my = panel_y + panel_h - 150
        draw.rounded_rectangle([cx, my, cx + panel_w - 72, my + 95], radius=8, fill=(14, 18, 28), outline=(30, 41, 59), width=1)
        
        col_w = (panel_w - 72) // 4
        # Col 1
        draw.text((cx + 20, my + 20), "BITRATE", fill=(100, 116, 139), font=font_badge)
        draw.text((cx + 20, my + 44), "128 KBPS OPUS", fill=(255, 255, 255), font=font_mono_lg)
        # Col 2
        draw.text((cx + col_w + 20, my + 20), "TRANSCODER", fill=(100, 116, 139), font=font_badge)
        draw.text((cx + col_w + 20, my + 44), "FFMPEG NATIVE", fill=(56, 189, 248), font=font_mono_lg)
        # Col 3
        draw.text((cx + col_w*2 + 20, my + 20), "RECONNECTS", fill=(100, 116, 139), font=font_badge)
        draw.text((cx + col_w*2 + 20, my + 44), "AUTO-HEALING", fill=(52, 211, 153), font=font_mono_lg)
        # Col 4
        draw.text((cx + col_w*3 + 20, my + 20), "SECURITY CHECK", fill=(100, 116, 139), font=font_badge)
        draw.text((cx + col_w*3 + 20, my + 44), "SSRF SHIELD OK", fill=(16, 185, 129), font=font_mono_lg)

    # -------------------------------------------------------------
    # ACT 4: Dynamic Contributor Card & Grand Reveal (11.4s - 16.0s / frames 342 - 480)
    # -------------------------------------------------------------
    else:
        # Spotlight Card Reveal
        if f < 435:
            # Card Zoom & Float animation
            reveal_prog = (f - 342) / (435 - 342)
            scale = 0.92 + 0.08 * math.sin(reveal_prog * math.pi / 2)
            
            cw = int(1000 * scale)
            ch = int(520 * scale)
            cx = (W - cw) // 2
            cy = (H - ch) // 2 - 20

            # Glowing Aura Behind Card
            for rad in range(30, 0, -5):
                alpha = int(40 * (rad / 30))
                draw.rounded_rectangle([cx - rad, cy - rad, cx + cw + rad, cy + ch + rad], radius=24, outline=(0, 229, 255, alpha), width=3)

            # Paste Card
            if card_raw:
                card_scaled = card_raw.resize((cw, ch), Image.Resampling.LANCZOS)
                img.paste(card_scaled, (cx, cy), card_scaled)

            # Top label
            draw.text((W // 2 - 240, cy - 50), "DYNAMIC GLASSMORPHIC CONTRIBUTOR PASSPORT", fill=(0, 229, 255), font=font_badge)
            draw.text((W // 2 - 280, cy + ch + 35), "AUTOMATIC DISCORD AVATAR COMPOSITING • VECTOR TIERS • PILLOW HIGH-DPI", fill=(148, 163, 184), font=font_badge)

        else:
            # Final Grand Outro Lockup
            out_prog = (f - 435) / (480 - 435)
            # Center typography
            draw.text((W // 2 - 130, H // 2 - 120), "❄️ SIRDEEP", fill=(0, 229, 255), font=font_hero)
            draw.text((W // 2 - 380, H // 2 - 40), "THE AUTONOMOUS COMMUNITY ENGINE FOR DEVELOPER GUILDS", fill=(255, 255, 255), font=font_title)
            draw.text((W // 2 - 280, H // 2 + 25), "Self-Hosted • Low-Latency Transcoder • Audit Sentinel • Zero Telemetry", fill=(148, 163, 184), font=font_subtitle)

            # Clean GitHub Pill
            pill_w = 460
            pill_h = 56
            px = (W - pill_w) // 2
            py = H // 2 + 85
            draw.rounded_rectangle([px, py, px + pill_w, py + pill_h], radius=10, fill=(15, 23, 42), outline=(0, 229, 255), width=2)
            draw.text((px + 45, py + 14), "github.com/OpenWinter/sirdeep", fill=(255, 255, 255), font=font_mono_lg)

    return img

print("Initializing Custom High-End Motion Video Render...")

cmd = [
    FFMPEG_EXE,
    "-y",
    "-f", "rawvideo",
    "-vcodec", "rawvideo",
    "-s", f"{W}x{H}",
    "-pix_fmt", "rgb24",
    "-r", str(FPS),
    "-i", "-",
    "-f", "lavfi",
    # Deep cinematic ambient drone with subtle warm filter
    "-i", "aevalsrc=sin(55*2*PI*t)*0.16+sin(82.4*2*PI*t)*0.12+sin(110*2*PI*t)*0.08+sin(220*2*PI*t)*0.03:s=44100:d=16",
    "-af", "lowpass=f=500,volume=1.8",
    "-c:v", "libx264",
    "-pix_fmt", "yuv420p",
    "-preset", "fast",
    "-crf", "16",
    "-c:a", "aac",
    "-b:a", "192k",
    "-shortest",
    OUTPUT_MP4
]

pipe = subprocess.Popen(cmd, stdin=subprocess.PIPE)

for f in range(TOTAL_FRAMES):
    if f % 48 == 0:
        print(f"Rendering frame {f}/{TOTAL_FRAMES} ({(f/TOTAL_FRAMES)*100:.1f}%)...")
    frame = render_frame(f)
    pipe.stdin.write(frame.tobytes())

pipe.stdin.close()
pipe.wait()
print(f"Custom MP4 Video Rendered: {OUTPUT_MP4}")
