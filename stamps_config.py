# stamps_config.py

STAMPS_DATABASE = {
    # Unique Stamp #1
    "stamp_001": {
        "title": "First Class Angled Ribbon",
        "family": "ribbon_circle",
        "color": "#2B3A4A",
        "outer_border": "thick_ring",
        "inner_border": "cogwheel",
        "ribbon_style": "notched_tails",
        "tilt_angle": -12,
        "text_fields": ["top_arc", "line1", "line2"]
    },
    
    # Unique Stamp #2
    "stamp_002": {
        "title": "100% Recycled Hexagon",
        "family": "polygon",
        "color": "#2E7D32",
        "sides": 6,  # Hexagon
        "outer_border": "double_line",
        "inner_border": "none",
        "ribbon_style": "none",
        "tilt_angle": 15,
        "text_fields": ["top_line", "center_bold", "bottom_line"]
    },

    # Unique Stamp #3
    "stamp_003": {
        "title": "Best Buy Center Box",
        "family": "circular_box",
        "color": "#8E24AA",
        "outer_border": "dotted_ring",
        "inner_border": "solid",
        "has_center_rectangle": True,
        "tilt_angle": 0,
        "text_fields": ["top_arc", "center_box", "bottom_arc"]
    }
    
    # ... Continue defining stamp_004 to stamp_100
}