import io
import math
import random
import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# Try importing cairosvg for high-res SVG template rendering
try:
    import cairosvg
    CAIROSVG_AVAILABLE = True
except ImportError:
    CAIROSVG_AVAILABLE = False


# ==========================================
# 1. DATABASE / CONFIGURATION (100 STAMPS MAP)
# ==========================================
# Instead of 10,000 lines of code, all 100 unique stamps are defined here.
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
        "sides": 24, # Sawtooth teeth count
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
    },
    # ------------------------------------------------------------------
    # Example for complex unique stamps using custom SVG background base
    # ------------------------------------------------------------------
    "stamp_005": {
        "name": "Custom Vector Crest / Tool Badge",
        "family": "svg_overlay",
        "svg_file": "templates/stamp_005.svg", # Path to SVG base image
        "default_color": "#1A237E",
        "text_type": "three_fields",
        "defaults": {
            "top": "HAND MADE",
            "center": "QUALITY",
            "bottom": "CRAFTED"
        }
    }
    # ... Populate up to stamp_100 following this exact dictionary structure
}


# ==========================================
# 2. HELPER UTILITIES & RENDERERS
# ==========================================

def hex_to_rgba(hex_str, alpha=255):
    """Converts hex color code string to RGBA tuple."""
    hex_str = hex_str.lstrip('#')
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4)) + (alpha,)


def load_font(size):
    """Loads a high-impact bold font, falling back to default PIL font."""
    font_candidates = ["impact.ttf", "arialbd.ttf", "DejaVuSans-Bold.ttf"]
    for font_name in font_candidates:
        try:
            return ImageFont.truetype(font_name, size)
        except IOError:
            continue
    return ImageFont.load_default()


def apply_grunge_texture(img, intensity=0.3):
    """Applies realistic worn-out rubber stamp ink erosion texture."""
    if intensity <= 0:
        return img
    
    noise = Image.new("L", img.size, 255)
    draw_noise = ImageDraw.Draw(noise)
    num_specks = int(img.width * img.height * 0.004 * intensity)
    
    for _ in range(num_specks):
        x = random.randint(0, img.width)
        y = random.randint(0, img.height)
        r = random.randint(1, 3)
        draw_noise.ellipse([x-r, y-r, x+r, y+r], fill=random.randint(40, 160))

    r, g, b, a = img.split()
    a_masked = Image.composite(a, Image.eval(noise, lambda p: 255 - p), a)
    return Image.merge("RGBA", (r, g, b, a_masked))


# ==========================================
# 3. CORE FAMILY RENDERING ENGINES
# ==========================================

def render_ribbon_circle(spec, top_text, line1, line2, color_hex):
    """Engine for Angled Ribbon & Circle Stamp layouts."""
    S = 1000
    cx, cy = S // 2, S // 2
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    color = hex_to_rgba(color_hex)

    # 1. Draw Background Ribbon Tails
    left_tail = [(50, cy + 80), (180, cy - 100), (220, cy + 20)]
    right_tail = [(S - 50, cy - 80), (S - 180, cy + 100), (S - 220, cy - 20)]
    draw.polygon(left_tail, fill=color)
    draw.polygon(right_tail, fill=color)

    # 2. Outer Thick Circular Ring
    r_outer = 420
    ring_w = spec.get("outer_ring_width", 110)
    draw.ellipse([cx - r_outer, cy - r_outer, cx + r_outer, cy + r_outer], fill=color)

    # 3. Center Masking Cutout
    r_inner = r_outer - ring_w
    draw.ellipse([cx - r_inner, cy - r_inner, cx + r_inner, cy + r_inner], fill=(255, 255, 255, 255))

    # 4. Cogwheel Inner Border
    if spec.get("border_style") == "cogwheel":
        r_cog = r_inner - 15
        num_notches = 24
        for i in range(num_notches):
            a1 = math.radians(i * (360 / num_notches))
            a2 = math.radians((i + 0.5) * (360 / num_notches))
            x1, y1 = cx + r_cog * math.cos(a1), cy + r_cog * math.sin(a1)
            x2, y2 = cx + r_cog * math.cos(a2), cy + r_cog * math.sin(a2)
            draw.line([(x1, y1), (x2, y2)], fill=color, width=14)

    # 5. Center Text Stack
    font_main = load_font(120)
    draw.text((cx, cy - 55), line1.upper(), font=font_main, fill=color, anchor="mm")
    draw.text((cx, cy + 55), line2.upper(), font=font_main, fill=color, anchor="mm")

    # Apply Rotation / Tilt
    angle = spec.get("ribbon_angle", 0)
    if angle != 0:
        img = img.rotate(angle, resample=Image.BICUBIC, expand=False)

    return img


