import math
import os
import io
import streamlit as st
from PIL import Image, ImageDraw, ImageFont

# ── 1. PAGE & UI CONFIGURATION ────────────────────────────────────────────
st.set_page_config(
    page_title="Official Stamp Generator",
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

# ── 2. FONT HELPER ─────────────────────────────────────────────────────────
def get_font(size, bold=True):
    paths = [
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/calibrib.ttf" if bold else "C:/Windows/Fonts/calibri.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for p in paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()

def hex_to_rgb(hex_color):
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

# ── 3. CURVED TEXT RENDERERS ──────────────────────────────────────────────
def curved_text_circle(img, text, cx, cy, radius, start_deg, color, font, spacing=1.05, flip=False):
    if not text.strip():
        return
    chars = list(text.upper())
    widths = []
    for ch in chars:
        try:
            bb = font.getbbox(ch)
            widths.append(max((bb[2] - bb[0]) * spacing, 7))
        except Exception:
            widths.append(15 * spacing)

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
            sz = int(cw) + 40
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
            sz = int(cw) + 40
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
            widths.append(max((bb[2] - bb[0]) * spacing, 7))
        except Exception:
            widths.append(15 * spacing)

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

            sz = int(cw) + 40
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

            sz = int(cw) + 40
            ch_im = Image.new("RGBA", (sz, sz), (0, 0, 0, 0))
            ImageDraw.Draw(ch_im).text((sz//2, sz//2), ch, font=font, fill=color+(255,), anchor="mm")
            ch_im = ch_im.rotate(-rot, expand=True, resample=Image.BICUBIC)
            pw, ph = ch_im.size
            img.paste(ch_im, (int(x - pw/2), int(y - ph/2)), ch_im)
            cur += cw / r_avg

# ── 4. DYNAMIC ICONS & CUSTOM LOGO HANDLING ──────────────────────────────
def get_icon_radius(canvas_dim, icon_scale_mode):
    scale_map = {
        "Small": 0.15,
        "Medium": 0.22,
        "Large": 0.30,
        "Best Fit": 0.26
    }
    multiplier = scale_map.get(icon_scale_mode, 0.26)
    return int(canvas_dim * multiplier)

def draw_builtin_icon(draw, cx, cy, size, color, icon_name):
    c = color + (220,)
    s = size

    if icon_name == "building":
        draw.rectangle([cx-s, cy-s//4, cx+s, cy+s//2], outline=c, width=2)
        draw.polygon([cx-s, cy-s//4, cx, cy-s, cx+s, cy-s//4], outline=c, width=2)
        ws = s // 3
        for col in [-1, 1]:
            wx = cx + col*(s//2) - ws//2
            draw.rectangle([wx, cy-s//5, wx+ws, cy+s//8], outline=c, width=1)
        draw.rectangle([cx-ws//2, cy+s//8, cx+ws//2, cy+s//2], outline=c, width=1)

    elif icon_name == "star":
        pts = []
        for i in range(10):
            a = math.radians(i*36 - 90)
            r = s if i % 2 == 0 else s // 2
            pts.append((cx + r*math.cos(a), cy + r*math.sin(a)))
        draw.polygon(pts, outline=c, width=2)

    elif icon_name == "shield":
        draw.polygon([
            cx-s, cy-s, cx+s, cy-s,
            cx+s, cy+s//3, cx, cy+s,
            cx-s, cy+s//3
        ], outline=c, width=2)
        draw.line([cx, cy-s+4, cx, cy+s-10], fill=c, width=1)
        draw.line([cx-s+4, cy-s//4, cx+s-4, cy-s//4], fill=c, width=1)

    elif icon_name == "gear":
        teeth = 8
        for i in range(teeth):
            a1 = math.radians(i*360/teeth)
            a2 = math.radians(i*360/teeth + 16)
            pts = [
                cx+s*math.cos(a1), cy+s*math.sin(a1),
                cx+(s+12)*math.cos(a1), cy+(s+12)*math.sin(a1),
                cx+(s+12)*math.cos(a2), cy+(s+12)*math.sin(a2),
                cx+s*math.cos(a2), cy+s*math.sin(a2),
            ]
            draw.polygon(pts, outline=c, width=1)
        draw.ellipse([cx-s, cy-s, cx+s, cy+s], outline=c, width=2)

    elif icon_name == "globe":
        draw.ellipse([cx-s, cy-s, cx+s, cy+s], outline=c, width=2)
        draw.ellipse([cx-s//2, cy-s, cx+s//2, cy+s], outline=c, width=1)
        draw.line([cx-s, cy, cx+s, cy], fill=c, width=1)

    elif icon_name == "crown":
        base_y = cy + s//2
        draw.polygon([
            cx-s, base_y, cx-s, cy-s//2,
            cx-s//2, cy, cx, cy-s,
            cx+s//2, cy, cx+s, cy-s//2,
            cx+s, base_y
        ], outline=c, width=2)

def paste_custom_logo(base_img, uploaded_file, cx, cy, max_size, target_color):
    logo = Image.open(uploaded_file).convert("RGBA")
    logo.thumbnail((max_size * 2, max_size * 2), Image.BICUBIC)
    
    alpha = logo.split()[3]
    color_img = Image.new("RGBA", logo.size, target_color + (255,))
    color_img.putalpha(alpha)
    
    lw, lh = color_img.size
    base_img.paste(color_img, (cx - lw // 2, cy - lh // 2), color_img)

# ── 5. STAMP BUILDER ENGINE ───────────────────────────────────────────────
def generate_stamp(company, address, fs_top, fs_bot, hex_color, shape, icon_source, icon_name, uploaded_file, icon_scale_mode):
    color = hex_to_rgb(hex_color)

    if shape in ["double_round", "round"]:
        S = 620
        img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        cx = cy = S // 2
        r_outer = S // 2 - 25
        r_inner = r_outer - 55

        if shape == "double_round":
            r_mid = r_outer - 55
            r_inner = r_mid - 20
            draw.ellipse([cx-r_outer, cy-r_outer, cx+r_outer, cy+r_outer], outline=color, width=10)
            draw.ellipse([cx-r_mid, cy-r_mid, cx+r_mid, cy+r_mid], outline=color, width=2)
            draw.ellipse([cx-r_inner, cy-r_inner, cx+r_inner, cy+r_inner], outline=color, width=1)
            r_text = (r_outer + r_mid) / 2
        else:
            draw.ellipse([cx-r_outer, cy-r_outer, cx+r_outer, cy+r_outer], outline=color, width=10)
            draw.ellipse([cx-r_inner, cy-r_inner, cx+r_inner, cy+r_inner], outline=color, width=2)
            r_text = (r_outer + r_inner) / 2

        curved_text_circle(img, company, cx, cy, r_text, -90, color, get_font(fs_top, True), 1.05, flip=False)
        curved_text_circle(img, address, cx, cy, r_text, 90, color, get_font(fs_bot, True), 1.08, flip=True)
        
        icon_size = get_icon_radius(S, icon_scale_mode)
        if icon_source == "Built-in Icon":
            draw_builtin_icon(draw, cx, cy, icon_size, color, icon_name)
        elif icon_source == "Upload Custom Logo" and uploaded_file is not None:
            paste_custom_logo(img, uploaded_file, cx, cy, icon_size, color)

    elif shape == "oval":
        W, H = 700, 480
        img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        cx, cy = W // 2, H // 2
        rx1, ry1 = W // 2 - 25, H // 2 - 25
        rx2, ry2 = rx1 - 65, ry1 - 65

        draw.ellipse([cx-rx1, cy-ry1, cx+rx1, cy+ry1], outline=color, width=10)
        draw.ellipse([cx-rx2, cy-ry2, cx+rx2, cy+ry2], outline=color, width=2)

        rx_text = (rx1 + rx2) / 2
        ry_text = (ry1 + ry2) / 2
        curved_text_oval(img, company, cx, cy, rx_text, ry_text, -90, color, get_font(fs_top, True), 1.05, flip=False)
        curved_text_oval(img, address, cx, cy, rx_text, ry_text, 90, color, get_font(fs_bot, True), 1.08, flip=True)

        icon_size = get_icon_radius(min(W, H), icon_scale_mode)
        if icon_source == "Built-in Icon":
            draw_builtin_icon(draw, cx, cy, icon_size, color, icon_name)
        elif icon_source == "Upload Custom Logo" and uploaded_file is not None:
            paste_custom_logo(img, uploaded_file, cx, cy, icon_size, color)

    elif shape in ["rectangle", "square", "capsule"]:
        W, H = (600, 400) if shape == "rectangle" else ((500, 500) if shape == "square" else (650, 350))
        img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        cx = W // 2
        pad = 16

        if shape == "capsule":
            draw.rounded_rectangle([pad, pad, W-pad, H-pad], radius=H//2, outline=color, width=8)
            draw.rounded_rectangle([pad+12, pad+12, W-pad-12, H-pad-12], radius=H//2, outline=color, width=2)
        else:
            draw.rectangle([pad, pad, W-pad, H-pad], outline=color, width=8)
            draw.rectangle([pad+14, pad+14, W-pad-14, H-pad-14], outline=color, width=2)

        draw.text((cx, pad+42), company.upper(), font=get_font(fs_top, True), fill=color+(255,), anchor="mm")
        draw.line([pad+30, pad+68, W-pad-30, pad+68], fill=color, width=2)
        draw.line([pad+30, H-pad-68, W-pad-30, H-pad-68], fill=color, width=2)
        draw.text((cx, H-pad-42), address.upper(), font=get_font(fs_bot, True), fill=color+(255,), anchor="mm")

        icon_size = get_icon_radius(min(W, H), icon_scale_mode)
        if icon_source == "Built-in Icon":
            draw_builtin_icon(draw, cx, H//2, icon_size, color, icon_name)
        elif icon_source == "Upload Custom Logo" and uploaded_file is not None:
            paste_custom_logo(img, uploaded_file, cx, H//2, icon_size, color)

    elif shape == "triangle":
        W, H = 600, 520
        img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        cx = W // 2
        
        pts_out = [(cx, 20), (W-20, H-20), (20, H-20)]
        pts_in = [(cx, 60), (W-60, H-40), (60, H-40)]
        draw.polygon(pts_out, outline=color, width=8)
        draw.polygon(pts_in, outline=color, width=2)

        draw.text((cx, H - 75), company.upper(), font=get_font(fs_top, True), fill=color+(255,), anchor="mm")
        draw.text((cx, H - 50), address.upper(), font=get_font(fs_bot, True), fill=color+(255,), anchor="mm")

        icon_size = get_icon_radius(min(W, H), icon_scale_mode)
        if icon_source == "Built-in Icon":
            draw_builtin_icon(draw, cx, H//2 - 20, icon_size, color, icon_name)
        elif icon_source == "Upload Custom Logo" and uploaded_file is not None:
            paste_custom_logo(img, uploaded_file, cx, H//2 - 20, icon_size, color)

    elif shape == "notary_star":
        S = 620
        img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        cx = cy = S // 2
        r_out = S // 2 - 20

        pts = []
        teeth = 36
        for i in range(teeth * 2):
            angle = math.radians(i * (360 / (teeth * 2)))
            r = r_out if i % 2 == 0 else r_out - 12
            pts.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
        draw.polygon(pts, outline=color, width=3)

        r_inner = r_out - 40
        draw.ellipse([cx-r_inner, cy-r_inner, cx+r_inner, cy+r_inner], outline=color, width=2)

        curved_text_circle(img, company, cx, cy, r_inner-25, -90, color, get_font(fs_top, True), 1.05, flip=False)
        curved_text_circle(img, address, cx, cy, r_inner-25, 90, color, get_font(fs_bot, True), 1.08, flip=True)

        icon_size = get_icon_radius(S, icon_scale_mode)
        if icon_source == "Built-in Icon":
            draw_builtin_icon(draw, cx, cy, icon_size, color, icon_name)
        elif icon_source == "Upload Custom Logo" and uploaded_file is not None:
            paste_custom_logo(img, uploaded_file, cx, cy, icon_size, color)

    return img

# ── 6. APPLICATION INTERFACE ──────────────────────────────────────────────
st.title("🏷️ Official Stamp & Seal Generator")
st.write("Configure and download custom transparent PNG stamps for official document approvals.")

col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    st.subheader("1. Text Content & Font Sizes")
    company_name = st.text_input("Company / Organization Name", "NATIONAL COMMISSION FOR HUMAN DEVELOPMENT")
    fs_top = st.slider("Company Name Font Size", min_value=10, max_value=40, value=22, step=1)

    address_text = st.text_input("Address / Location Text", "TEHSIL AND DISTRICT NAROWAL")
    fs_bot = st.slider("Address Text Font Size", min_value=10, max_value=35, value=18, step=1)

    st.subheader("2. Design & Ink")
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

    hex_color = st.color_picker("Ink Color", "#1a3d8f")

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
    st.subheader("Live Stamp Preview")
    
    stamp_img = generate_stamp(
        company=company_name,
        address=address_text,
        fs_top=fs_top,
        fs_bot=fs_bot,
        hex_color=hex_color,
        shape=shape,
        icon_source=icon_source,
        icon_name=icon_name,
        uploaded_file=uploaded_file,
        icon_scale_mode=icon_scale_mode
    )

    st.image(stamp_img, use_container_width=True)

    buf = io.BytesIO()
    stamp_img.save(buf, format="PNG")
    byte_im = buf.getvalue()

    st.download_button(
        label="💾 Download Transparent PNG Stamp",
        data=byte_im,
        file_name="official_stamp.png",
        mime="image/png"
    )