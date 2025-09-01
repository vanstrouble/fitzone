# Global color palettes
COLOR_PALETTES = {
    "midnight_violet": {
        "primary": ("#944388", "#7a3671"),
        "accent": ("#ECA66C", "#d99558"),
        "danger": ("#D45276", "#b83d60"),
        "neutral_bg": ("#f0f0f0", "#2a2a2a"),
        "neutral_fg": ("#e0e0e0", "#3a3a3a"),
        "text_primary": ("#303030", "#e0e0e0"),
        "text_secondary": ("#707070", "#a0a0a0"),
    },
    "ocean_breeze": {
        "primary": ("#215273", "#19405A"),
        "secondary": ("#359D9E", "#2A7E7F"),
        "accent": ("#55C595", "#47A67D"),
        "highlight": ("#7CE495", "#65B879"),
        "neutral": ("#CFF4D1", "#B8DCBA"),
        "danger": ("#215273", "#19405A"),
        "neutral_bg": ("#F2FFFA", "#1E3A45"),
        "neutral_fg": ("#E0F5ED", "#244550"),
        "text_primary": ("#1E3A45", "#F2FFFA"),
        "text_secondary": ("#4A7684", "#A5C4C4"),
    }
}

# Current active palette (default to midnight_violet)
_current_palette = "midnight_violet"


def get_current_palette():
    """Get the name of the current active palette"""
    return _current_palette


def set_palette(palette_name):
    """Set the active color palette"""
    global _current_palette
    if palette_name in COLOR_PALETTES:
        _current_palette = palette_name
        return True
    return False


def get_palette_names():
    """Get list of available palette names"""
    return list(COLOR_PALETTES.keys())


# Dynamic COLORS dictionary that returns the current palette
class ColorProxy:
    def __getitem__(self, key):
        return COLOR_PALETTES[_current_palette][key]

    def __contains__(self, key):
        return key in COLOR_PALETTES[_current_palette]

    def get(self, key, default=None):
        return COLOR_PALETTES[_current_palette].get(key, default)

    def keys(self):
        return COLOR_PALETTES[_current_palette].keys()

    def items(self):
        return COLOR_PALETTES[_current_palette].items()


# Export the proxy as COLORS for backward compatibility
COLORS = ColorProxy()
