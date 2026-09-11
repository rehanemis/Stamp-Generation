import os
import math
import io
import streamlit as st
from PIL import Image, ImageDraw, ImageFont

# -----------------------------------------------------------------------------
# DIRECTORY SETUPS & AUTOMATIC ASSET GENERATION
# -----------------------------------------------------------------------------
FRAMES_DIR = "blank_stamps"
ICONS_DIR = "stamp_icons"

os.makedirs(FRAMES_DIR, exist_ok=True)
os.makedirs(ICONS_DIR, exist_ok=True)

def generate_default_assets_if_empty():
    """Generates starter PNG frames and icons if folders are empty on GitHub."""
    S = 1000
    
    # 1. Create default blank stamp frames if blank_stamps/ is empty
    if not [f for f in os.listdir(FRAMES_DIR) if f.lower().endswith('.png')]:
        # Circular Double Frame
        img1 = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        d1 = ImageDraw.Draw(img1)
        d1.ellipse([40, 40, 960, 960], outline=(0, 0, 0, 255), width=20)
        d1.ellipse([70, 70, 930, 930], outline=(0, 0, 0, 255), width=6)
        d1.ellipse([180, 180, 820, 820], outline=(0, 0, 0, 255), width=8)
        img1.save(os.path.join(FRAMES_DIR, "circular_double.png"))

        # Starburst Frame
        img2 = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        d2 = ImageDraw.Draw(img2)
        d2.ellipse([50, 50, 950, 950], outline=(0, 0, 0, 255), width=24)
        d2.ellipse([160, 160, 840, 840], outline=(0, 0, 0, 255), width=8)
        img2.save(os.path.join(FRAMES_DIR, "starburst.png"))

    # 2. Create default icons if stamp_icons/ is empty
    if not [f for f in os.listdir(ICONS_DIR) if f.lower().endswith('.png')]:
        # Star Icon
        star_img = Image.new("RGBA", (400, 400), (0, 0, 0, 0))
        sd = ImageDraw.Draw(star_img)
        star_points = [(200, 20), (250, 140), (380, 140), (275, 210), (315, 340), (200, 260), (85, 340), (125, 210), (20, 140), (150, 140)]
        sd.polygon(star_points, fill=(0, 0, 0, 255))
        star_img.save(os.path.join(ICONS_DIR, "star.png"))

        # Checkmark Icon
        check_img = Image.new("RGBA", (400, 400), (0, 0, 0, 0))
        cd = ImageDraw.Draw(check_img)
        cd.line([(60, 200), (160, 300), (340, 100)], fill=(0, 0, 0, 255), width=45)
        check_img.save(os.path.join(ICONS_DIR, "checkmark.png"))

# Run auto-generator check
generate_default_assets_if_empty()

BASE_TEMPLATES = {
    "circular_double": {"name": "Classic Double Ring", "radius": 360, "type": "circle"},
    "starburst": {"name": "Starburst Seal", "radius": 330, "type": "circle"}
}

# -----------------------------------------------------------------------------
# HELPER FUNCTIONS
# -----------------------------------------------------------------------------
def load_font(size):
    for font_name in ["arialbd.ttf", "impact.ttf", "DejaVuSans-Bold.ttf", "Arial.ttf"]:
        try:
            return ImageFont.truetype(font_name, size)
        except IOError:
            continue
    return ImageFont.load_default()

def hex_to_rgba(hex_str):
    hex_str = str(hex_str).strip().lstrip('#')
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4)) + (255,)

