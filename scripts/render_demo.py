import os
import sys
import math
import subprocess
from PIL import Image, ImageDraw, ImageFont

# Dimensions & Parameters
W, H = 1920, 1080
FPS = 30
DURATION = 15  # seconds
TOTAL_FRAMES = FPS * DURATION  # 450 frames

FFMPEG_EXE = r"C:\Users\conta\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.2-full_build\bin\ffmpeg.exe"
OUTPUT_MP4 = r"C:\DEV\SirDeep\assets\branding\demo.mp4"
OUTPUT_GIF = r"C:\DEV\SirDeep\assets\branding\demo.gif"
CARD_IMG_PATH = r"C:\DEV\SirDeep\assets\branding\sample_card.png"
BANNER_PATH = r"C:\DEV\SirDeep\assets\branding\banner.jpg"

# Fonts
FONT_DIR = r"C:\Windows\Fonts"
font_title = ImageFont.truetype(os.path.join(FONT_DIR, "segoeuib.ttf"), 38)
font_large = ImageFont.truetype(os.path.join(FONT_DIR, "segoeuib.ttf"), 30)
font_heading = ImageFont.truetype(os.path.join(FONT_DIR, "segoeuib.ttf"), 24)
font_body = ImageFont.truetype(os.path.join(FONT_DIR, "segoeui.ttf"), 20)
font_body_bold = ImageFont.truetype(os.path.join(FONT_DIR, "segoeuib.ttf"), 20)
font_small = ImageFont.truetype(os.path.join(FONT_DIR, "segoeui.ttf"), 16)
font_mono = ImageFont.truetype(os.path.join(FONT_DIR, "consola.ttf"), 20)
font_mono_bold = ImageFont.truetype(os.path.join(FONT_DIR, "consolab.ttf"), 22)
font_tag = ImageFont.truetype(os.path.join(FONT_DIR, "segoeuib.ttf"), 13)

# Load existing assets
card_img_raw = Image.open(CARD_IMG_PATH).convert("RGBA") if os.path.exists(CARD_IMG_PATH) else None
banner_img_raw = Image.open(BANNER_PATH).convert("RGB") if os.path.exists(BANNER_PATH) else None

def draw_rounded_rect(draw, box, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)

