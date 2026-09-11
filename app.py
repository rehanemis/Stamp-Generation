import os
import math
import io
import streamlit as st
from PIL import Image, ImageDraw, ImageFont

# -----------------------------------------------------------------------------
# DIRECTORY SETUPS & CONFIGURATIONS
# -----------------------------------------------------------------------------
FRAMES_DIR = "blank_stamps"
ICONS_DIR = "stamp_icons"

os.makedirs(FRAMES_DIR, exist_ok=True)
os.makedirs(ICONS_DIR, exist_ok=True)

# Base dictionary for pre-configured templates
BASE_TEMPLATES = {
    "circular_double": {"name": "Classic Double Ring", "radius": 365, "type": "circle"},
    "starburst": {"name": "Starburst Seal", "radius": 330, "type": "circle"},
    "slanted_ribbon": {"name": "Slanted Central Ribbon", "radius": 360, "type": "circle"},
    "oval_banner": {"name": "Oval Banner Frame", "radius": 380, "type": "circle"},
    "heavy_box": {"name": "Heavy Rectangular Frame", "radius": None, "type": "rectangle"},
    "checkmark_circle": {"name": "Checkmark Seal", "radius": 350, "type": "circle"},
    "cross_shield": {"name": "Rejected Cross Shield", "radius": 360, "type": "circle"}
}

# -----------------------------------------------------------------------------
# HELPER FUNCTIONS
# -----------------------------------------------------------------------------
def load_font(size):
    """Loads a bold truetype font or falls back to system defaults."""
    for font_name in ["arialbd.ttf", "impact.ttf", "DejaVuSans-Bold.ttf", "Arial.ttf"]:
        try:
            return ImageFont.truetype(font_name, size)
        except IOError:
            continue
    return ImageFont.load_default()

def hex_to_rgba(hex_str):
    """Converts HEX color string to RGBA tuple."""
    hex_str = str(hex_str).strip().lstrip('#')
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4)) + (255,)

