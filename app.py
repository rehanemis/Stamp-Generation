import io
import math
import random
import streamlit as st
from PIL import Image, ImageDraw, ImageFont

# ==========================================
# 1. DATABASE / CONFIGURATION (PRESETS)
# ==========================================
STAMPS_DATABASE = {
    "stamp_001": {
        "name": "First Class Angled Ribbon",
        "family": "ribbon_circle",
        "default_color": "#2B3A4A",
        "ribbon_angle": -12,
        "outer_ring_width": 110,
        "border_style": "cogwheel",
        "text_type": "two_lines_center",
        "defaults": {
            "top": "FIRST CLASS • FIRST CLASS",
            "line1": "FIRST",
            "line2": "CLASS"
        }
    },
    "stamp_002": {
        "name": "Center Box Banner (e.g. Best Buy)",
        "family": "circular_box",
        "default_color": "#8E24AA",
        "ribbon_angle": 0,
        "border_style": "dotted_double",
        "text_type": "three_fields",
        "defaults": {
            "top": "MONEY BACK",
            "center": "BEST BUY",
            "bottom": "GUARANTEED"
        }
    },
    "stamp_003": {
        "name": "Sawtooth Starburst (e.g. Best Seller)",
        "family": "polygon",
        "default_color": "#D32F2F",
        "sides": 24,
        "text_type": "three_fields",
        "defaults": {
            "top": "100% QUALITY",
            "center": "BEST SELLER",
            "bottom": "OFFICIAL STAMP"
        }
    },
    "stamp_004": {
        "name": "Classic Rounded Box (e.g. 100% Recycled)",
        "family": "rectangle",
        "default_color": "#2E7D32",
        "text_type": "two_lines_center",
        "defaults": {
            "top": "",
            "line1": "100%",
            "line2": "RECYCLED"
        }
    }
}


# ==========================================
# 2. HELPER UTILITIES & TEXT CURVING
# ==========================================

def hex_to_rgba(hex_str, alpha=255):
    """Converts hex color code string to RGBA tuple."""
    hex_str = hex_str.lstrip('#')
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4)) + (alpha,)


def load_font(size):
    """Loads a bold font with fallback to default font."""
    font_candidates = ["impact.ttf", "arialbd.ttf", "DejaVuSans-Bold.ttf"]
    for font_name in font_candidates:
        try:
            return ImageFont.truetype(font_name, size)
        except IOError:
            continue
    return ImageFont.load_default()


def draw_curved_text_top(image_draw, text, cx, cy, radius, font, fill):
    """Renders text curved along the top arch of a circle."""
    if not text:
        return
    text = text.upper()
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
        
        rotated_char = char_img.rotate(angle_deg + 90, resample=Image.BICUBIC, expand=False)
        image_draw._image.paste(rotated_char, (int(x - 70), int(y - 70)), rotated_char)


def draw_curved_text_bottom(image_draw, text, cx, cy, radius, font, fill):
    """Renders text curved along the bottom arch of a circle."""
    if not text:
        return
    text = text.upper()
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
        
        rotated_char = char_img.rotate(angle_deg - 90, resample=Image.BICUBIC, expand=False)
        image_draw._image.paste(rotated_char, (int(x - 70), int(y - 70)), rotated_char)


def apply_grunge_texture(img, intensity=0.3):
    """Applies noise restricted ONLY to non-transparent ink pixels."""
    if intensity <= 0:
        return img
    
    noise = Image.new("L", img.size, 255)
    draw_noise = ImageDraw.Draw(noise)
    num_specks = int(img.width * img.height * 0.005 * intensity)
    
    for _ in range(num_specks):
        x = random.randint(0, img.width)
        y = random.randint(0, img.height)
        r = random.randint(1, 3)
        draw_noise.ellipse([x-r, y-r, x+r, y+r], fill=random.randint(20, 120))

    r, g, b, a = img.split()
    a_masked = Image.composite(Image.eval(a, lambda p: 0), a, noise)
    return Image.merge("RGBA", (r, g, b, a_masked))


# ==========================================
# 3. RENDERING ENGINES
# ==========================================

