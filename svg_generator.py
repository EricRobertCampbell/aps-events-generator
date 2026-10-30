"""SVG generation for event graphics."""

import logging
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any
from svg import SVG, Text, Rect
from dates import format_event_when, format_registration_deadline

logger = logging.getLogger(__name__)

# Constants
TEXT_COLOUR = "#FFFFFF"  # White text colour
_DEFAULT_LOGO = Path(__file__).resolve().parent / "files" / "APS logo-black.svg"
_LOGO_ID_PREFIX = "aps-logo-"
_EDITOR_NAMESPACES = {
    "http://www.inkscape.org/namespaces/inkscape",
    "http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd",
}


def generate_svg(
    event_data: dict[str, Any],
    logo_path: str | Path | None = None,
) -> SVG:
    """
    Generate an SVG graphic for a single event.
    
    The SVG includes:
    - APS logo in the top-left corner
    - "Palaeo Events!" header text (centered horizontally)
    - Event details (title, subtitle, host, date, location) centered on the page
    - Registration deadline, when the event includes one, below those details
    
    Args:
        event_data: Dictionary containing event information. May include:
            - title (str, optional): Event title
            - subtitle (str, optional): Event subtitle
            - start (str, optional): ISO datetime with offset
            - end (str, optional): ISO datetime with offset
            - startDate (str, optional): Date-only start, YYYY-MM-DD
            - endDate (str, optional): Date-only end, YYYY-MM-DD
            - host (str, optional): Event host
            - location (str, optional): Event location
            - registrationDeadline (str, optional): ``YYYY-MM-DD`` or an ISO
              datetime with an offset
        logo_path: Path to the APS logo SVG file. Defaults to the logo
            shipped with this project.
        
    Returns:
        SVG element representing the event graphic. The logo artwork is
        inlined, so the file does not depend on an external logo path.
        
    Example:
        >>> event = {
        ...     "title": "Fossil Discovery",
        ...     "subtitle": "Monthly Meeting",
        ...     "start": "2026-01-03T16:00:00-07:00",
        ...     "end": "2026-01-03T17:00:00-07:00",
        ...     "host": "Dr. Smith",
        ...     "location": "Calgary, AB"
        ... }
        >>> svg_content = generate_svg(event)
        >>> isinstance(svg_content, SVG)
        True
    """
    event_title = event_data.get('title', 'Unknown')
    logger.debug(f"Generating SVG structure for event: {event_title}")
    
    resolved_logo = Path(logo_path) if logo_path is not None else _DEFAULT_LOGO
    if not resolved_logo.exists():
        logger.warning(f"Logo file not found: {resolved_logo}. Continuing without logo.")
    
    # SVG dimensions
    width = 1024
    height = 1024
    
    # Logo dimensions (from the SVG viewBox: 0 0 166 166)
    logo_size = 120
    logo_padding = 40
    
    elements = []
    
    # Add black background
    background = Rect(
        x=0,
        y=0,
        width=width,
        height=height,
        fill="#000000"
    )
    elements.append(background)
    
    # Add logo in top left, inlined so the SVG stays valid when moved
    if resolved_logo.exists():
        logo_markup = _embed_logo_markup(
            resolved_logo,
            x=logo_padding,
            y=logo_padding,
            size=logo_size,
        )
        elements.append(_RawMarkup(logo_markup))
    
    # Add "Palaeo Events!" text horizontally centered, vertically aligned with logo
    events_text = Text(
        x=width / 2,
        y=logo_padding + logo_size / 2,
        text="Palaeo Events!",
        font_size=64,  # Reduced by a third from 96
        font_weight="bold",
        fill=TEXT_COLOUR,
        text_anchor="middle",
        dominant_baseline="middle"
    )
    elements.append(events_text)
    
    # Collect content text elements and calculate total height for centering
    content_elements = []
    line_height_multiplier = 1.2  # Spacing between lines
    current_y_offset = 0
    
    # Title (doubled: 36 -> 72)
    if (title := event_data.get('title')):
        content_elements.append({
            'text': title,
            'font_size': 72,
            'font_weight': 'bold',
            'fill': TEXT_COLOUR,
            'y_offset': current_y_offset
        })
        current_y_offset += 72 * line_height_multiplier
    
    # Subtitle (doubled: 24 -> 48)
    if (subtitle := event_data.get('subtitle')):
        content_elements.append({
            'text': subtitle,
            'font_size': 48,
            'font_weight': None,
            'fill': TEXT_COLOUR,
            'y_offset': current_y_offset
        })
        current_y_offset += 48 * line_height_multiplier
    
    # Host (doubled: 20 -> 40, no label)
    if (host := event_data.get('host')):
        content_elements.append({
            'text': host,
            'font_size': 40,
            'font_weight': None,
            'fill': TEXT_COLOUR,
            'y_offset': current_y_offset
        })
        current_y_offset += 40 * line_height_multiplier
    
    # Date (doubled: 20 -> 40, no label)
    if (when := format_event_when(event_data)):
        content_elements.append({
            'text': when,
            'font_size': 40,
            'font_weight': None,
            'fill': TEXT_COLOUR,
            'y_offset': current_y_offset
        })
        current_y_offset += 40 * line_height_multiplier
    
    # Location (doubled: 20 -> 40, no label)
    if (location := event_data.get('location')):
        content_elements.append({
            'text': location,
            'font_size': 40,
            'font_weight': None,
            'fill': TEXT_COLOUR,
            'y_offset': current_y_offset
        })
        current_y_offset += 40 * line_height_multiplier

    # Registration deadline sits below every other line
    if (deadline := format_registration_deadline(event_data)):
        content_elements.append({
            'text': deadline,
            'font_size': 32,
            'font_weight': None,
            'fill': TEXT_COLOUR,
            'y_offset': current_y_offset
        })
        current_y_offset += 32 * line_height_multiplier
    
    # Calculate center position for the content group
    content_x = width / 2
    total_content_height = current_y_offset
    content_start_y = (height - total_content_height) / 2
    
    # Add content elements centered vertically and horizontally
    for elem_data in content_elements:
        text_elem = Text(
            x=content_x,
            y=content_start_y + elem_data['y_offset'],
            text=elem_data['text'],
            font_size=elem_data['font_size'],
            fill=elem_data['fill'],
            text_anchor="middle",
            text_rendering="optimizeLegibility",
            font_weight=elem_data.get('font_weight')
        )
        elements.append(text_elem)
    
    # Create the main SVG element
    svg_element = SVG(
        width=width,
        height=height,
        viewBox=f"0 0 {width} {height}",
        elements=elements
    )
    
    return svg_element


