"""
icons.py — tiny inline-SVG icon set for CAMPUSX AI.

Replaces emoji glyphs with crisp, theme-colored SVGs that inherit
`currentColor`, so they scale and recolor cleanly inside Streamlit's
markdown/HTML blocks. Each icon is a small hand-built composition
(stroke-based "line icon" style) — no external assets required.
"""

_STROKE_ICONS = {
    # simple activity / pulse mark used as the CAMPUSX logomark
    "logo": '<polyline points="2,13 6,13 9,4 13,20 16,13 22,13"/>',

    "refresh": (
        '<path d="M3 9a9 9 0 0 1 15-5.5L21 6"/>'
        '<path d="M21 6V2M21 6h-4"/>'
        '<path d="M21 15a9 9 0 0 1-15 5.5L3 18"/>'
        '<path d="M3 18v4M3 18h4"/>'
    ),

    "alert": (
        '<path d="M12 3 22 20H2Z" stroke-linejoin="round"/>'
        '<line x1="12" y1="10" x2="12" y2="14.5"/>'
        '<circle cx="12" cy="17.3" r="0.6" fill="currentColor" stroke="none"/>'
    ),

    "map": (
        '<polygon points="3,6 9,4 15,6 21,4 21,18 15,20 9,18 3,20" stroke-linejoin="round"/>'
        '<line x1="9" y1="4" x2="9" y2="18"/>'
        '<line x1="15" y1="6" x2="15" y2="20"/>'
    ),

    "pin": (
        '<path d="M12 2a7 7 0 0 0-7 7c0 5.2 7 13 7 13s7-7.8 7-13a7 7 0 0 0-7-7Z" stroke-linejoin="round"/>'
        '<circle cx="12" cy="9" r="2.4"/>'
    ),

    "building": (
        '<rect x="4" y="3" width="10" height="18" rx="1"/>'
        '<rect x="14" y="9" width="6" height="12" rx="1"/>'
        '<line x1="7" y1="7" x2="7" y2="7.01"/>'
        '<line x1="11" y1="7" x2="11" y2="7.01"/>'
        '<line x1="7" y1="11" x2="7" y2="11.01"/>'
        '<line x1="11" y1="11" x2="11" y2="11.01"/>'
        '<line x1="7" y1="15" x2="7" y2="15.01"/>'
        '<line x1="11" y1="15" x2="11" y2="15.01"/>'
    ),

    "person": (
        '<circle cx="12" cy="7.5" r="3.8"/>'
        '<path d="M4.5 21c0-4.1 3.4-7.3 7.5-7.3s7.5 3.2 7.5 7.3"/>'
    ),

    "thermometer": (
        '<path d="M12 3.5a2 2 0 0 0-2 2v8.7a4 4 0 1 0 4 0V5.5a2 2 0 0 0-2-2Z"/>'
        '<line x1="12" y1="7" x2="12" y2="14"/>'
    ),

    "check": (
        '<circle cx="12" cy="12" r="9.5"/>'
        '<polyline points="7.5,12.3 10.5,15.3 16.5,8.7"/>'
    ),

    "cpu": (
        '<rect x="7" y="7" width="10" height="10" rx="1.5"/>'
        '<rect x="10" y="10" width="4" height="4"/>'
        '<line x1="12" y1="2" x2="12" y2="5"/>'
        '<line x1="12" y1="19" x2="12" y2="22"/>'
        '<line x1="2" y1="12" x2="5" y2="12"/>'
        '<line x1="19" y1="12" x2="22" y2="12"/>'
        '<line x1="4.5" y1="4.5" x2="6.5" y2="6.5"/>'
        '<line x1="17.5" y1="17.5" x2="19.5" y2="19.5"/>'
        '<line x1="4.5" y1="19.5" x2="6.5" y2="17.5"/>'
        '<line x1="17.5" y1="6.5" x2="19.5" y2="4.5"/>'
    ),

    "trend": (
        '<polyline points="3,17 9,11 13,15 21,6"/>'
        '<polyline points="15,6 21,6 21,12"/>'
    ),

    "droplet": (
        '<path d="M12 2.5s7 8.2 7 13a7 7 0 0 1-14 0c0-4.8 7-13 7-13Z" stroke-linejoin="round"/>'
    ),

    "gear": (
        '<circle cx="12" cy="12" r="3"/>'
        '<path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.6 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.6a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1Z"/>'
    ),

    "lock": (
        '<rect x="5" y="11" width="14" height="10" rx="2"/>'
        '<path d="M8 11V7a4 4 0 0 1 8 0v4"/>'
    ),

    "history": (
        '<path d="M3 12a9 9 0 1 0 3-6.7"/>'
        '<path d="M3 4v5h5"/>'
        '<path d="M12 7v5l4 2"/>'
    ),

    "leaf": (
        '<path d="M20 4c-9.5 0-16 6-16 14.5" stroke-linecap="round"/>'
        '<path d="M20 4c0 9.5-6 16-14.5 16C4.7 12.7 10.7 4.7 20 4Z" stroke-linejoin="round"/>'
    ),

    "coin": (
        '<circle cx="12" cy="12" r="9"/>'
        '<path d="M9.2 15.3c.5.9 1.5 1.5 2.8 1.5 1.8 0 3-1 3-2.3 0-1.4-1.2-1.9-3-2.3-1.8-.4-3-1-3-2.3 0-1.3 1.2-2.3 3-2.3 1.3 0 2.3.6 2.8 1.5"/>'
        '<line x1="12" y1="6.3" x2="12" y2="7.6"/>'
        '<line x1="12" y1="16.4" x2="12" y2="17.7"/>'
    ),
}

_FILLED_ICONS = {
    "dot": '<circle cx="12" cy="12" r="9" fill="{color}" stroke="none"/>',
    "bolt": (
        '<polygon points="13,2 4,14 11,14 9,22 20,10 13,10" '
        'fill="{color}" stroke="none" stroke-linejoin="round"/>'
    ),
}


def icon(name: str, size: int = 16, color: str = "currentColor", stroke_width: float = 2.0) -> str:
    """Return an inline <svg> string for the named icon."""
    if name in _FILLED_ICONS:
        body = _FILLED_ICONS[name].format(color=color)
        return (
            f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" '
            f'xmlns="http://www.w3.org/2000/svg" style="display:inline-block;vertical-align:middle">'
            f'{body}</svg>'
        )
    body = _STROKE_ICONS.get(name, "")
    return (
        f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
        f'stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round" '
        f'xmlns="http://www.w3.org/2000/svg" style="display:inline-block;vertical-align:middle">'
        f'{body}</svg>'
    )


def status_icon(state: str, size: int = 14) -> str:
    """Colored status dot for 'normal' | 'warning' | 'critical'."""
    colors = {"normal": "#22c55e", "warning": "#eab308", "critical": "#f85149"}
    return icon("dot", size=size, color=colors.get(state, "#8b949e"))