def render_ribbon_circle(spec, top_text, line1, line2, color_hex):
    S = 1000
    cx, cy = S // 2, S // 2
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    color = hex_to_rgba(color_hex)

    left_tail = [(50, cy + 80), (180, cy - 100), (220, cy + 20)]
    right_tail = [(S - 50, cy - 80), (S - 180, cy + 100), (S - 220, cy - 20)]
    draw.polygon(left_tail, fill=color)
    draw.polygon(right_tail, fill=color)

    r_outer = 420
    ring_w = spec.get("outer_ring_width", 110)
    draw.ellipse([cx - r_outer, cy - r_outer, cx + r_outer, cy + r_outer], fill=color)

    r_inner = r_outer - ring_w
    draw.ellipse([cx - r_inner, cy - r_inner, cx + r_inner, cy + r_inner], fill=(255, 255, 255, 255))

    if spec.get("border_style") == "cogwheel":
        r_cog = r_inner - 15
        num_notches = 24
        for i in range(num_notches):
            a1 = math.radians(i * (360 / num_notches))
            a2 = math.radians((i + 0.5) * (360 / num_notches))
            x1, y1 = cx + r_cog * math.cos(a1), cy + r_cog * math.sin(a1)
            x2, y2 = cx + r_cog * math.cos(a2), cy + r_cog * math.sin(a2)
            draw.line([(x1, y1), (x2, y2)], fill=color, width=14)

    font_arc = load_font(42)
    draw_curved_text_top(draw, top_text, cx, cy, radius=365, font=font_arc, fill=(255, 255, 255, 255))

    font_main = load_font(120)
    draw.text((cx, cy - 55), line1.upper(), font=font_main, fill=color, anchor="mm")
    draw.text((cx, cy + 55), line2.upper(), font=font_main, fill=color, anchor="mm")

    angle = spec.get("ribbon_angle", 0)
    if angle != 0:
        img = img.rotate(angle, resample=Image.BICUBIC, expand=False)

    return img


