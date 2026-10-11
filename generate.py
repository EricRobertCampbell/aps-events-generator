#!/usr/bin/env python3
"""Main CLI entry point for generating SVG graphics from APS event data."""

import argparse
import logging
import sys
from pathlib import Path
from datetime import datetime, timedelta

from api_client import APIClient
from dates import event_weekday, format_event_when
from svg_generator import generate_svg
from validators import validate_date_format, validate_date_range, validate_api_response

# Default API base URL
# DEFAULT_BASE_URL = "http://localhost:4321"  # For local development
DEFAULT_BASE_URL = "https://albertapaleo.org"


def main() -> None:
    """
    Main entry point for the CLI.
    
    Parses command-line arguments, validates inputs, fetches event data,
    and generates SVG graphics for each event.
    """
    parser = argparse.ArgumentParser(
        description='Generate SVG graphics for APS weekly events',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate events for a week starting today
  python generate.py

  # Generate events for a week starting January 15th
  python generate.py 2025-01-15
  
  # Generate events for a specific date range
  python generate.py 2025-01-15 2025-01-20
  
  # Use custom output directory and API URL
  python generate.py 2025-01-15 --output-dir events --base-url https://albertapaleo.org
  
  # Preview without generating files
  python generate.py 2025-01-15 --dry-run
        """
    )
    
    parser.add_argument(
        'start_date',
        type=str,
        nargs='?',
        default=None,
        help='Start date in YYYY-MM-DD format (e.g., 2025-01-15). If omitted, defaults to today'
    )
    parser.add_argument(
        'end_date',
        type=str,
        nargs='?',
        default=None,
        help='End date in YYYY-MM-DD format. If omitted, defaults to 7 days after start_date'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default=None,
        help='Output directory for generated SVG files. Defaults to start_date (YYYY-MM-DD)'
    )
    parser.add_argument(
        '--base-url',
        type=str,
        default=DEFAULT_BASE_URL,
        help=f'Base URL for the API. Default: {DEFAULT_BASE_URL}'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging (DEBUG level)'
    )
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Suppress informational messages (WARNING level only)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview what would be generated without creating files'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(verbose=args.verbose, quiet=args.quiet)
    logger = logging.getLogger(__name__)
    
    logger.info("Starting SVG generation process")
    
    try:
        # Validate start date (default to today if not provided)
        if args.start_date:
            start_date = validate_date_format(args.start_date)
        else:
            start_date = datetime.now().strftime('%Y-%m-%d')
            logger.info(f"Start date not provided, defaulting to today: {start_date}")
        
        # Calculate or validate end date
        if args.end_date:
            end_date = validate_date_format(args.end_date)
            validate_date_range(start_date, end_date)
        else:
            end_date = calculate_end_date(start_date)
            logger.info(f"End date not provided, defaulting to 7 days after start date: {end_date}")
        
        logger.info(f"Date range: {start_date} to {end_date}")
        
        # Determine output directory
        if args.output_dir:
            output_dir = Path(args.output_dir)
        else:
            output_dir = Path(start_date)
        
        if not args.dry_run:
            output_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Output directory: {output_dir}")
        else:
            logger.info(f"DRY RUN: Would create output directory: {output_dir}")
        
        # Initialize API client
        client = APIClient(base_url=args.base_url)
        
        # Fetch event data
        logger.info("Fetching event data...")
        try:
            events_data = client.get_events(start_date=start_date, end_date=end_date)
            events_data = validate_api_response(events_data)
        except Exception as e:
            logger.error(f"Failed to fetch event data: {e}")
            logger.error("Please check:")
            logger.error("  - API server is running and accessible")
            logger.error("  - API URL is correct (use --base-url to override)")
            logger.error("  - Network connection is working")
            logger.error("  - Date range is valid")
            sys.exit(1)
        
        logger.info(f"Found {len(events_data)} event(s) to process")
        
        if len(events_data) == 0:
            logger.warning("No events found for the specified date range")
            return
        
        # Generate SVG for each event
        for index, event_data in enumerate(events_data):
            event_title = event_data.get('title', 'Unknown')
            logger.info(f"Processing event {index + 1}/{len(events_data)}: {event_title}")
            
            filename = output_dir / f"event_{index:02d}.svg"
            
            try:
                logger.debug(f"Generating SVG for event: {event_title}")
                svg_content = generate_svg(event_data)
                
                if args.dry_run:
                    logger.info(f"DRY RUN: Would create {filename}")
                    logger.debug(f"SVG content preview: {str(svg_content)[:200]}...")
                else:
                    logger.debug(f"Writing SVG to file: {filename}")
                    filename.write_text(str(svg_content))
                    logger.info(f"Successfully created {filename}")
                    
            except Exception as e:
                logger.error(f"Failed to generate SVG for event {index + 1}: {e}")
                logger.error(f"Event data: {event_data}")
                continue
        
        # Generate content.txt
        content_txt = generate_content_txt(events_data)
        content_file = output_dir / "content.txt"
        
        if args.dry_run:
            logger.info(f"DRY RUN: Would create {content_file}")
            logger.debug(f"Content preview:\n{content_txt[:500]}...")
            logger.info(f"DRY RUN: Would generate {len(events_data)} SVG file(s) and content.txt in {output_dir}/")
        else:
            logger.debug(f"Writing content.txt to file: {content_file}")
            content_file.write_text(content_txt)
            logger.info(f"Successfully created {content_file}")
            logger.info(f"Completed! Generated {len(events_data)} SVG file(s) and content.txt in {output_dir}/")
            
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)


def setup_logging(verbose: bool = False, quiet: bool = False) -> None:
    """
    Configure logging based on verbosity flags.
    
    Args:
        verbose: If True, set logging level to DEBUG
        quiet: If True, set logging level to WARNING
    """
    if quiet:
        level = logging.WARNING
    elif verbose:
        level = logging.DEBUG
    else:
        level = logging.INFO
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def calculate_end_date(start_date: str) -> str:
    """
    Calculate end date as 7 days after start date.
    
    Args:
        start_date: Start date in YYYY-MM-DD format
        
    Returns:
        End date in YYYY-MM-DD format (7 days after start_date)
    """
    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
    end_dt = start_dt + timedelta(days=7)
    return end_dt.strftime('%Y-%m-%d')


def generate_content_txt(events_data: list[dict]) -> str:
    """
    Generate content.txt text listing all events in the specified format.
    
    Args:
        events_data: List of event dictionaries
        
    Returns:
        Formatted text string for content.txt
    """
    lines = []
    
    for event_data in events_data:
        title = event_data.get('title') or 'Event'
        location = event_data.get('location') or ''
        host = event_data.get('host') or ''
        when = format_event_when(event_data)
        day_name = event_weekday(event_data)
        
        event_line_parts = []
        if day_name and when:
            event_line_parts.append(f"{day_name}, {when}: {title}")
        elif when:
            event_line_parts.append(f"{when}: {title}")
        else:
            event_line_parts.append(title)
        
        if location:
            event_line_parts.append(f"@ {location}")
        
        if host:
            event_line_parts.append(f"({host})")
        
        lines.append(" ".join(event_line_parts))
    
    # Add footer
    lines.extend([
        "",
        "For more information: see https://albertapaleo.org/events/calendar",
        "",
        "#palaeontology #paleontology #fossils #dinosaurs #events"
    ])
    
    return "\n".join(lines)


if __name__ == '__main__':
    main()
