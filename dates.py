"""Compact date and time formatting for APS event graphics."""

from datetime import datetime
from typing import Any


def format_event_when(event: dict[str, Any]) -> str:
    """
    Format an event's start and end as a short date and time.

    Timed events use ``start`` and ``end`` (ISO datetimes, offset included).
    Date-only events use ``startDate`` and ``endDate`` (``YYYY-MM-DD``).
    The clock time in the string is kept as written; it is not shifted into
    the machine's timezone. The year is omitted.

    Args:
        event: Event dictionary from the API. May include ``start``, ``end``,
            ``startDate``, and ``endDate``.

    Returns:
        A compact date string, or an empty string when no date is present.

    Example:
        >>> format_event_when({
        ...     "start": "2026-01-03T16:00:00-07:00",
        ...     "end": "2026-01-03T17:00:00-07:00",
        ... })
        'January 3, 4 - 5pm'
        >>> format_event_when({
        ...     "start": "2026-01-03T10:00:00-07:00",
        ...     "end": "2026-01-03T13:00:00-07:00",
        ... })
        'January 3, 10am - 1pm'
        >>> format_event_when({"start": "2026-01-03T19:30:00-07:00"})
        'January 3, 7:30pm'
        >>> format_event_when({
        ...     "start": "2026-01-16T19:30:00-07:00",
        ...     "end": "2026-01-16T21:00:00-07:00",
        ... })
        'January 16, 7:30 - 9pm'
        >>> format_event_when({"start": "2026-01-03T23:30:00-07:00"})
        'January 3, 11:30pm'
        >>> format_event_when({"startDate": "2026-01-03"})
        'January 3'
        >>> format_event_when({
        ...     "startDate": "2026-01-03",
        ...     "endDate": "2026-01-05",
        ... })
        'January 3 - 5'
        >>> format_event_when({
        ...     "startDate": "2026-01-30",
        ...     "endDate": "2026-02-02",
        ... })
        'January 30 - February 2'
        >>> format_event_when({
        ...     "start": "2026-01-03T16:00:00-07:00",
        ...     "end": "2026-01-05T14:00:00-07:00",
        ... })
        'January 3, 4pm - January 5, 2pm'
        >>> format_event_when({})
        ''
    """
    start_raw = _text(event.get("start"))
    end_raw = _text(event.get("end"))
    if start_raw or end_raw:
        start = _parse_iso(start_raw) if start_raw else None
        end = _parse_iso(end_raw) if end_raw else None
        return _format_range(start, end, timed=True)

    start = _parse_iso(_text(event.get("startDate")))
    end = _parse_iso(_text(event.get("endDate")))
    if start is None and end is None:
        return ""
    return _format_range(start, end, timed=False)


def event_weekday(event: dict[str, Any]) -> str:
    """
    Return the weekday name for an event's start, in the event's own offset.

    Args:
        event: Event dictionary from the API.

    Returns:
        A full weekday name, or an empty string when no date is present.

    Example:
        >>> event_weekday({"start": "2026-01-03T16:00:00-07:00"})
        'Saturday'
        >>> event_weekday({"startDate": "2026-01-03"})
        'Saturday'
        >>> event_weekday({})
        ''
    """
    start = _event_start(event)
    if start is None:
        return ""
    return start.strftime("%A")


def _event_start(event: dict[str, Any]) -> datetime | None:
    """Return the event start, preferring a timed start over a date-only start."""
    for key in ("start", "startDate", "end", "endDate"):
        parsed = _parse_iso(_text(event.get(key)))
        if parsed is not None:
            return parsed
    return None


def _format_range(start: datetime | None, end: datetime | None, timed: bool) -> str:
    """Format a start/end pair. ``timed`` controls whether clock times are shown."""
    if start is None and end is None:
        return ""
    if start is None:
        start = end
        end = None
    if start is None:
        return ""
    if end is None or _same_point(start, end, timed):
        if timed:
            return f"{_month_day(start)}, {_format_time(start, include_meridiem=True)}"
        return _month_day(start)

    if timed and start.date() == end.date():
        same_meridiem = _meridiem(start) == _meridiem(end)
        start_time = _format_time(start, include_meridiem=not same_meridiem)
        end_time = _format_time(end, include_meridiem=True)
        return f"{_month_day(start)}, {start_time} - {end_time}"

    if timed:
        start_time = _format_time(start, include_meridiem=True)
        end_time = _format_time(end, include_meridiem=True)
        return f"{_month_day(start)}, {start_time} - {_month_day(end)}, {end_time}"

    if start.year == end.year and start.month == end.month:
        return f"{_month_name(start)} {start.day} - {end.day}"
    return f"{_month_day(start)} - {_month_day(end)}"


def _same_point(start: datetime, end: datetime, timed: bool) -> bool:
    """True when the end does not add another day or another clock time."""
    if start.date() != end.date():
        return False
    if not timed:
        return True
    return (start.hour, start.minute) == (end.hour, end.minute)


def _format_time(moment: datetime, include_meridiem: bool) -> str:
    """Format a clock time as ``4``, ``4pm``, or ``7:30pm``."""
    hour12 = moment.hour % 12
    if hour12 == 0:
        hour12 = 12
    if moment.minute == 0:
        clock = f"{hour12}"
    else:
        clock = f"{hour12}:{moment.minute:02d}"
    if include_meridiem:
        return f"{clock}{_meridiem(moment)}"
    return clock


def _meridiem(moment: datetime) -> str:
    """Return ``am`` or ``pm`` for a clock time."""
    if moment.hour < 12:
        return "am"
    return "pm"


def _month_day(moment: datetime) -> str:
    """Format a calendar day as ``January 3``, without the year."""
    return f"{_month_name(moment)} {moment.day}"


def _month_name(moment: datetime) -> str:
    """Return the full English month name."""
    return moment.strftime("%B")


def _parse_iso(value: str) -> datetime | None:
    """Parse an ISO date or datetime, preserving its offset."""
    if not value:
        return None
    return datetime.fromisoformat(value)


def _text(value: Any) -> str:
    """Return a stripped string, or an empty string for missing values."""
    if not isinstance(value, str):
        return ""
    return value.strip()