def render_frame(frame_idx: int) -> Image.Image:
    t = frame_idx / FPS
    img = Image.new("RGB", (W, H), (11, 15, 23))
    draw = ImageDraw.Draw(img)

    # -------------------------------------------------------------
    # SCENE 1: Terminal Boot & Startup (0s - 3.2s / frames 0 - 95)
    # -------------------------------------------------------------
    if frame_idx < 95:
        # Subtle dark ambient background
        draw.rectangle([0, 0, W, H], fill=(11, 15, 23))
        # Top banner glow
        for r in range(100):
            alpha = int(25 * (1 - r / 100))
            draw.ellipse([W//2 - 500 - r, -200 - r, W//2 + 500 + r, 200 + r], outline=(0, 210, 255, alpha))

        # Terminal Window
        tw_x, tw_y, tw_w, tw_h = 260, 140, 1400, 800
        draw_rounded_rect(draw, [tw_x, tw_y, tw_x + tw_w, tw_y + tw_h], radius=16, fill=(15, 23, 42), outline=(56, 189, 248, 120), width=2)
        # Window Header
        draw.rectangle([tw_x, tw_y, tw_x + tw_w, tw_y + 44], fill=(30, 41, 59))
        draw_rounded_rect(draw, [tw_x, tw_y, tw_x + tw_w, tw_y + 44], radius=16, fill=(30, 41, 59))
        draw.rectangle([tw_x, tw_y + 24, tw_x + tw_w, tw_y + 44], fill=(30, 41, 59))
        
        # Window Controls
        draw.ellipse([tw_x + 18, tw_y + 14, tw_x + 32, tw_y + 28], fill=(239, 68, 68))
        draw.ellipse([tw_x + 38, tw_y + 14, tw_x + 52, tw_y + 28], fill=(245, 158, 11))
        draw.ellipse([tw_x + 58, tw_y + 14, tw_x + 72, tw_y + 28], fill=(16, 185, 129))
        draw.text((tw_x + tw_w // 2 - 120, tw_y + 12), "openwinter@production: ~/sirdeep", fill=(148, 163, 184), font=font_small)

        # Terminal Content
        cy = tw_y + 70
        cx = tw_x + 40

        # Typing command simulation
        full_cmd = "docker compose up -d --build"
        char_count = min(len(full_cmd), int(frame_idx * 0.9))
        draw.text((cx, cy), "$ " + full_cmd[:char_count] + ("_" if (frame_idx // 8) % 2 == 0 else ""), fill=(0, 210, 255), font=font_mono_bold)

        if frame_idx > 35:
            cy += 45
            draw.text((cx, cy), "[+] Building 0.4s (12/12) FINISHED", fill=(148, 163, 184), font=font_mono)
            cy += 30
            draw.text((cx, cy), " ✔ Network sirdeep_default    Created", fill=(52, 211, 153), font=font_mono)
            cy += 30
            draw.text((cx, cy), " ✔ Container sirdeep          Started [HEALTHY]", fill=(52, 211, 153), font=font_mono)

        if frame_idx > 55:
            cy += 45
            draw.text((cx, cy), "=========================================================", fill=(56, 189, 248), font=font_mono)
            cy += 30
            draw.text((cx, cy), " ⚡ SIRDEEP COMMUNITY ENGINE v1.0.0 ONLINE", fill=(0, 210, 255), font=font_mono_bold)
            cy += 30
            draw.text((cx, cy), " [INFO] Gateway: Connected to Discord WebSocket Gateway v10", fill=(255, 255, 255), font=font_mono)
            cy += 30
            draw.text((cx, cy), " [INFO] Subsystems active: AuditSentinel, RadioPlayer, AIEngine, Leveling", fill=(226, 232, 240), font=font_mono)
            cy += 30
            draw.text((cx, cy), " [READY] Logged in as SirDeep#1316 (Guild: OpenWinter)", fill=(16, 185, 129), font=font_mono_bold)
            cy += 30
            draw.text((cx, cy), "=========================================================", fill=(56, 189, 248), font=font_mono)

    # -------------------------------------------------------------
    # SCENES 2, 3, 4: Discord App Interface (frames 95 - 410)
    # -------------------------------------------------------------
    elif frame_idx < 410:
        # Discord Full Window Frame
        app_x, app_y, app_w, app_h = 140, 80, 1640, 920
        draw_rounded_rect(draw, [app_x, app_y, app_x + app_w, app_y + app_h], radius=14, fill=(49, 51, 56), outline=(43, 45, 49), width=2)

        # Discord Server Rail (Far left)
        rail_w = 72
        draw.rectangle([app_x, app_y, app_x + rail_w, app_y + app_h], fill=(30, 31, 34))
        # OpenWinter Guild Icon
        draw_rounded_rect(draw, [app_x + 12, app_y + 20, app_x + 60, app_y + 68], radius=16, fill=(15, 23, 42), outline=(0, 210, 255), width=2)
        draw.text((app_x + 23, app_y + 28), "❄️", font=font_heading)

        # Discord Channel Sidebar
        side_w = 240
        side_x = app_x + rail_w
        draw.rectangle([side_x, app_y, side_x + side_w, app_y + app_h], fill=(43, 45, 49))
        
        # Guild Name Header
        draw.text((side_x + 16, app_y + 18), "OpenWinter", fill=(255, 255, 255), font=font_large)
        draw.line([side_x, app_y + 56, side_x + side_w, app_y + 56], fill=(30, 31, 34), width=1)

        # Channel Categories & Channels
        cy = app_y + 75
        draw.text((side_x + 16, cy), "▼ INFORMATION", fill=(148, 163, 184), font=font_tag)
        cy += 28
        draw.text((side_x + 24, cy), "#  welcome", fill=(148, 155, 164), font=font_body)
        cy += 40
        draw.text((side_x + 16, cy), "▼ TEXT CHANNELS", fill=(148, 163, 184), font=font_tag)
        cy += 28
        # #general (active)
        draw_rounded_rect(draw, [side_x + 8, cy - 6, side_x + side_w - 8, cy + 30], radius=6, fill=(53, 55, 60))
        draw.text((side_x + 24, cy), "#  general", fill=(255, 255, 255), font=font_body_bold)
        cy += 38
        draw.text((side_x + 24, cy), "#  tech-debates", fill=(148, 155, 164), font=font_body)
        cy += 38
        draw.text((side_x + 24, cy), "🔒  audit-logs", fill=(148, 155, 164), font=font_body)

        cy += 45
        draw.text((side_x + 16, cy), "▼ VOICE CHANNELS", fill=(148, 163, 184), font=font_tag)
        cy += 28
        is_voice_active = frame_idx >= 210
        if is_voice_active:
            draw_rounded_rect(draw, [side_x + 8, cy - 6, side_x + side_w - 8, cy + 30], radius=6, fill=(46, 75, 60))
            draw.text((side_x + 24, cy), "🔊  24/7 Coding Radio", fill=(52, 211, 153), font=font_body_bold)
            cy += 38
            # Voice users connected
            draw.ellipse([side_x + 36, cy + 2, side_x + 52, cy + 18], fill=(16, 185, 129))
            draw.text((side_x + 58, cy), "SirDeep [BOT]", fill=(52, 211, 153), font=font_small)
            cy += 26
            draw.ellipse([side_x + 36, cy + 2, side_x + 52, cy + 18], fill=(90, 100, 110))
            draw.text((side_x + 58, cy), "harshit", fill=(200, 210, 220), font=font_small)
        else:
            draw.text((side_x + 24, cy), "🔊  24/7 Coding Radio", fill=(148, 155, 164), font=font_body)

        # Discord Chat Header
        chat_x = side_x + side_w
        chat_w = app_w - rail_w - side_w
        draw.rectangle([chat_x, app_y, app_x + app_w, app_y + 56], fill=(49, 51, 56))
        draw.line([chat_x, app_y + 56, app_x + app_w, app_y + 56], fill=(40, 42, 46), width=1)
        draw.text((chat_x + 20, app_y + 16), "#  general", fill=(255, 255, 255), font=font_large)
        draw.text((chat_x + 170, app_y + 22), "|  OpenWinter Engineering Discussions & AI Pair Programming", fill=(148, 155, 164), font=font_small)

        # Chat Area Content
        chat_y = app_y + 75
        
        # -------------------------------------------------------------
        # SCENE 2 (frames 95 - 210): AI Interaction
        # -------------------------------------------------------------
        if frame_idx < 210:
            # User Message
            draw.ellipse([chat_x + 24, chat_y, chat_x + 72, chat_y + 48], fill=(99, 102, 241))
            draw.text((chat_x + 38, chat_y + 10), "H", fill=(255, 255, 255), font=font_large)
            draw.text((chat_x + 88, chat_y + 2), "harshit", fill=(255, 255, 255), font=font_body_bold)
            draw.text((chat_x + 165, chat_y + 6), "Today at 11:45 PM", fill=(148, 155, 164), font=font_small)
            draw.text((chat_x + 88, chat_y + 30), "@SirDeep explain SQLite WAL mode concurrency in 2 lines", fill=(220, 225, 235), font=font_body)

            # Typing indicator (frames 115 - 145)
            if 115 <= frame_idx < 145:
                ty = chat_y + 85
                draw.text((chat_x + 88, ty), "⚡ SirDeep is typing", fill=(0, 210, 255), font=font_body)
                dots = "." * ((frame_idx // 6) % 4)
                draw.text((chat_x + 260, ty), dots, fill=(0, 210, 255), font=font_large)

            # Bot Reply (frames 145+)
            if frame_idx >= 145:
                by = chat_y + 90
                # Bot Avatar
                draw_rounded_rect(draw, [chat_x + 24, by, chat_x + 72, by + 48], radius=24, fill=(15, 23, 42), outline=(0, 210, 255), width=2)
                draw.text((chat_x + 36, by + 10), "⚡", fill=(0, 210, 255), font=font_large)
                draw.text((chat_x + 88, by + 2), "SirDeep", fill=(0, 210, 255), font=font_body_bold)
                draw_rounded_rect(draw, [chat_x + 180, by + 4, chat_x + 225, by + 22], radius=4, fill=(88, 101, 242))
                draw.text((chat_x + 186, by + 5), "BOT", fill=(255, 255, 255), font=font_tag)
                draw.text((chat_x + 240, by + 6), "Today at 11:45 PM", fill=(148, 155, 164), font=font_small)

                draw.text((chat_x + 88, by + 32), "Write-Ahead Logging (WAL) writes changes to a separate -wal file before committing,", fill=(230, 235, 245), font=font_body)
                draw.text((chat_x + 88, by + 60), "enabling concurrent readers and writers without lock contention:", fill=(230, 235, 245), font=font_body)

                # Code block
                draw_rounded_rect(draw, [chat_x + 88, by + 95, chat_x + 650, by + 155], radius=8, fill=(30, 31, 34), outline=(43, 45, 49), width=1)
                draw.text((chat_x + 108, by + 115), "conn.execute(\"PRAGMA journal_mode=WAL;\")", fill=(56, 189, 248), font=font_mono_bold)

        # -------------------------------------------------------------
        # SCENE 3 (frames 210 - 320): 24/7 Coding Radio Stream
        # -------------------------------------------------------------
        elif frame_idx < 320:
            # User command
            draw.ellipse([chat_x + 24, chat_y, chat_x + 72, chat_y + 48], fill=(99, 102, 241))
            draw.text((chat_x + 38, chat_y + 10), "H", fill=(255, 255, 255), font=font_large)
            draw.text((chat_x + 88, chat_y + 2), "harshit", fill=(255, 255, 255), font=font_body_bold)
            draw.text((chat_x + 165, chat_y + 6), "Today at 11:46 PM", fill=(148, 155, 164), font=font_small)
            draw.text((chat_x + 88, chat_y + 30), "/radio station station:synthwave", fill=(56, 189, 248), font=font_body_bold)

            # Bot Radio Embed Response
            by = chat_y + 80
            draw_rounded_rect(draw, [chat_x + 24, by, chat_x + 72, by + 48], radius=24, fill=(15, 23, 42), outline=(0, 210, 255), width=2)
            draw.text((chat_x + 36, by + 10), "⚡", fill=(0, 210, 255), font=font_large)
            draw.text((chat_x + 88, by + 2), "SirDeep", fill=(0, 210, 255), font=font_body_bold)
            draw_rounded_rect(draw, [chat_x + 180, by + 4, chat_x + 225, by + 22], radius=4, fill=(88, 101, 242))
            draw.text((chat_x + 186, by + 5), "BOT", fill=(255, 255, 255), font=font_tag)

            # Discord Rich Embed Box
            embed_y = by + 35
            embed_w = 780
            embed_h = 240
            draw_rounded_rect(draw, [chat_x + 88, embed_y, chat_x + 88 + embed_w, embed_y + embed_h], radius=10, fill=(35, 37, 42), outline=(50, 52, 58), width=1)
            # Left neon cyan color bar
            draw_rounded_rect(draw, [chat_x + 88, embed_y, chat_x + 94, embed_y + embed_h], radius=4, fill=(0, 210, 255))

            draw.text((chat_x + 110, embed_y + 16), "📻 24/7 CODING RADIO • OPENWINTER SOUNDSCAPES", fill=(148, 163, 184), font=font_tag)
            draw.text((chat_x + 110, embed_y + 38), "🌆 Station Active: Synthwave & Cyberpunk", fill=(0, 210, 255), font=font_large)
            draw.text((chat_x + 110, embed_y + 80), "Connected to: 🔊 24/7 Coding Radio | Transcoder: FFmpeg 9.0.2 (128kbps stereo)", fill=(220, 225, 235), font=font_body)

            # Animated Audio Equalizer Bars
            eq_y = embed_y + 150
            draw.text((chat_x + 110, eq_y - 28), "LIVE AUDIO STREAM EQUALIZER", fill=(16, 185, 129), font=font_tag)
            num_bars = 28
            for b in range(num_bars):
                bx = chat_x + 110 + b * 22
                # Sine wave dancing bars
                bar_h = 10 + int(35 * abs(math.sin(t * 8 + b * 0.4)))
                draw_rounded_rect(draw, [bx, eq_y + 40 - bar_h, bx + 12, eq_y + 40], radius=3, fill=(0, 210, 255))

        # -------------------------------------------------------------
        # SCENE 4 (frames 320 - 410): Contributor Rank Card Generation
        # -------------------------------------------------------------
        else:
            # User command
            draw.ellipse([chat_x + 24, chat_y, chat_x + 72, chat_y + 48], fill=(99, 102, 241))
            draw.text((chat_x + 38, chat_y + 10), "H", fill=(255, 255, 255), font=font_large)
            draw.text((chat_x + 88, chat_y + 2), "harshit", fill=(255, 255, 255), font=font_body_bold)
            draw.text((chat_x + 165, chat_y + 6), "Today at 11:47 PM", fill=(148, 155, 164), font=font_small)
            draw.text((chat_x + 88, chat_y + 30), "/rank", fill=(56, 189, 248), font=font_body_bold)

            by = chat_y + 75
            draw_rounded_rect(draw, [chat_x + 24, by, chat_x + 72, by + 48], radius=24, fill=(15, 23, 42), outline=(0, 210, 255), width=2)
            draw.text((chat_x + 36, by + 10), "⚡", fill=(0, 210, 255), font=font_large)
            draw.text((chat_x + 88, by + 2), "SirDeep", fill=(0, 210, 255), font=font_body_bold)
            draw_rounded_rect(draw, [chat_x + 180, by + 4, chat_x + 225, by + 22], radius=4, fill=(88, 101, 242))
            draw.text((chat_x + 186, by + 5), "BOT", fill=(255, 255, 255), font=font_tag)
            draw.text((chat_x + 88, by + 30), "Generated OpenWinter Contributor Passport for @harshit:", fill=(220, 225, 235), font=font_body)

            # Paste and zoom the real sample card!
            if card_img_raw:
                card_w, card_h = 820, 426
                card_resized = card_img_raw.resize((card_w, card_h), Image.Resampling.LANCZOS)
                cx = chat_x + 88
                cy = by + 65
                # Outer glowing shadow
                draw_rounded_rect(draw, [cx - 6, cy - 6, cx + card_w + 6, cy + card_h + 6], radius=20, fill=(11, 15, 23), outline=(0, 210, 255, 180), width=3)
                img.paste(card_resized, (cx, cy), card_resized)

    # -------------------------------------------------------------
    # SCENE 5 (frames 410 - 450 / 13.7s - 15.0s): Epic Cinematic Outro
    # -------------------------------------------------------------
    else:
        # Dark cinematic fade with cyan & emerald glow
        draw.rectangle([0, 0, W, H], fill=(11, 15, 23))
        
        # Center radial pulse
        pulse = abs(math.sin(t * 3))
        for r in range(120, 0, -10):
            alpha = int(40 * (r / 120) * (0.8 + 0.2 * pulse))
            draw.ellipse([W//2 - r*5, H//2 - r*3, W//2 + r*5, H//2 + r*3], outline=(0, 210, 255, alpha), width=3)

        draw.text((W // 2 - 160, H // 2 - 140), "⚡ SirDeep", fill=(0, 210, 255), font=font_title)
        draw.text((W // 2 - 380, H // 2 - 60), "The Autonomous Community Engine for Developer Guilds", fill=(255, 255, 255), font=font_large)
        draw.text((W // 2 - 270, H // 2 + 10), "Self-Hosted • Low Latency • Zero-Trust Security • AI Ready", fill=(148, 163, 184), font=font_heading)

        # Button pill
        draw_rounded_rect(draw, [W // 2 - 260, H // 2 + 80, W // 2 + 260, H // 2 + 140], radius=16, fill=(16, 185, 129), outline=(52, 211, 153), width=2)
        draw.text((W // 2 - 210, H // 2 + 96), "github.com/OpenWinter/sirdeep", fill=(11, 15, 23), font=font_large)

    return img

print("Initializing video rendering pipeline...")
# Open FFmpeg subprocess with rawvideo stdin pipe
cmd = [
    FFMPEG_EXE,
    "-y",
    "-f", "rawvideo",
    "-vcodec", "rawvideo",
    "-s", f"{W}x{H}",
    "-pix_fmt", "rgb24",
    "-r", str(FPS),
    "-i", "-", # Stdin pipe
    "-f", "lavfi",
    "-i", "aevalsrc=sin(220*2*PI*t)*0.08+sin(330*2*PI*t)*0.06+sin(440*2*PI*t)*0.04:s=44100:d=15", # Ambient synth chord
    "-c:v", "libx264",
    "-pix_fmt", "yuv420p",
    "-preset", "fast",
    "-crf", "18",
    "-c:a", "aac",
    "-b:a", "192k",
    "-shortest",
    OUTPUT_MP4
]

pipe = subprocess.Popen(cmd, stdin=subprocess.PIPE)

for f in range(TOTAL_FRAMES):
    if f % 45 == 0:
        print(f"Rendering frame {f}/{TOTAL_FRAMES} ({(f/TOTAL_FRAMES)*100:.1f}%)...")
    frame = render_frame(f)
    pipe.stdin.write(frame.tobytes())

pipe.stdin.close()
pipe.wait()
print(f"Video MP4 rendered successfully: {OUTPUT_MP4}")

# Also generate high-quality GIF preview for GitHub README
print("Generating optimized animated GIF for GitHub README...")
gif_cmd = [
    FFMPEG_EXE,
    "-y",
    "-i", OUTPUT_MP4,
    "-vf", "fps=12,scale=800:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse",
    "-t", "15",
    OUTPUT_GIF
]
subprocess.run(gif_cmd, check=True)
print(f"GIF preview rendered successfully: {OUTPUT_GIF}")
