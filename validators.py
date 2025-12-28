"""Validation functions for dates and API responses."""

import logging
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


def validate_date_format(date_str: str) -> str:
    """
    Validate that a date string is in YYYY-MM-DD format.
    
    Args:
        date_str: Date string to validate
        
    Returns:
        The validated date string
        
    Raises:
        ValueError: If the date format is invalid
        
    Example:
        >>> validate_date_format("2025-01-15")
        '2025-01-15'
        >>> validate_date_format("01/15/2025")
        ValueError: Invalid date format: 01/15/2025. Expected YYYY-MM-DD
    """
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return date_str
    except ValueError as e:
        raise ValueError(
            f"Invalid date format: {date_str}. Expected YYYY-MM-DD format (e.g., 2025-01-15)"
        ) from e


def validate_date_range(start_date: str, end_date: str) -> tuple[str, str]:
    """
    Validate that start_date is before or equal to end_date.
    
    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        
    Returns:
        Tuple of (start_date, end_date) as validated strings
        
    Raises:
        ValueError: If start_date is after end_date
        
    Example:
        >>> validate_date_range("2025-01-15", "2025-01-20")
        ('2025-01-15', '2025-01-20')
        >>> validate_date_range("2025-01-20", "2025-01-15")
        ValueError: Start date (2025-01-20) must be before or equal to end date (2025-01-15)
    """
    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
    end_dt = datetime.strptime(end_date, '%Y-%m-%d')
    
    if start_dt > end_dt:
        raise ValueError(
            f"Start date ({start_date}) must be before or equal to end date ({end_date})"
        )
    
    return start_date, end_date


def validate_api_response(response_data: Any) -> list[dict[str, Any]]:
    """
    Validate that the API response is a list of event dictionaries.
    
    Args:
        response_data: The JSON response from the API
        
    Returns:
        List of validated event dictionaries
        
    Raises:
        ValueError: If the response structure is invalid
        
    Example:
        >>> validate_api_response([{"title": "Event"}])
        [{'title': 'Event'}]
        >>> validate_api_response({"events": []})
        ValueError: API response must be a list, got dict
    """
    if not isinstance(response_data, list):
        raise ValueError(
            f"API response must be a list of events, got {type(response_data).__name__}. Please check the API endpoint and response format."
        )
    
    validated_events = []
    for i, event in enumerate(response_data):
        if not isinstance(event, dict):
            raise ValueError(
                f"Event at index {i} must be a dictionary, got {type(event).__name__}. Please check the API response format."
            )
        validated_events.append(event)
    
    logger.debug(f"Validated {len(validated_events)} event(s) from API response")
    return validated_events

