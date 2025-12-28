"""API client for fetching event data from the APS API with retry logic."""

import logging
from typing import Any
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


class APIClient:
    """
    Client for interacting with the APS events API.
    
    Features:
    - Automatic retry with exponential backoff
    - Comprehensive error handling
    - Detailed logging
    
    Example:
        >>> client = APIClient("http://localhost:4321")
        >>> events = client.get_events("2025-01-15", "2025-01-22")
        >>> len(events)
        3
    """
    
    def __init__(
        self,
        base_url: str,
        timeout: int = 10,
        max_retries: int = 3
    ) -> None:
        """
        Initialize the API client.
        
        Args:
            base_url: Base URL for the API (e.g., "http://localhost:4321")
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        
        # Configure retry strategy with exponential backoff
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=1,  # Wait 1, 2, 4 seconds between retries
            status_forcelist=[429, 500, 502, 503, 504],  # Retry on these status codes
            allowed_methods=["GET"],
            raise_on_status=False
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    def get_events(self, start_date: str, end_date: str) -> list[dict[str, Any]]:
        """
        Fetch events from the API for the given date range.
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            List of event dictionaries. Each event may contain:
            - title (str, optional): Event title
            - subtitle (str, optional): Event subtitle
            - date (str, optional): Event date
            - host (str, optional): Event host
            - location (str, optional): Event location
            
        Raises:
            requests.exceptions.RequestException: If the API request fails after retries
            ValueError: If the API response is invalid
            
        Example:
            >>> client = APIClient("http://localhost:4321")
            >>> events = client.get_events("2025-01-15", "2025-01-22")
        """
        url = f"{self.base_url}/api/events"
        params = {
            'start_date': start_date,
            'end_date': end_date
        }
        
        logger.debug(f"Making request to {url} with params: {params}")
        
        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            
            # Handle HTTP errors with detailed messages
            if response.status_code == 404:
                raise requests.exceptions.RequestException(
                    f"API endpoint not found: {url}. Please check that the API server is running and the endpoint is correct."
                )
            elif response.status_code == 401:
                raise requests.exceptions.RequestException(
                    f"Authentication required for {url}. Please check your API credentials."
                )
            elif response.status_code == 403:
                raise requests.exceptions.RequestException(
                    f"Access forbidden for {url}. Please check your API permissions."
                )
            
            response.raise_for_status()
            
            # Validate response is JSON
            try:
                events = response.json()
            except ValueError as e:
                raise ValueError(
                    f"API returned invalid JSON response. Expected JSON but got: {response.text[:200]}"
                ) from e
            
            logger.info(f"Successfully fetched {len(events)} event(s) from API")
            return events
            
        except requests.exceptions.Timeout as e:
            error_msg = (
                f"Request to {url} timed out after {self.timeout} seconds. "
                + "The API server may be slow or unavailable. "
                + "Try increasing the timeout or check your network connection."
            )
            logger.error(error_msg)
            raise requests.exceptions.RequestException(error_msg) from e
            
        except requests.exceptions.ConnectionError as e:
            error_msg = (
                f"Failed to connect to {url}. "
                + "Please check that the API server is running and accessible. "
                + f"Error: {str(e)}"
            )
            logger.error(error_msg)
            raise requests.exceptions.RequestException(error_msg) from e
            
        except requests.exceptions.HTTPError as e:
            error_msg = (
                f"HTTP error {response.status_code} from {url}. "
                + f"Response: {response.text[:200]}"
            )
            logger.error(error_msg)
            raise requests.exceptions.RequestException(error_msg) from e
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Request error: {str(e)}"
            logger.error(error_msg)
            raise requests.exceptions.RequestException(error_msg) from e
