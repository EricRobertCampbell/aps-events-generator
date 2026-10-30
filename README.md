# APS Weekly Events SVG Generator

A Python script to generate SVG graphics for weekly palaeontological events from the Alberta Palaeontological Society API.

## Features

- Fetches event data from the APS API with automatic retry logic
- Generates beautiful SVG graphics with the APS logo and event details
- Automatically organizes output files by date
- Handles missing event data gracefully
- Comprehensive error handling and validation
- API response caching for improved performance
- Command-line interface with multiple options

## Requirements

- Python 3.7+
- Dependencies listed in `requirements.txt`

## Installation

1. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Basic Usage

Generate SVGs for events starting today (through 7 days later):

```bash
python generate.py
```

Or specify a start date:

```bash
python generate.py 2025-01-15
```

This will:
- Fetch events from January 15, 2025 to January 22, 2025 (7 days)
- Create a folder named `2025-01-15/`
- Generate SVG files (`event_00.svg`, `event_01.svg`, etc.) in that folder

### Command-Line Options

```bash
python generate.py [start_date] [end_date] [options]
```

**Positional Arguments:**
- `start_date`: Start date in YYYY-MM-DD format (optional, defaults to today)
- `end_date`: End date in YYYY-MM-DD format (optional, defaults to 7 days after start_date)