def get_available_frames():
    """
    Scans blank_stamps/ directory and dynamically builds a template map.
    Capable of scaling up to 100+ stamp frame PNGs seamlessly.
    """
    files = [f for f in os.listdir(FRAMES_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    frames_map = {}
    
    for f in sorted(files):
        key = os.path.splitext(f)[0]
        file_path = os.path.join(FRAMES_DIR, f)
        
        # Pull metadata if in BASE_TEMPLATES, otherwise auto-generate defaults
        if key in BASE_TEMPLATES:
            info = BASE_TEMPLATES[key].copy()
            info["file"] = file_path
        else:
            display_title = key.replace("_", " ").title()
            is_rect = "box" in key.lower() or "rect" in key.lower()
            info = {
                "name": display_title,
                "file": file_path,
                "radius": None if is_rect else 350,
                "type": "rectangle" if is_rect else "circle"
            }
        frames_map[key] = info
        
    # Fallback template if folder is completely empty
    if not frames_map:
        frames_map["default_circle"] = {
            "name": "Default Circular Frame",
            "file": None,
            "radius": 360,
            "type": "circle"
        }
    return frames_map

def get_available_icons():
    """Scans stamp_icons/ directory and returns map of Display Name -> File Path."""
    files = [f for f in os.listdir(ICONS_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    icon_map = {"None (Text / Frame Only)": None}
    for f in sorted(files):
        display_name = os.path.splitext(f)[0].replace("_", " ").title()
        icon_map[display_name] = os.path.join(ICONS_DIR, f)
    return icon_map

def draw_curved_text_top(image_draw, text, cx, cy, radius, font, fill):
    if not text: return
    text = str(text).upper()
    total_angle = min(160, len(text) * 11)
    start_angle = -90 - (total_angle / 2)
    angle_step = total_angle / max(1, (len(text) - 1)) if len(text) > 1 else 0

    for i, char in enumerate(text):
        angle_deg = start_angle + (i * angle_step)
        angle_rad = math.radians(angle_deg)
        x = cx + radius * math.cos(angle_rad)
        y = cy + radius * math.sin(angle_rad)

        char_img = Image.new("RGBA", (140, 140), (0, 0, 0, 0))
        char_draw = ImageDraw.Draw(char_img)
        char_draw.text((70, 70), char, font=font, fill=fill, anchor="mm")
        
        rotated_char = char_img.rotate(angle_deg + 90, resample=Image.BICUBIC)
        image_draw._image.paste(rotated_char, (int(x - 70), int(y - 70)), rotated_char)

def draw_curved_text_bottom(image_draw, text, cx, cy, radius, font, fill):
    if not text: return
    text = str(text).upper()
    total_angle = min(160, len(text) * 11)
    start_angle = 90 + (total_angle / 2)
    angle_step = total_angle / max(1, (len(text) - 1)) if len(text) > 1 else 0

    for i, char in enumerate(text):
        angle_deg = start_angle - (i * angle_step)
        angle_rad = math.radians(angle_deg)
        x = cx + radius * math.cos(angle_rad)
        y = cy + radius * math.sin(angle_rad)

        char_img = Image.new("RGBA", (140, 140), (0, 0, 0, 0))
        char_draw = ImageDraw.Draw(char_img)
        char_draw.text((70, 70), char, font=font, fill=fill, anchor="mm")
        
        rotated_char = char_img.rotate(angle_deg - 90, resample=Image.BICUBIC)
        image_draw._image.paste(rotated_char, (int(x - 70), int(y - 70)), rotated_char)

def render_stamp(template_info, top_text, center_text, bottom_text, hex_color, icon_path):
    """Generates complete stamp image canvas with frame, text, and icons."""
    S = 1000
    cx, cy = S // 2, S // 2
    color = hex_to_rgba(hex_color)

    # 1. Base Canvas Preparation
    frame_file = template_info.get("file")
    if frame_file and os.path.exists(frame_file):
        base = Image.open(frame_file).convert("RGBA")
        r, g, b, alpha = base.split()
        canvas = Image.new("RGBA", base.size, color)
        canvas.putalpha(alpha)
    else:
        canvas = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        fallback_draw = ImageDraw.Draw(canvas)
        fallback_draw.ellipse([50, 50, 950, 950], outline=color, width=16)

    draw = ImageDraw.Draw(canvas)
    font_arc = load_font(48)
    font_center = load_font(75)

    # 2. Add Curved Arc Text (If Circle Template)
    if template_info.get("type") == "circle" and template_info.get("radius"):
        draw_curved_text_top(draw, top_text, cx, cy, template_info["radius"], font_arc, color)
        draw_curved_text_bottom(draw, bottom_text, cx, cy, template_info["radius"], font_arc, color)

    # 3. Add Center Icon or Center Text
    if icon_path and os.path.exists(icon_path):
        raw_icon = Image.open(icon_path).convert("RGBA")
        target_size = int(S * 0.35)
        raw_icon.thumbnail((target_size, target_size), Image.Resampling.LANCZOS)
        
        # Tint icon to stamp color using its alpha channel
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
st.markdown("Select from dynamic stamp frames and icons, preview live thumbnails, curve text, and export high-res PNGs.")

col_controls, col_preview = st.columns([1, 1])

with col_controls:
    st.subheader("1. Frame & Style Selection")
    
    all_frames = get_available_frames()
    frame_keys = list(all_frames.keys())
    
    # Dropdown to choose among all loaded blank stamp templates
    selected_frame_key = st.selectbox(
        f"Select Blank Stamp Frame ({len(frame_keys)} Loaded)",
        options=frame_keys,
        format_func=lambda x: all_frames[x]["name"]
    )
    selected_template = all_frames[selected_frame_key]

    # Live frame icon/thumbnail preview
    if selected_template.get("file") and os.path.exists(selected_template["file"]):
        col_frame_preview, col_color = st.columns([1, 3])
        with col_frame_preview:
            st.image(selected_template["file"], width=80, caption="Frame Preview")
        with col_color:
            ink_color = st.color_picker("Stamp Ink Color", "#C2185B")
    else:
        ink_color = st.color_picker("Stamp Ink Color", "#C2185B")

    st.subheader("2. Center Icon / Logo")
    available_icons = get_available_icons()
    selected_icon_name = st.selectbox(
        f"Select Center Icon ({len(available_icons)-1} Loaded)",
        list(available_icons.keys())
    )
    selected_icon_path = available_icons[selected_icon_name]

    # Live center icon thumbnail preview
    if selected_icon_path and os.path.exists(selected_icon_path):
        st.image(selected_icon_path, caption=f"Icon Preview: {selected_icon_name}", width=70)

    st.subheader("3. Stamp Text Fields")
    top_text = st.text_input("Top Arc Text", "RUKN AL MADAR SERVICES")
    center_text = st.text_input("Center Text (Used if no icon is selected)", "VERIFIED")
    bottom_text = st.text_input("Bottom Arc Text", "OFFICIAL APPROVED SEAL")

# Generate main live preview
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