"""SVG generation for event graphics."""

import logging
from pathlib import Path
from typing import Any
import svg
from svg import SVG, Image, Text, Rect

logger = logging.getLogger(__name__)

# Constants
TEXT_COLOUR = "#FFFFFF"  # White text colour


def parse_date_without_time(date_str: str) -> str:
    """
    Parse date string and return only the date part (remove time if present).
    
    Args:
        date_str: Date string that may include time
        
    Returns:
        Date string without time component
    """
    if not date_str:
        return date_str
    
    # Common patterns that include time
    time_patterns = ['T', ' at ', ' @ ']
    for pattern in time_patterns:
        if pattern in date_str:
            date_str = date_str.split(pattern)[0]
            break
    
    return date_str.strip()


def generate_svg(event_data: dict[str, Any], logo_path: str = "files/APS logo-black.svg") -> SVG:
    """
    Generate an SVG graphic for a single event.
    
    The SVG includes:
    - APS logo in the top-left corner
    - "Palaeo Events!" header text (centered horizontally)
    - Event details (title, subtitle, host, date, location) centered on the page
    
    Args:
        event_data: Dictionary containing event information. May include:
            - title (str, optional): Event title
            - subtitle (str, optional): Event subtitle
            - date (str, optional): Event date
            - host (str, optional): Event host
            - location (str, optional): Event location
        logo_path: Path to the APS logo SVG file
        
    Returns:
        SVG element representing the event graphic
        
    Raises:
        FileNotFoundError: If the logo file doesn't exist
        
    Example:
        >>> event = {
        ...     "title": "Fossil Discovery",
        ...     "subtitle": "Monthly Meeting",
        ...     "date": "January 15, 2025",
        ...     "host": "Dr. Smith",
        ...     "location": "Calgary, AB"
        ... }
        >>> svg_content = generate_svg(event)
        >>> isinstance(svg_content, SVG)
        True
    """
    event_title = event_data.get('title', 'Unknown')
    logger.debug(f"Generating SVG structure for event: {event_title}")
    
    # Validate logo file exists
    if not Path(logo_path).exists():
        logger.warning(f"Logo file not found: {logo_path}. Continuing without logo.")
    
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
    
    # Add logo in top left
    logo = Image(
        href=logo_path,
        x=logo_padding,
        y=logo_padding,
        width=logo_size,
        height=logo_size,
        preserveAspectRatio="xMidYMid meet"
    )
    elements.append(logo)
    
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
    
    # Date (doubled: 20 -> 40, no label) - remove time if present
    if (date := event_data.get('date')):
        date_without_time = parse_date_without_time(date)
        content_elements.append({
            'text': date_without_time,
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