**Options:**
- `--output-dir DIR`: Custom output directory (defaults to start_date)
- `--base-url URL`: Override API base URL (default: https://albertapaleo.org)
- `--verbose, -v`: Enable verbose logging (DEBUG level)
- `--quiet, -q`: Suppress informational messages (WARNING level only)
- `--dry-run`: Preview what would be generated without creating files
- `--help, -h`: Show help message

### Examples

**Generate events for a week starting January 1st:**
```bash
python generate.py 2025-01-01
```

**Generate events for a specific date range:**
```bash
python generate.py 2025-03-15 2025-03-22
```

**Use custom output directory:**
```bash
python generate.py 2025-01-15 --output-dir my-events
```

**Use local development API:**
```bash
python generate.py 2025-01-15 --base-url http://localhost:4321
```

**Preview without generating files:**
```bash
python generate.py 2025-01-15 --dry-run
```

**Verbose logging for debugging:**
```bash
python generate.py 2025-01-15 --verbose
```

## Output

The script creates:
- A directory named after the start date (e.g., `2025-01-15/`) or custom directory if specified
- SVG files for each event (e.g., `event_00.svg`, `event_01.svg`, etc.)

Each SVG includes:
- APS logo in the top-left corner, embedded in the file
- "Palaeo Events!" header text (centered horizontally)
- Event title, subtitle, host, date, and location (centered on the page)
- Registration deadline, when the event includes one, below those details

The logo artwork is written into the SVG, so moving the file does not break the logo. Dates are compact, for example `January 3, 4 - 5pm`. `content.txt` uses the same date after the weekday, for example `Saturday, January 3, 4 - 5pm: Event Title`.

## API Response Format

The script expects the API endpoint `/api/events` to return a JSON array of event objects.

### Request Format

```
GET /api/events?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD
```

### Response Format

The API should return a JSON array of event frontmatter. Dates stay in their source form. This script formats them for the graphic and for `content.txt`.

```json
[
  {
    "id": "2026-01-03-example",
    "title": "Event Title",
    "subtitle": "Event Subtitle",
    "start": "2026-01-03T16:00:00-07:00",
    "end": "2026-01-03T17:00:00-07:00",
    "type": "External",
    "host": "Event Host",
    "location": "Calgary, AB",
    "registrationDeadline": "2026-01-02T17:00:00-07:00",
    "detailsLink": "https://example.com/event",
    "image": {
      "src": "/events/2026/example.jpg",
      "alt": "Event poster"
    }
  },
  {
    "id": "2026-01-20-field-trip",
    "title": "Another Event",
    "startDate": "2026-01-20",
    "endDate": "2026-01-22",
    "type": "Field Trip",
    "location": "Edmonton, AB"
  }
]
```

**Fields:**
- `id` (str): Content collection id
- `title` (str): Event title
- `type` (str): Event type, such as `Monthly Meeting` or `Field Trip`
- `subtitle` (str, optional): Event subtitle
- `start` / `end` (str, optional): ISO datetimes with an offset, used when the event has a time
- `startDate` / `endDate` (str, optional): `YYYY-MM-DD`, used when the event has a date but no time
- `host` (str, optional): Host, included only when the host is not the APS
- `location` (str, optional): Event location
- `detailsLink` (str, optional): Link to more information
- `registrationDeadline` (str, optional): `YYYY-MM-DD`, or an ISO datetime with an offset. Drawn below the other text as `Registration deadline: January 2, 5pm`
- `image` (object, optional): `src`, `alt`, and optional `attribution`. Not drawn on the graphic

Missing optional fields are omitted and simply won't appear in the generated SVG. Timed fields are preferred over date-only fields when both are present. A same-day range such as 4:00 p.m. to 5:00 p.m. on January 3 is written as `January 3, 4 - 5pm`.

### API Features

- **Automatic Retry**: Failed requests are automatically retried up to 3 times with exponential backoff
- **Error Handling**: Comprehensive error messages for common issues (timeouts, connection errors, etc.)

## Troubleshooting

### Common Issues

**"Invalid date format" error:**
- Ensure dates are in YYYY-MM-DD format (e.g., `2025-01-15`, not `01/15/2025`)
- Check that start_date is before or equal to end_date

**"Failed to connect to API" error:**
- Verify the API server is running and accessible
- Check the API URL is correct (use `--base-url` to override)
- Ensure your network connection is working
- For local development, use `--base-url http://localhost:4321` if testing against a local server

**"API endpoint not found (404)" error:**
- Verify the API endpoint path is `/api/events`
- Check that the API server is running the correct version
- Ensure the base URL is correct

**"API returned invalid JSON" error:**
- The API may be returning an error page instead of JSON
- Check the API server logs for errors
- Verify the API endpoint is working by testing it directly (e.g., with `curl`)

**"No events found" warning:**
- This is normal if there are no events in the specified date range
- Try a different date range
- Verify events exist in the API for those dates

**Logo file not found:**
- Ensure `files/APS logo-black.svg` exists in the project directory
- The script will continue without the logo but will log a warning
- When the logo is found, it is embedded in each SVG rather than linked by path

### Debugging Tips

1. **Use verbose logging:**
   ```bash
   python generate.py 2025-01-15 --verbose
   ```

2. **Use dry-run to preview:**
   ```bash
   python generate.py 2025-01-15 --dry-run
   ```

3. **Test API directly:**
   ```bash
   # Production API
   curl "https://albertapaleo.org/api/events?start_date=2025-01-15&end_date=2025-01-22"
   
   # Local development API
   curl "http://localhost:4321/api/events?start_date=2025-01-15&end_date=2025-01-22"
   ```

## Project Structure

```
aps-weekly-events/
├── generate.py          # Main CLI entry point
├── api_client.py        # API client with retry logic and caching
├── dates.py             # Compact date and time formatting
├── svg_generator.py      # SVG generation logic
├── validators.py        # Input validation functions
├── requirements.txt     # Python dependencies
├── README.md           # This file
├── .gitignore          # Git ignore rules
└── files/
    ├── APS logo-black.svg  # APS logo embedded in generated SVGs
    └── APS logo-white.svg  # APS logo file
```

## Development

### Code Quality

The project follows Python best practices:
- Type hints throughout
- Comprehensive docstrings with examples
- Modular structure for maintainability
- Error handling and validation

### Adding New Features

1. **API Client** (`api_client.py`): Handles all API communication
2. **Dates** (`dates.py`): Compact date and time formatting
3. **SVG Generator** (`svg_generator.py`): Handles SVG creation
4. **Validators** (`validators.py`): Input validation logic
5. **CLI** (`generate.py`): Command-line interface

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]
