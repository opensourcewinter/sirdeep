import os
import sys
import io
from urllib.parse import urlparse
import aiohttp
from PIL import Image, ImageDraw, ImageFont

# Protect against decompression bomb denial-of-service
Image.MAX_IMAGE_PIXELS = 10_000_000
MAX_AVATAR_BYTES = 5 * 1024 * 1024  # 5 MB limit
ALLOWED_CDN_DOMAINS = {"cdn.discordapp.com", "media.discordapp.net"}

def get_font(size: int, bold: bool = False):
    candidates = []
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    bundled_font_dir = os.path.join(base_dir, "assets", "fonts")
    
    if bold:
        candidates.append(os.path.join(bundled_font_dir, "Inter-Bold.ttf"))
    else:
        candidates.append(os.path.join(bundled_font_dir, "Inter-Regular.ttf"))

    if sys.platform == 'win32':
        font_dir = os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Fonts')
        candidates.extend([
            os.path.join(font_dir, 'segoeuib.ttf' if bold else 'segoeui.ttf'),
            os.path.join(font_dir, 'arialbd.ttf' if bold else 'arial.ttf')
        ])
    else:
        candidates.extend([
            '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf' if bold else '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
            '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf' if bold else '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf'
        ])

    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                pass
    return ImageFont.load_default()

