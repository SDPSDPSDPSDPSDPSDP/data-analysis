from ...config import TextColors


def get_luminance(hex_color: str) -> float:
    # Remove '#' if present
    hex_color = hex_color.lstrip('#')
    
    # Convert to RGB
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    
    # Normalize to 0-1 range
    r, g, b = r / 255.0, g / 255.0, b / 255.0
    
    # Apply gamma correction
    def adjust(c):
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    
    r, g, b = adjust(r), adjust(g), adjust(b)
    
    # Calculate luminance
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def get_text_color_for_background(bg_color: str) -> str:
    luminance = get_luminance(bg_color)
    # Threshold of 0.179 is the WCAG standard for proper contrast
    # Higher luminance = lighter color -> use black text
    # Lower luminance = darker color -> use white text
    return TextColors.WHITE if luminance < 0.179 else TextColors.BLACK