class _RawMarkup:
    """SVG fragment inserted verbatim.

    ``svg.py`` stringifies children that are not ``Element`` instances, so this
    object's markup is written into the parent document unchanged.
    """

    def __init__(self, markup: str) -> None:
        self.markup = markup

    def __str__(self) -> str:
        return self.markup


def _embed_logo_markup(logo_path: Path, x: int, y: int, size: int) -> str:
    """
    Inline the logo artwork as a nested SVG.

    Editor metadata is dropped. Ids and class names are prefixed so they do
    not collide if this graphic is pasted into another SVG.
    """
    root = ET.parse(logo_path).getroot()
    inner = ET.Element("svg")
    inner.set("x", str(x))
    inner.set("y", str(y))
    inner.set("width", str(size))
    inner.set("height", str(size))
    inner.set("viewBox", "0 0 166 166")
    for child in list(root):
        cleaned = _clean_logo_element(child)
        if cleaned is not None:
            inner.append(cleaned)
    return ET.tostring(inner, encoding="unicode")


def _clean_logo_element(element: ET.Element) -> ET.Element | None:
    """Copy an element without Inkscape or sodipodi metadata, prefixing ids."""
    if _clark_namespace(element.tag) in _EDITOR_NAMESPACES:
        return None

    cleaned = ET.Element(_local_name(element.tag))
    for key, value in element.attrib.items():
        if _clark_namespace(key) in _EDITOR_NAMESPACES:
            continue
        name = _local_name(key)
        if name == "id":
            value = _prefix_token(value)
        elif name == "class":
            value = " ".join(_prefix_token(part) for part in value.split() if part)
        elif name == "style":
            value = _rewrite_fragment_urls(value)
        cleaned.set(name, value)

    if _local_name(element.tag) == "style" and element.text:
        cleaned.text = _rewrite_css_classes(_rewrite_fragment_urls(element.text))
    else:
        cleaned.text = element.text

    for child in list(element):
        cleaned_child = _clean_logo_element(child)
        if cleaned_child is not None:
            cleaned.append(cleaned_child)
    return cleaned


def _prefix_token(token: str) -> str:
    """Prefix an id or class name once."""
    if token.startswith(_LOGO_ID_PREFIX):
        return token
    return f"{_LOGO_ID_PREFIX}{token}"


def _rewrite_fragment_urls(value: str) -> str:
    """Point ``url(#id)`` references at the prefixed id."""
    return re.sub(
        r"url\(\s*#([^)]+?)\s*\)",
        lambda match: f"url(#{_prefix_token(match.group(1))})",
        value,
    )


def _rewrite_css_classes(css: str) -> str:
    """Prefix class selectors in a style block."""
    return re.sub(
        r"\.([A-Za-z_][\w-]*)",
        lambda match: f".{_prefix_token(match.group(1))}",
        css,
    )


def _clark_namespace(name: str) -> str | None:
    """Return the namespace URI from a Clark notation name, if any."""
    if name.startswith("{"):
        return name[1:].split("}", 1)[0]
    return None


def _local_name(name: str) -> str:
    """Return the local part of a Clark notation name."""
    if name.startswith("{"):
        return name.split("}", 1)[1]
    return name

