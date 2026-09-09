import math
import io
import urllib.request
import streamlit as st
from PIL import Image, ImageDraw, ImageFont

# ── 1. PAGE & UI CONFIGURATION ────────────────────────────────────────────
st.set_page_config(
    page_title="Official Stamp Creation- Tariq Sb",
    page_icon="🏷️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 2rem;
        }
        h1 {
            color: #1a3d8f;
            font-weight: 700;
        }
        .stDownloadButton button {
            width: 100%;
            background-color: #1a3d8f;
            color: white;
            border-radius: 8px;
            height: 3.2em;
            font-weight: bold;
            font-size: 16px;
        }
        .stDownloadButton button:hover {
            background-color: #122b66;
            color: white;
        }
    </style>
""", unsafe_allow_html=True)

# ── 2. FONTS ENGINE (DIRECT GOOGLE STATIC CDN LINKS) ───────────────────────
FONT_URLS = {
    "Bold Heavy (Anton)": "https://fonts.gstatic.com/s/anton/v25/1Ptg8zYS_SKggPN-C0IS.ttf",
    "Clean Modern (Montserrat)": "https://fonts.gstatic.com/s/montserrat/v25/JTUHjIg1_i6t8kCHKm453WzA.ttf",
    "Formal Classic (Playfair)": "https://fonts.gstatic.com/s/playfairdisplay/v30/nuFvD-vYSZviVYUb_RJ3ijvrye4-TYja.ttf",
    "Compact Narrow (Oswald)": "https://fonts.gstatic.com/s/oswald/v49/TK3iWkUHHAIjg752GT8G.ttf"
}

@st.cache_data(show_spinner=False)
def fetch_font_bytes(url):
    try:
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.read()
    except Exception:
        return None

def get_font(size, font_style):
    url = FONT_URLS.get(font_style)
    if url:
        font_bytes = fetch_font_bytes(url)
        if font_bytes:
            try:
                return ImageFont.truetype(io.BytesIO(font_bytes), size)
            except Exception:
                pass

    # System local fallbacks if offline
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
        "arialbd.ttf"
    ]
    for path in font_paths:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue

    try:
        return ImageFont.load_default(size=size)
    except Exception:
        return ImageFont.load_default()

def hex_to_rgb(hex_color):
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

# ── 3. BORDER STYLES DRAWING HELPERS ──────────────────────────────────────
def draw_ellipse_border(draw, bbox, color, style, width=16):
    x0, y0, x1, y1 = bbox
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    rx, ry = (x1 - x0) / 2, (y1 - y0) / 2

    if style == "Solid":
        draw.ellipse(bbox, outline=color, width=width)
    elif style == "Double Line":
        draw.ellipse(bbox, outline=color, width=int(width * 0.7))
        draw.ellipse([x0 + width + 6, y0 + width + 6, x1 - width - 6, y1 - width - 6], outline=color, width=max(int(width * 0.3), 2))
    elif style in ["Dashed", "Dotted"]:
        num_segments = 90 if style == "Dashed" else 140
        dash_ratio = 0.6 if style == "Dashed" else 0.25
        dot_r = max(width // 2, 2)

        for i in range(num_segments):
            a_start = 2 * math.pi * (i / num_segments)
            a_end = a_start + 2 * math.pi * (dash_ratio / num_segments)
            
            if style == "Dashed":
                steps = 6
                for s in range(steps):
                    t1 = a_start + (a_end - a_start) * (s / steps)
                    t2 = a_start + (a_end - a_start) * ((s + 1) / steps)
                    draw.line([
                        cx + rx * math.cos(t1), cy + ry * math.sin(t1),
                        cx + rx * math.cos(t2), cy + ry * math.sin(t2)
                    ], fill=color, width=width)
            else:
                px = cx + rx * math.cos(a_start)
                py = cy + ry * math.sin(a_start)
                draw.ellipse([px - dot_r, py - dot_r, px + dot_r, py + dot_r], fill=color)

def draw_rect_border(draw, bbox, color, style, width=16, radius=0):
    if style == "Solid":
        if radius > 0:
            draw.rounded_rectangle(bbox, radius=radius, outline=color, width=width)
        else:
            draw.rectangle(bbox, outline=color, width=width)
    elif style == "Double Line":
        x0, y0, x1, y1 = bbox
        if radius > 0:
            draw.rounded_rectangle(bbox, radius=radius, outline=color, width=int(width * 0.7))
            draw.rounded_rectangle([x0+width+6, y0+width+6, x1-width-6, y1-width-6], radius=max(radius-width, 4), outline=color, width=max(int(width * 0.3), 2))
        else:
            draw.rectangle(bbox, outline=color, width=int(width * 0.7))
            draw.rectangle([x0+width+6, y0+width+6, x1-width-6, y1-width-6], outline=color, width=max(int(width * 0.3), 2))
    elif style in ["Dashed", "Dotted"]:
        x0, y0, x1, y1 = bbox
        pts = []
        steps_h, steps_v = 40, 25
        for i in range(steps_h): pts.append((x0 + (x1-x0)*(i/steps_h), y0))
        for i in range(steps_v): pts.append((x1, y0 + (y1-y0)*(i/steps_v)))
        for i in range(steps_h): pts.append((x1 - (x1-x0)*(i/steps_h), y1))
        for i in range(steps_v): pts.append((x0, y1 - (y1-y0)*(i/steps_v)))

        step = 2 if style == "Dashed" else 3
        dot_r = max(width // 2, 2)
        for i in range(0, len(pts), step):
            p = pts[i]
            if style == "Dashed" and i + 1 < len(pts):
                p2 = pts[i+1]
                draw.line([p[0], p[1], p2[0], p2[1]], fill=color, width=width)
            else:
                draw.ellipse([p[0]-dot_r, p[1]-dot_r, p[0]+dot_r, p[1]+dot_r], fill=color)

# ── 4. CURVED TEXT RENDERERS ──────────────────────────────────────────────
def curved_text_circle(img, text, cx, cy, radius, start_deg, color, font, spacing=1.05, flip=False):
    if not text.strip():
        return
    chars = list(text.upper())
    widths = []
    for ch in chars:
        try:
            bb = font.getbbox(ch)
            widths.append(max((bb[2] - bb[0]) * spacing, 10))
        except Exception:
            widths.append(20 * spacing)

    total_rad = sum(widths) / radius
    start_rad = math.radians(start_deg)

    if flip:
        cur = start_rad + total_rad / 2
        for ch, cw in zip(chars, widths):
            cur -= cw / radius
            mid = cur + (cw / 2) / radius
            x = cx + radius * math.cos(mid)
            y = cy + radius * math.sin(mid)
            rot = math.degrees(mid) - 90
            sz = int(cw) + 80
            ch_im = Image.new("RGBA", (sz, sz), (0, 0, 0, 0))
            ImageDraw.Draw(ch_im).text((sz//2, sz//2), ch, font=font, fill=color+(255,), anchor="mm")
            ch_im = ch_im.rotate(-rot, expand=True, resample=Image.BICUBIC)
            pw, ph = ch_im.size
            img.paste(ch_im, (int(x - pw/2), int(y - ph/2)), ch_im)
    else:
        cur = start_rad - total_rad / 2
        for ch, cw in zip(chars, widths):
            mid = cur + (cw / 2) / radius
            x = cx + radius * math.cos(mid)
            y = cy + radius * math.sin(mid)
            rot = math.degrees(mid) + 90
            sz = int(cw) + 80
            ch_im = Image.new("RGBA", (sz, sz), (0, 0, 0, 0))
            ImageDraw.Draw(ch_im).text((sz//2, sz//2), ch, font=font, fill=color+(255,), anchor="mm")
            ch_im = ch_im.rotate(-rot, expand=True, resample=Image.BICUBIC)
            pw, ph = ch_im.size
            img.paste(ch_im, (int(x - pw/2), int(y - ph/2)), ch_im)
            cur += cw / radius

def curved_text_oval(img, text, cx, cy, rx, ry, start_deg, color, font, spacing=1.05, flip=False):
    if not text.strip():
        return
    chars = list(text.upper())
    widths = []
    for ch in chars:
        try:
            bb = font.getbbox(ch)
            widths.append(max((bb[2] - bb[0]) * spacing, 10))
        except Exception:
            widths.append(20 * spacing)

    r_avg = (rx + ry) / 2
    total_rad = sum(widths) / r_avg
    start_rad = math.radians(start_deg)

    if flip:
        cur = start_rad + total_rad / 2
        for ch, cw in zip(chars, widths):
            cur -= cw / r_avg
            mid = cur + (cw / 2) / r_avg
            x = cx + rx * math.cos(mid)
            y = cy + ry * math.sin(mid)
            dx = -rx * math.sin(mid)
            dy =  ry * math.cos(mid)
            rot = math.degrees(math.atan2(dy, dx)) - 180

            sz = int(cw) + 80
            ch_im = Image.new("RGBA", (sz, sz), (0, 0, 0, 0))
            ImageDraw.Draw(ch_im).text((sz//2, sz//2), ch, font=font, fill=color+(255,), anchor="mm")
            ch_im = ch_im.rotate(-rot, expand=True, resample=Image.BICUBIC)
            pw, ph = ch_im.size
            img.paste(ch_im, (int(x - pw/2), int(y - ph/2)), ch_im)
    else:
        cur = start_rad - total_rad / 2
        for ch, cw in zip(chars, widths):
            mid = cur + (cw / 2) / r_avg
            x = cx + rx * math.cos(mid)
            y = cy + ry * math.sin(mid)
            dx = -rx * math.sin(mid)
            dy =  ry * math.cos(mid)
            rot = math.degrees(math.atan2(dy, dx))

            sz = int(cw) + 80
            ch_im = Image.new("RGBA", (sz, sz), (0, 0, 0, 0))
            ImageDraw.Draw(ch_im).text((sz//2, sz//2), ch, font=font, fill=color+(255,), anchor="mm")
            ch_im = ch_im.rotate(-rot, expand=True, resample=Image.BICUBIC)
            pw, ph = ch_im.size
            img.paste(ch_im, (int(x - pw/2), int(y - ph/2)), ch_im)
            cur += cw / r_avg

# ── 5. ICONS & LOGO ENGINE ────────────────────────────────────────────────
def get_icon_radius(canvas_dim, icon_scale_mode):
    scale_map = {"Small": 0.14, "Medium": 0.20, "Best Fit": 0.25, "Large": 0.32}
    return int(canvas_dim * scale_map.get(icon_scale_mode, 0.25))

def draw_builtin_icon(draw, cx, cy, size, color, icon_name):
    c = color + (220,)
    s = size
    if icon_name == "building":
        draw.rectangle([cx-s, cy-s//4, cx+s, cy+s//2], outline=c, width=4)
        draw.polygon([cx-s, cy-s//4, cx, cy-s, cx+s, cy-s//4], outline=c, width=4)
        ws = s // 3
        for col in [-1, 1]:
            wx = cx + col*(s//2) - ws//2
            draw.rectangle([wx, cy-s//5, wx+ws, cy+s//8], outline=c, width=2)
        draw.rectangle([cx-ws//2, cy+s//8, cx+ws//2, cy+s//2], outline=c, width=2)
    elif icon_name == "star":
        pts = [(cx + (s if i%2==0 else s//2)*math.cos(math.radians(i*36-90)), cy + (s if i%2==0 else s//2)*math.sin(math.radians(i*36-90))) for i in range(10)]
        draw.polygon(pts, outline=c, width=4)
    elif icon_name == "shield":
        draw.polygon([cx-s, cy-s, cx+s, cy-s, cx+s, cy+s//3, cx, cy+s, cx-s, cy+s//3], outline=c, width=4)
        draw.line([cx, cy-s+8, cx, cy+s-20], fill=c, width=3)
        draw.line([cx-s+8, cy-s//4, cx+s-8, cy-s//4], fill=c, width=3)
    elif icon_name == "gear":
        for i in range(8):
            a1, a2 = math.radians(i*45), math.radians(i*45 + 16)
            draw.polygon([cx+s*math.cos(a1), cy+s*math.sin(a1), cx+(s+20)*math.cos(a1), cy+(s+20)*math.sin(a1), cx+(s+20)*math.cos(a2), cy+(s+20)*math.sin(a2), cx+s*math.cos(a2), cy+s*math.sin(a2)], outline=c, width=2)
        draw.ellipse([cx-s, cy-s, cx+s, cy+s], outline=c, width=4)
    elif icon_name == "globe":
        draw.ellipse([cx-s, cy-s, cx+s, cy+s], outline=c, width=4)
        draw.ellipse([cx-s//2, cy-s, cx+s//2, cy+s], outline=c, width=2)
        draw.line([cx-s, cy, cx+s, cy], fill=c, width=2)
    elif icon_name == "crown":
        draw.polygon([cx-s, cy+s//2, cx-s, cy-s//2, cx-s//2, cy, cx, cy-s, cx+s//2, cy, cx+s, cy-s//2, cx+s, cy+s//2], outline=c, width=4)

def paste_custom_logo(base_img, uploaded_file, cx, cy, max_size, target_color):
    try:
        uploaded_file.seek(0)
        logo = Image.open(uploaded_file).convert("RGBA")
        aspect = logo.width / logo.height
        new_w, new_h = (max_size * 2, max(int(max_size * 2 / aspect), 1)) if aspect > 1 else (max(int(max_size * 2 * aspect), 1), max_size * 2)
        logo = logo.resize((new_w, new_h), Image.BICUBIC)

        extrema = logo.getextrema()
        has_transparency = (len(extrema) == 4 and extrema[3][0] < 255)

        if has_transparency:
            r, g, b, alpha = logo.split()
            color_img = Image.new("RGBA", logo.size, target_color + (255,))
            gray = logo.convert("L")
            mask = Image.eval(gray, lambda p: 255 - p)
            color_img.putalpha(Image.composite(mask, alpha, alpha))
            logo_to_paste = color_img
        else:
            gray = logo.convert("L")
            alpha_mask = Image.eval(gray, lambda p: 255 - p if p > 30 else 255)
            color_img = Image.new("RGBA", logo.size, target_color + (255,))
            color_img.putalpha(alpha_mask)
            logo_to_paste = color_img

        lw, lh = logo_to_paste.size
        base_img.paste(logo_to_paste, (cx - lw // 2, cy - lh // 2), logo_to_paste)
    except Exception:
        pass

# ── 6. MAIN STAMP BUILDER ─────────────────────────────────────────────────
def generate_stamp(company, address, fs_top, fs_bot, font_style, text_hex, shape_hex, shape, border_style, icon_source, icon_name, uploaded_file, icon_scale_mode):
    text_color = hex_to_rgb(text_hex)
    shape_color = hex_to_rgb(shape_hex)
    font_top = get_font(fs_top, font_style)
    font_bot = get_font(fs_bot, font_style)

    if shape in ["double_round", "round"]:
        S = 1200
        img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        cx = cy = S // 2
        r_outer = S // 2 - 50
        r_inner = r_outer - 110

        if shape == "double_round":
            r_mid = r_outer - 110
            r_inner = r_mid - 40
            draw_ellipse_border(draw, [cx-r_outer, cy-r_outer, cx+r_outer, cy+r_outer], shape_color, border_style, width=18)
            draw.ellipse([cx-r_mid, cy-r_mid, cx+r_mid, cy+r_mid], outline=shape_color, width=4)
            draw.ellipse([cx-r_inner, cy-r_inner, cx+r_inner, cy+r_inner], outline=shape_color, width=3)
            r_text = (r_outer + r_mid) / 2
        else:
            draw_ellipse_border(draw, [cx-r_outer, cy-r_outer, cx+r_outer, cy+r_outer], shape_color, border_style, width=18)
            draw.ellipse([cx-r_inner, cy-r_inner, cx+r_inner, cy+r_inner], outline=shape_color, width=4)
            r_text = (r_outer + r_inner) / 2

        curved_text_circle(img, company, cx, cy, r_text, -90, text_color, font_top, 1.05, flip=False)
        curved_text_circle(img, address, cx, cy, r_text, 90, text_color, font_bot, 1.08, flip=True)

        icon_size = get_icon_radius(S, icon_scale_mode)
        if icon_source == "Built-in Icon":
            draw_builtin_icon(draw, cx, cy, icon_size, shape_color, icon_name)
        elif icon_source == "Upload Custom Logo" and uploaded_file is not None:
            paste_custom_logo(img, uploaded_file, cx, cy, icon_size, shape_color)

    elif shape == "oval":
        W, H = 1300, 900
        img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        cx, cy = W // 2, H // 2
        rx1, ry1 = W // 2 - 50, H // 2 - 50
        rx2, ry2 = rx1 - 130, ry1 - 130

        draw_ellipse_border(draw, [cx-rx1, cy-ry1, cx+rx1, cy+ry1], shape_color, border_style, width=18)
        draw.ellipse([cx-rx2, cy-ry2, cx+rx2, cy+ry2], outline=shape_color, width=4)

        rx_text, ry_text = (rx1 + rx2) / 2, (ry1 + ry2) / 2
        curved_text_oval(img, company, cx, cy, rx_text, ry_text, -90, text_color, font_top, 1.05, flip=False)
        curved_text_oval(img, address, cx, cy, rx_text, ry_text, 90, text_color, font_bot, 1.08, flip=True)

        icon_size = get_icon_radius(min(W, H), icon_scale_mode)
        if icon_source == "Built-in Icon":
            draw_builtin_icon(draw, cx, cy, icon_size, shape_color, icon_name)
        elif icon_source == "Upload Custom Logo" and uploaded_file is not None:
            paste_custom_logo(img, uploaded_file, cx, cy, icon_size, shape_color)

    elif shape in ["rectangle", "square", "capsule"]:
        W, H = (1200, 800) if shape == "rectangle" else ((1000, 1000) if shape == "square" else (1300, 700))
        img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        cx, pad = W // 2, 32

        rad = H // 2 if shape == "capsule" else 0
        draw_rect_border(draw, [pad, pad, W-pad, H-pad], shape_color, border_style, width=16, radius=rad)

        if shape == "capsule":
            draw.rounded_rectangle([pad+24, pad+24, W-pad-24, H-pad-24], radius=H//2, outline=shape_color, width=4)
        else:
            draw.rectangle([pad+28, pad+28, W-pad-28, H-pad-28], outline=shape_color, width=4)

        draw.text((cx, pad+84), company.upper(), font=font_top, fill=text_color+(255,), anchor="mm")
        draw.line([pad+60, pad+136, W-pad-60, pad+136], fill=shape_color, width=4)
        draw.line([pad+60, H-pad-136, W-pad-60, H-pad-136], fill=shape_color, width=4)
        draw.text((cx, H-pad-84), address.upper(), font=font_bot, fill=text_color+(255,), anchor="mm")

        icon_size = get_icon_radius(min(W, H), icon_scale_mode)
        if icon_source == "Built-in Icon":
            draw_builtin_icon(draw, cx, H//2, icon_size, shape_color, icon_name)
        elif icon_source == "Upload Custom Logo" and uploaded_file is not None:
            paste_custom_logo(img, uploaded_file, cx, H//2, icon_size, shape_color)

    elif shape == "triangle":
        W, H = 1200, 1040
        img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        cx = W // 2

        draw.polygon([(cx, 40), (W-40, H-40), (40, H-40)], outline=shape_color, width=16)
        draw.polygon([(cx, 120), (W-120, H-80), (120, H-80)], outline=shape_color, width=4)

        draw.text((cx, H - 150), company.upper(), font=font_top, fill=text_color+(255,), anchor="mm")
        draw.text((cx, H - 100), address.upper(), font=font_bot, fill=text_color+(255,), anchor="mm")

        icon_size = get_icon_radius(min(W, H), icon_scale_mode)
        if icon_source == "Built-in Icon":
            draw_builtin_icon(draw, cx, H//2 - 40, icon_size, shape_color, icon_name)
        elif icon_source == "Upload Custom Logo" and uploaded_file is not None:
            paste_custom_logo(img, uploaded_file, cx, H//2 - 40, icon_size, shape_color)

    elif shape == "notary_star":
        S = 1200
        img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        cx = cy = S // 2
        r_out = S // 2 - 40

        pts = []
        teeth = 36
        for i in range(teeth * 2):
            angle = math.radians(i * (360 / (teeth * 2)))
            r = r_out if i % 2 == 0 else r_out - 24
            pts.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
        draw.polygon(pts, outline=shape_color, width=6)

        r_inner = r_out - 80
        draw.ellipse([cx-r_inner, cy-r_inner, cx+r_inner, cy+r_inner], outline=shape_color, width=4)

        curved_text_circle(img, company, cx, cy, r_inner-50, -90, text_color, font_top, 1.05, flip=False)
        curved_text_circle(img, address, cx, cy, r_inner-50, 90, text_color, font_bot, 1.08, flip=True)

        icon_size = get_icon_radius(S, icon_scale_mode)
        if icon_source == "Built-in Icon":
            draw_builtin_icon(draw, cx, cy, icon_size, shape_color, icon_name)
        elif icon_source == "Upload Custom Logo" and uploaded_file is not None:
            paste_custom_logo(img, uploaded_file, cx, cy, icon_size, shape_color)

    return img

# ── 7. UI FRONTEND ────────────────────────────────────────────────────────
st.title("🏷️ Official Stamp & Seal Generator")
st.write("Configure and download high-resolution transparent PNG stamps for official approvals.")

col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    st.subheader("1. Text Content & Font Options")
    company_name = st.text_input("Company / Organization Name", "SAKIB HASSAN BUILDING MAINTINANCE LLC")
    fs_top = st.slider("Company Name Font Size", min_value=20, max_value=80, value=52, step=2)

    address_text = st.text_input("Address / Location Text", "AJMAN U.A.E")
    fs_bot = st.slider("Address Text Font Size", min_value=15, max_value=70, value=38, step=2)

    font_style = st.selectbox("Font Typeface", list(FONT_URLS.keys()))

    st.subheader("2. Colors & Design")

    col_c1, col_c2 = st.columns(2)
    with col_c1:
        text_hex = st.color_picker("Text Color", "#1a3d8f")
    with col_c2:
        shape_hex = st.color_picker("Frame & Shape Color", "#1a3d8f")

    col_s1, col_s2 = st.columns(2)
    with col_s1:
        shape = st.selectbox("Stamp Frame Shape", [
            ("Double Ring Circle", "double_round"),
            ("Single Ring Circle", "round"),
            ("Oval", "oval"),
            ("Rectangle", "rectangle"),
            ("Square", "square"),
            ("Capsule / Pill", "capsule"),
            ("Triangle", "triangle"),
            ("Notary Starburst", "notary_star")
        ], format_func=lambda x: x[0])[1]

    with col_s2:
        border_style = st.selectbox("Border Style", ["Solid", "Double Line", "Dashed", "Dotted"])

    st.subheader("3. Icon & Scaling")
    icon_source = st.radio("Center Element", ["Built-in Icon", "Upload Custom Logo"])

    icon_name = "building"
    uploaded_file = None

    if icon_source == "Built-in Icon":
        icon_name = st.selectbox("Choose Icon", ["building", "star", "shield", "gear", "globe", "crown"])
    else:
        uploaded_file = st.file_uploader("Upload PNG/JPG Logo", type=["png", "jpg", "jpeg"])

    icon_scale_mode = st.select_slider("Icon Size Mode", options=["Small", "Medium", "Best Fit", "Large"], value="Best Fit")

with col_right:
    st.subheader("High-Res Live Preview")

    stamp_img = generate_stamp(
        company=company_name,
        address=address_text,
        fs_top=fs_top,
        fs_bot=fs_bot,
        font_style=font_style,
        text_hex=text_hex,
        shape_hex=shape_hex,
        shape=shape,
        border_style=border_style,
        icon_source=icon_source,
        icon_name=icon_name,
        uploaded_file=uploaded_file,
        icon_scale_mode=icon_scale_mode
    )

    st.image(stamp_img, use_container_width=True)

    buf = io.BytesIO()
    stamp_img.save(buf, format="PNG", dpi=(300, 300))
    byte_im = buf.getvalue()

    st.download_button(
        label="💾 Download High-Res PNG (300 DPI)",
        data=byte_im,
        file_name="official_stamp_high_res.png",
        mime="image/png"
    )