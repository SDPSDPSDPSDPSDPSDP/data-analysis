from ..config import TextColors


def get_luminance(hex_color: str) -> float:
    """Calculate the relative luminance of a hex color.
    
    Uses the formula from WCAG 2.0:
    https://www.w3.org/TR/WCAG20/#relativeluminancedef
    
    Args:
        hex_color: Hex color string (with or without '#')
        
    Returns:
        Relative luminance value between 0 (darkest) and 1 (lightest)
    """
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
    """Determine optimal text color (white or black) based on background color.
    
    Uses WCAG 2.0 contrast ratio guidelines.
    Returns white text for dark backgrounds, black text for light backgrounds.
    
    Args:
        bg_color: Background hex color string
        
    Returns:
        Text color (TextColors.WHITE or TextColors.BLACK)
    """
    luminance = get_luminance(bg_color)
    # Threshold of 0.179 is the WCAG standard for proper contrast
    # Higher luminance = lighter color -> use black text
    # Lower luminance = darker color -> use white text
    return TextColors.WHITE if luminance < 0.179 else TextColors.BLACK