def render_circular_box(spec, top_text, center_text, bottom_text, color_hex):
    """Engine for Center Box Banner Stamp layouts."""
    S = 1000
    cx, cy = S // 2, S // 2
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    color = hex_to_rgba(color_hex)

    # Borders
    draw.ellipse([50, 50, S - 50, S - 50], outline=color, width=12)
    draw.ellipse([90, 90, S - 90, S - 90], outline=color, width=6)
    draw.ellipse([160, 160, S - 160, S - 160], outline=color, width=4)

    # Center Box Banner
    box_w, box_h = 820, 180
    box_rect = [cx - box_w//2, cy - box_h//2, cx + box_w//2, cy + box_h//2]
    draw.rectangle(box_rect, fill=(255, 255, 255, 255))
    draw.rectangle(box_rect, outline=color, width=12)

    # Center Text
    font_lg = load_font(100)
    draw.text((cx, cy), center_text.upper(), font=font_lg, fill=color, anchor="mm")

    return img


def render_rectangle(spec, line1, line2, color_hex):
    """Engine for Rectangular & Boxed Stamp layouts."""
    W, H = 1000, 600
    cx, cy = W // 2, H // 2
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    color = hex_to_rgba(color_hex)

    # Outer Double Borders
    draw.rounded_rectangle([30, 30, W - 30, H - 30], radius=35, outline=color, width=16)
    draw.rounded_rectangle([60, 60, W - 60, H - 60], radius=20, outline=color, width=6)

    # Text Lines
    font_main = load_font(110)
    draw.text((cx, cy - 60), line1.upper(), font=font_main, fill=color, anchor="mm")
    draw.text((cx, cy + 60), line2.upper(), font=font_main, fill=color, anchor="mm")

    return img


def render_svg_overlay(spec, top_text, center_text, bottom_text, color_hex):
    """Engine for SVG/PNG Background Overlay Stamp layouts."""
    if not CAIROSVG_AVAILABLE:
        # Fallback if CairoSVG is not installed on system
        img = Image.new("RGBA", (800, 800), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        draw.text((400, 400), "CairoSVG needed for SVG templates", anchor="mm", fill=(255, 0, 0, 255))
        return img

    svg_file = spec.get("svg_file")
    try:
        with open(svg_file, "r") as f:
            svg_content = f.read()
            
        svg_content = svg_content.replace("{{COLOR}}", color_hex)
        svg_content = svg_content.replace("{{TOP_TEXT}}", top_text)
        svg_content = svg_content.replace("{{CENTER_TEXT}}", center_text)
        svg_content = svg_content.replace("{{BOTTOM_TEXT}}", bottom_text)

        png_bytes = cairosvg.svg2png(bytestring=svg_content.encode('utf-8'), scale=3.0)
        return Image.open(io.BytesIO(png_bytes))
    except Exception as e:
        # Graceful fallback error rendering
        img = Image.new("RGBA", (800, 800), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        draw.text((400, 400), f"Template error: {e}", anchor="mm", fill=(255, 0, 0, 255))
        return img


# ==========================================
# 4. STREAMLIT APPLICATION CONTROLLER
# ==========================================

def main():
    st.set_page_config(page_title="Official Stamp Generator", page_icon="🎨", layout="wide")
    st.title("Stamp Generator Studio")

    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.subheader("1. Choose Stamp Design Preset")
        
        # Selectbox to pick from 100 stamps
        stamp_key = st.selectbox(
            "Select Preset Template",
            options=list(STAMPS_DATABASE.keys()),
            format_func=lambda k: f"{k.upper()} — {STAMPS_DATABASE[k]['name']}"
        )
        
        spec = STAMPS_DATABASE[stamp_key]
        defaults = spec.get("defaults", {})

        st.subheader("2. Customize Text & Color")
        
        # Dynamic text fields based on layout requirements
        top_text = ""
        center_text = ""
        bottom_text = ""
        line1, line2 = "", ""

        if spec["text_type"] == "three_fields":
            top_text = st.text_input("Top Arc / Header Text", defaults.get("top", ""))
            center_text = st.text_input("Center Text", defaults.get("center", ""))
            bottom_text = st.text_input("Bottom Arc / Footer Text", defaults.get("bottom", ""))
        elif spec["text_type"] == "two_lines_center":
            top_text = st.text_input("Outer Arc Text (Optional)", defaults.get("top", ""))
            c1, c2 = st.columns(2)
            with c1:
                line1 = st.text_input("Center Line 1", defaults.get("line1", ""))
            with c2:
                line2 = st.text_input("Center Line 2", defaults.get("line2", ""))

        color_hex = st.color_picker("Stamp Ink Color", spec["default_color"])
        
        st.subheader("3. Realism Effects")
        grunge_level = st.slider("Ink Wear / Grunge Effect", 0.0, 1.0, 0.2, step=0.05)

    with col_right:
        st.subheader("Live High-Res Preview")

        # MASTER ROUTER: Calls the appropriate rendering engine family
        family = spec["family"]
        
        if family == "ribbon_circle":
            img = render_ribbon_circle(spec, top_text, line1, line2, color_hex)
        elif family == "circular_box":
            img = render_circular_box(spec, top_text, center_text, bottom_text, color_hex)
        elif family == "rectangle":
            img = render_rectangle(spec, line1, line2, color_hex)
        elif family == "svg_overlay":
            img = render_svg_overlay(spec, top_text, center_text, bottom_text, color_hex)
        else:
            img = render_circular_box(spec, top_text, center_text, bottom_text, color_hex)

        # Apply Realism Effects
        if grunge_level > 0:
            img = apply_grunge_texture(img, intensity=grunge_level)

        # Display Live Preview Image
        st.image(img, use_container_width=True)

        # Download Button
        buf = io.BytesIO()
        img.save(buf, format="PNG", dpi=(300, 300))
        st.download_button(
            label="💾 Download High-Res PNG (300 DPI)",
            data=buf.getvalue(),
            file_name=f"{stamp_key}_custom.png",
            mime="image/png"
        )


if __name__ == "__main__":
    main()