def get_available_frames():
    files = [f for f in os.listdir(FRAMES_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    frames_map = {}
    
    for f in sorted(files):
        key = os.path.splitext(f)[0]
        file_path = os.path.join(FRAMES_DIR, f)
        
        if key in BASE_TEMPLATES:
            info = BASE_TEMPLATES[key].copy()
            info["file"] = file_path
        else:
            display_title = key.replace("_", " ").title()
            is_rect = "box" in key.lower() or "rect" in key.lower()
            info = {
                "name": display_title,
                "file": file_path,
                "radius": None if is_rect else 360,
                "type": "rectangle" if is_rect else "circle"
            }
        frames_map[key] = info
        
    return frames_map

def get_available_icons():
    files = [f for f in os.listdir(ICONS_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    icon_map = {"None (Text / Frame Only)": None}
    for f in sorted(files):
        display_name = os.path.splitext(f)[0].replace("_", " ").title()
        icon_map[display_name] = os.path.join(ICONS_DIR, f)
    return icon_map

def draw_curved_text_top(canvas, text, cx, cy, radius, font, fill):
    if not text: return
    text = str(text).upper()
    
    total_angle = min(160, len(text) * 9.5)
    start_angle = -90 - (total_angle / 2)
    angle_step = total_angle / max(1, (len(text) - 1)) if len(text) > 1 else 0

    for i, char in enumerate(text):
        angle_deg = start_angle + (i * angle_step)
        angle_rad = math.radians(angle_deg)
        
        x = cx + radius * math.cos(angle_rad)
        y = cy + radius * math.sin(angle_rad)

        cell_size = 100
        char_img = Image.new("RGBA", (cell_size, cell_size), (0, 0, 0, 0))
        char_draw = ImageDraw.Draw(char_img)
        char_draw.text((cell_size // 2, cell_size // 2), char, font=font, fill=fill, anchor="mm")
        
        rotated = char_img.rotate(angle_deg + 90, resample=Image.BICUBIC, expand=False)
        
        px = int(x - (cell_size // 2))
        py = int(y - (cell_size // 2))
        canvas.paste(rotated, (px, py), rotated)

def draw_curved_text_bottom(canvas, text, cx, cy, radius, font, fill):
    if not text: return
    text = str(text).upper()
    
    total_angle = min(160, len(text) * 9.5)
    start_angle = 90 + (total_angle / 2)
    angle_step = total_angle / max(1, (len(text) - 1)) if len(text) > 1 else 0

    for i, char in enumerate(text):
        angle_deg = start_angle - (i * angle_step)
        angle_rad = math.radians(angle_deg)
        
        x = cx + radius * math.cos(angle_rad)
        y = cy + radius * math.sin(angle_rad)

        cell_size = 100
        char_img = Image.new("RGBA", (cell_size, cell_size), (0, 0, 0, 0))
        char_draw = ImageDraw.Draw(char_img)
        char_draw.text((cell_size // 2, cell_size // 2), char, font=font, fill=fill, anchor="mm")
        
        rotated = char_img.rotate(angle_deg - 90, resample=Image.BICUBIC, expand=False)
        
        px = int(x - (cell_size // 2))
        py = int(y - (cell_size // 2))
        canvas.paste(rotated, (px, py), rotated)

def render_stamp(template_info, top_text, center_text, bottom_text, hex_color, icon_path):
    S = 1000
    cx, cy = S // 2, S // 2
    color = hex_to_rgba(hex_color)

    frame_file = template_info.get("file")
    if frame_file and os.path.exists(frame_file):
        base = Image.open(frame_file).convert("RGBA")
        r, g, b, alpha = base.split()
        canvas = Image.new("RGBA", base.size, color)
        canvas.putalpha(alpha)
    else:
        canvas = Image.new("RGBA", (S, S), (0, 0, 0, 0))

    draw = ImageDraw.Draw(canvas)
    font_arc = load_font(46)
    font_center = load_font(72)

    if template_info.get("type") == "circle" and template_info.get("radius"):
        draw_curved_text_top(canvas, top_text, cx, cy, template_info["radius"], font_arc, color)
        draw_curved_text_bottom(canvas, bottom_text, cx, cy, template_info["radius"], font_arc, color)

    if icon_path and os.path.exists(icon_path):
        raw_icon = Image.open(icon_path).convert("RGBA")
        target_size = int(S * 0.35)
        raw_icon.thumbnail((target_size, target_size), Image.Resampling.LANCZOS)
        
        ir, ig, ib, ialpha = raw_icon.split()
        tinted_icon = Image.new("RGBA", raw_icon.size, color)
        tinted_icon.putalpha(ialpha)
        
        ix = cx - (tinted_icon.width // 2)
        iy = cy - (tinted_icon.height // 2)
        canvas.paste(tinted_icon, (ix, iy), tinted_icon)
    elif center_text:
        draw.text((cx, cy), str(center_text).upper(), font=font_center, fill=color, anchor="mm")

    return canvas

# -----------------------------------------------------------------------------
# STREAMLIT UI LAYOUT
# -----------------------------------------------------------------------------
st.set_page_config(page_title="Multi-Company Stamp Generator", layout="wide")

st.title("🏷️ Multi-Company Rubber Stamp Generator")

col_controls, col_preview = st.columns([1, 1])

with col_controls:
    st.subheader("1. Frame & Style Selection")
    all_frames = get_available_frames()
    frame_keys = list(all_frames.keys())
    
    selected_frame_key = st.selectbox(
        f"Select Blank Stamp Frame ({len(frame_keys)} Loaded)",
        options=frame_keys,
        format_func=lambda x: all_frames[x]["name"]
    )
    selected_template = all_frames[selected_frame_key]

    ink_color = st.color_picker("Stamp Ink Color", "#C2185B")

    st.subheader("2. Center Icon / Logo")
    available_icons = get_available_icons()
    selected_icon_name = st.selectbox(
        f"Select Center Icon ({len(available_icons)-1} Loaded)",
        list(available_icons.keys())
    )
    selected_icon_path = available_icons[selected_icon_name]

    if selected_icon_path and os.path.exists(selected_icon_path):
        st.image(selected_icon_path, caption=f"Icon Preview: {selected_icon_name}", width=70)

    st.subheader("3. Stamp Text Fields")
    top_text = st.text_input("Top Arc Text", "RUKN AL MADAR SERVICES")
    center_text = st.text_input("Center Text (Used if no icon is selected)", "VERIFIED")
    bottom_text = st.text_input("Bottom Arc Text", "OFFICIAL APPROVED SEAL")

stamp_canvas = render_stamp(
    template_info=selected_template,
    top_text=top_text,
    center_text=center_text,
    bottom_text=bottom_text,
    hex_color=ink_color,
    icon_path=selected_icon_path
)

with col_preview:
    st.subheader("Live High-Res Stamp Preview")
    st.image(stamp_canvas, use_container_width=True)
    
    buf = io.BytesIO()
    stamp_canvas.save(buf, format="PNG")
    byte_im = buf.getvalue()

    st.download_button(
        label="📥 Download High-Res PNG Stamp",
        data=byte_im,
        file_name=f"{selected_frame_key}_stamp.png",
        mime="image/png"
    )