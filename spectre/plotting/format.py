from dataclasses import dataclass

@dataclass
class PanelFormat:
    small_size: int = 18
    medium_size: int = 21
    large_size: int = 24
    line_width: int = 3
    style: str = "dark_background"


DEFAULT_PANEL_FORMAT = PanelFormat()