def render_circular_box(spec, top_text, center_text, bottom_text, color_hex):
    S = 1000
    cx, cy = S // 2, S // 2
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    color = hex_to_rgba(color_hex)

    draw.ellipse([80, 80, S - 80, S - 80], outline=color, width=16)
    draw.ellipse([120, 120, S - 120, S - 120], outline=color, width=6)
    draw.ellipse([180, 180, S - 180, S - 180], outline=color, width=4)

    font_arc = load_font(45)
    draw_curved_text_top(draw, top_text.upper(), cx, cy, radius=390, font=font_arc, fill=color)
    draw_curved_text_bottom(draw, bottom_text.upper(), cx, cy, radius=390, font=font_arc, fill=color)

    box_w, box_h = 780, 180
    box_rect = [cx - box_w//2, cy - box_h//2, cx + box_w//2, cy + box_h//2]
    
    draw.rectangle(box_rect, fill=(255, 255, 255, 255))
    draw.rectangle(box_rect, outline=color, width=14)

    font_lg = load_font(85)
    draw.text((cx, cy), center_text.upper(), font=font_lg, fill=color, anchor="mm")

    return img


def render_rectangle(spec, line1, line2, color_hex):
    W, H = 1000, 600
    cx, cy = W // 2, H // 2
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    color = hex_to_rgba(color_hex)

    draw.rounded_rectangle([30, 30, W - 30, H - 30], radius=35, outline=color, width=16)
    draw.rounded_rectangle([60, 60, W - 60, H - 60], radius=20, outline=color, width=6)

    font_main = load_font(110)
    draw.text((cx, cy - 60), line1.upper(), font=font_main, fill=color, anchor="mm")
    draw.text((cx, cy + 60), line2.upper(), font=font_main, fill=color, anchor="mm")

    return img


def render_logo_to_stamp(uploaded_file, top_text, center_text, bottom_text, color_hex, threshold_val=200, crop_ratio=0.38):
    """Strips outer text rings from uploaded image and re-builds new stamp with user text."""
    S = 1000
    cx, cy = S // 2, S // 2
    
    canvas = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    color = hex_to_rgba(color_hex)

    if uploaded_file is not None:
        try:
            # 1. Flatten uploaded image
            raw_img = Image.open(uploaded_file).convert("RGBA")
            bg = Image.new("RGBA", raw_img.size, (255, 255, 255, 255))
            flattened = Image.alpha_composite(bg, raw_img).convert("L")
            
            # 2. High-contrast threshold mask
            mono_mask = flattened.point(lambda p: 255 if p < threshold_val else 0, mode='L')
            
            # 3. MASK OUT OUTER TEXT & RINGS: Keep only central icon circle
            lw, lh = mono_mask.size
            lcx, lcy = lw // 2, lh // 2
            max_r = int(min(lw, lh) * crop_ratio)
            
            circle_mask = Image.new("L", (lw, lh), 0)
            mask_draw = ImageDraw.Draw(circle_mask)
            mask_draw.ellipse([lcx - max_r, lcy - max_r, lcx + max_r, lcy + max_r], fill=255)
            
            # Combine image mask and center circular crop mask
            isolated_center_mask = Image.eval(Image.merge("L", (mono_mask,)), lambda p: 0)
            isolated_center_mask = Image.composite(mono_mask, isolated_center_mask, circle_mask)

            # 4. Colorize central icon
            colored_icon = Image.new("RGBA", raw_img.size, color)
            colored_icon.putalpha(isolated_center_mask)
            
            # 5. Scale and place central icon on canvas
            target_size = int(S * 0.45)
            colored_icon.thumbnail((target_size, target_size), Image.Resampling.LANCZOS)
            
            lx = cx - (colored_icon.width // 2)
            ly = cy - (colored_icon.height // 2)
            canvas.paste(colored_icon, (lx, ly), colored_icon)
        except Exception as e:
            st.error(f"Error processing image: {e}")

    # Draw New Clean Rings
    draw.ellipse([50, 50, S - 50, S - 50], outline=color, width=16)
    draw.ellipse([85, 85, S - 85, S - 85], outline=color, width=6)
    draw.ellipse([180, 180, S - 180, S - 180], outline=color, width=6)

    # Draw New Custom Curved Text
    font_arc = load_font(48)
    font_center = load_font(75)

    if top_text:
        draw_curved_text_top(draw, top_text.upper(), cx, cy, radius=370, font=font_arc, fill=color)
    if bottom_text:
        draw_curved_text_bottom(draw, bottom_text.upper(), cx, cy, radius=370, font=font_arc, fill=color)
    if center_text and uploaded_file is None:
        draw.text((cx, cy), center_text.upper(), font=font_center, fill=color, anchor="mm")

    return canvas


# ==========================================
# 4. STREAMLIT APPLICATION CONTROLLER
# ==========================================

def main():
    st.set_page_config(page_title="Official Stamp Generator Studio", page_icon="🎨", layout="wide")
    st.title("Stamp Generator Studio")

    col_left, col_right = st.columns([1, 1])

    with col_left:
        app_mode = st.radio(
            "Select Generator Mode",
            ["📋 Preset Templates", "🖼️ Convert Sample Logo"],
            horizontal=True
        )

        st.markdown("---")

        if app_mode == "📋 Preset Templates":
            st.subheader("1. Choose Stamp Preset")
            stamp_key = st.selectbox(
                "Select Preset Template",
                options=list(STAMPS_DATABASE.keys()),
                format_func=lambda k: f"{k.upper()} — {STAMPS_DATABASE[k]['name']}"
            )
            
            spec = STAMPS_DATABASE[stamp_key]
            defaults = spec.get("defaults", {})

            st.subheader("2. Customize Text & Color")
            top_text, center_text, bottom_text = "", "", ""
            line1, line2 = "", ""

            if spec["text_type"] == "three_fields":
                top_text = st.text_input("Top Arc Text", defaults.get("top", ""))
                center_text = st.text_input("Center Text", defaults.get("center", ""))
                bottom_text = st.text_input("Bottom Arc Text", defaults.get("bottom", ""))
            elif spec["text_type"] == "two_lines_center":
                top_text = st.text_input("Outer Arc Text (Optional)", defaults.get("top", ""))
                c1, c2 = st.columns(2)
                with c1:
                    line1 = st.text_input("Center Line 1", defaults.get("line1", ""))
                with c2:
                    line2 = st.text_input("Center Line 2", defaults.get("line2", ""))

            color_hex = st.color_picker("Stamp Ink Color", spec["default_color"], key="cp_preset")

        else:
            st.subheader("1. Upload Reference Stamp or Logo")
            uploaded_logo = st.file_uploader("Upload PNG or JPG Image", type=["png", "jpg", "jpeg"])

            st.subheader("2. Customize Stamp Text")
            top_text_logo = st.text_input("Top Arc Text", "MY CUSTOM COMPANY", key="top_logo")
            center_text_logo = st.text_input("Center Text (Optional Override)", "", key="cnt_logo")
            bottom_text_logo = st.text_input("Bottom Arc Text", "EXPRESS DELIVERY", key="bot_logo")

            color_hex = st.color_picker("Stamp Ink Color", "#C2185B", key="cp_logo")
            
            st.subheader("3. Fine-Tune Extraction")
            c1, c2 = st.columns(2)
            with c1:
                crop_ratio = st.slider("Keep Center Icon Size", 0.15, 0.48, 0.35, help="Lower values erase more of the old outer text.")
            with c2:
                threshold_val = st.slider("Logo Contrast Threshold", 50, 255, 200)

        st.subheader("4. Realism & Effects")
        grunge_level = st.slider("Ink Wear / Grunge Effect", 0.0, 1.0, 0.15, step=0.05)

    with col_right:
        st.subheader("Live High-Res Preview")

        if app_mode == "🖼️ Convert Sample Logo":
            img = render_logo_to_stamp(
                uploaded_logo, 
                top_text_logo, 
                center_text_logo, 
                bottom_text_logo, 
                color_hex,
                threshold_val=threshold_val,
                crop_ratio=crop_ratio
            )
        else:
            family = spec["family"]
            if family == "ribbon_circle":
                img = render_ribbon_circle(spec, top_text, line1, line2, color_hex)
            elif family == "circular_box":
                img = render_circular_box(spec, top_text, center_text, bottom_text, color_hex)
            elif family == "rectangle":
                img = render_rectangle(spec, line1, line2, color_hex)
            else:
                img = render_circular_box(spec, top_text, center_text, bottom_text, color_hex)

        if grunge_level > 0:
            img = apply_grunge_texture(img, intensity=grunge_level)

        st.image(img, use_container_width=True)

        buf = io.BytesIO()
        img.save(buf, format="PNG", dpi=(300, 300))
        st.download_button(
            label="💾 Download High-Res PNG (300 DPI)",
            data=buf.getvalue(),
            file_name="custom_stamp_replaced_text.png",
            mime="image/png"
        )


if __name__ == "__main__":
    main()