def draw_rounded_rect(draw, bbox, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(bbox, radius=radius, fill=fill, outline=outline, width=width)

def clean_tag_text(text: str) -> str:
    for prefix in ["💻 ", "🌐 ", "🧠 ", "🎨 ", "📢 ", "🌱 ", "🛠️ ", "⚡ ", "❄️ ", "💎 "]:
        if text.startswith(prefix):
            text = text[len(prefix):]
    return text.strip()

async def render_contributor_card(member, guild, level=1, xp=0, needed_xp=100, rank_pos=1, rep_points=0, specializations=None):
    W, H = 1000, 520
    card = Image.new("RGBA", (W, H), (11, 15, 23, 255))
    draw = ImageDraw.Draw(card)

    for y in range(H):
        ratio = y / H
        r = int(10 * (1 - ratio) + 15 * ratio)
        g = int(14 * (1 - ratio) + 23 * ratio)
        b = int(26 * (1 - ratio) + 42 * ratio)
        draw.line([(0, y), (W, y)], fill=(r, g, b, 255))

    for rad in range(300, 0, -15):
        alpha = int(22 * (1 - rad / 300))
        draw.ellipse([W - 100 - rad, -50 - rad, W - 100 + rad, -50 + rad], fill=(0, 210, 255, alpha))
        draw.ellipse([-50 - rad, H - 50 - rad, -50 + rad, H - 50 + rad], fill=(56, 189, 248, alpha))

    draw_rounded_rect(draw, [20, 20, W - 20, H - 20], radius=24, fill=(15, 23, 42, 220), outline=(56, 189, 248, 80), width=2)

    font_brand = get_font(16, bold=True)
    font_title = get_font(28, bold=True)
    font_sub = get_font(16, bold=False)
    font_bold = get_font(18, bold=True)
    font_huge = get_font(36, bold=True)
    font_small = get_font(13, bold=False)

    draw.text((50, 42), f"{guild.name.upper()} // OPEN-SOURCE ECOSYSTEM", fill=(0, 210, 255, 240), font=font_brand)
    draw.text((W - 250, 42), f"GLOBAL RANK #{rank_pos}", fill=(148, 163, 184, 220), font=font_brand)
    draw.line([(50, 72), (W - 50, 72)], fill=(56, 189, 248, 40), width=1)

    avatar_size = 140
    avatar_x, avatar_y = 55, 105
    avatar_img = None
    try:
        avatar_url = member.display_avatar.with_format("png").with_size(256).url
        parsed = urlparse(avatar_url)
        # SSRF and Host check
        if parsed.netloc in ALLOWED_CDN_DOMAINS and parsed.scheme in {"http", "https"}:
            async with aiohttp.ClientSession() as session:
                async with session.get(avatar_url, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                    if resp.status == 200:
                        content_length = resp.headers.get("Content-Length")
                        if not content_length or int(content_length) <= MAX_AVATAR_BYTES:
                            data = await resp.read()
                            if len(data) <= MAX_AVATAR_BYTES:
                                avatar_raw = Image.open(io.BytesIO(data)).convert("RGBA")
                                avatar_raw = avatar_raw.resize((avatar_size, avatar_size), Image.Resampling.LANCZOS)
                                mask = Image.new("L", (avatar_size, avatar_size), 0)
                                mask_draw = ImageDraw.Draw(mask)
                                mask_draw.ellipse([0, 0, avatar_size, avatar_size], fill=255)
                                avatar_img = Image.new("RGBA", (avatar_size, avatar_size), (0, 0, 0, 0))
                                avatar_img.paste(avatar_raw, (0, 0), mask)
    except Exception as e:
        print(f"[CARD ERROR] Failed to fetch avatar safely: {e}")

    for ring in range(6, 0, -1):
        draw.ellipse([avatar_x - ring, avatar_y - ring, avatar_x + avatar_size + ring, avatar_y + avatar_size + ring], outline=(0, 210, 255, int(40 * (ring / 6))), width=1)

    if avatar_img:
        card.paste(avatar_img, (avatar_x, avatar_y), avatar_img)
    else:
        draw.ellipse([avatar_x, avatar_y, avatar_x + avatar_size, avatar_y + avatar_size], fill=(30, 41, 59, 255), outline=(0, 210, 255, 200), width=3)

    name_x = 225
    display_name = clean_tag_text(member.display_name)
    if len(display_name) > 20:
        display_name = display_name[:18] + "..."
    draw.text((name_x, 102), display_name, fill=(255, 255, 255, 255), font=font_title)
    draw.text((name_x, 142), f"@{member.name} • Joined {member.joined_at.strftime('%b %Y') if member.joined_at else '2026'}", fill=(148, 163, 184, 220), font=font_sub)

    tier_label = "BUILDER" if level < 5 else ("CORE CONTRIBUTOR" if level < 15 else "SENIOR ARCHITECT")
    badge_bg = (16, 185, 129, 40) if level >= 5 else (56, 189, 248, 30)
    badge_border = (16, 185, 129, 180) if level >= 5 else (56, 189, 248, 140)
    badge_text_color = (52, 211, 153, 255) if level >= 5 else (56, 189, 248, 255)

    draw_rounded_rect(draw, [name_x, 175, name_x + 200, 207], radius=8, fill=badge_bg, outline=badge_border, width=1)
    draw.text((name_x + 22, 182), tier_label, fill=badge_text_color, font=font_brand)

    stat_start_x = 640
    draw_rounded_rect(draw, [stat_start_x, 102, stat_start_x + 95, 195], radius=14, fill=(15, 23, 42, 240), outline=(56, 189, 248, 60), width=1)
    draw.text((stat_start_x + 22, 115), "LEVEL", fill=(148, 163, 184, 220), font=font_small)
    draw.text((stat_start_x + 24, 138), f"{level:02d}", fill=(0, 210, 255, 255), font=font_huge)

    draw_rounded_rect(draw, [stat_start_x + 110, 102, stat_start_x + 205, 195], radius=14, fill=(15, 23, 42, 240), outline=(16, 185, 129, 60), width=1)
    draw.text((stat_start_x + 128, 115), "REP", fill=(148, 163, 184, 220), font=font_small)
    draw.text((stat_start_x + 128, 138), f"{rep_points}", fill=(52, 211, 153, 255), font=font_huge)

    prog_y = 275
    draw.text((55, prog_y - 25), "CONTRIBUTION XP PROGRESSION", fill=(148, 163, 184, 240), font=font_brand)
    xp_label = f"{xp:,} / {needed_xp:,} XP  ({int((xp / max(1, needed_xp)) * 100)}%)"
    draw.text((W - 55 - (len(xp_label) * 9), prog_y - 25), xp_label, fill=(0, 210, 255, 240), font=font_brand)

    bar_x, bar_w, bar_h = 55, W - 110, 20
    draw_rounded_rect(draw, [bar_x, prog_y, bar_x + bar_w, prog_y + bar_h], radius=10, fill=(30, 41, 59, 200), outline=(51, 65, 85, 255), width=1)

    fill_ratio = min(1.0, max(0.02, xp / max(1, needed_xp)))
    filled_w = int(bar_w * fill_ratio)
    if filled_w > 12:
        bar_fill = Image.new("RGBA", (filled_w, bar_h), (0, 0, 0, 0))
        bf_draw = ImageDraw.Draw(bar_fill)
        for fx in range(filled_w):
            frat = fx / max(1, filled_w)
            cr = int(0 * (1 - frat) + 56 * frat)
            cg = int(210 * (1 - frat) + 189 * frat)
            cb = int(255 * (1 - frat) + 248 * frat)
            bf_draw.line([(fx, 0), (fx, bar_h)], fill=(cr, cg, cb, 255))
        bar_mask = Image.new("L", (filled_w, bar_h), 0)
        bm_draw = ImageDraw.Draw(bar_mask)
        draw_rounded_rect(bm_draw, [0, 0, filled_w, bar_h], radius=10, fill=255)
        card.paste(bar_fill, (bar_x, prog_y), bar_mask)

    draw.line([(50, prog_y + 45), (W - 50, prog_y + 45)], fill=(56, 189, 248, 30), width=1)
    draw.text((55, prog_y + 60), "ENGINEERING DOMAINS & FOCUS", fill=(148, 163, 184, 240), font=font_brand)

    tags = specializations if specializations else ["Systems & Low-Level", "Full-Stack & Web", "AI & Machine Learning"]
    tag_x = 55
    tag_y = prog_y + 92
    for raw_t in tags[:4]:
        t = clean_tag_text(raw_t)
        tw = len(t) * 11 + 28
        draw_rounded_rect(draw, [tag_x, tag_y, tag_x + tw, tag_y + 34], radius=8, fill=(30, 41, 59, 180), outline=(56, 189, 248, 80), width=1)
        draw.text((tag_x + 14, tag_y + 8), t, fill=(226, 232, 240, 255), font=font_bold)
        tag_x += tw + 16

    footer_text = f"Verified Contributor Identity • {guild.name} Foundation • Build together. Share freely."
    draw.text((55, H - 45), footer_text, fill=(100, 116, 139, 200), font=font_small)

    buf = io.BytesIO()
    card.save(buf, format="PNG", optimize=True)
    buf.seek(0)
    return buf
