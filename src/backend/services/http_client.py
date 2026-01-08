import requests
from requests import Response
from typing import Optional, Dict

class HttpClient:
    DEFAULT_TIMEOUT = 5

    DEFAULT_HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        )
    }

    @classmethod
    def get(
        cls,
        url: str,
        params: Optional[Dict[str, str]] = None,
    ) -> Response:
        return requests.get(
            url,
            timeout=cls.DEFAULT_TIMEOUT,
            allow_redirects=True,
            headers=cls.DEFAULT_HEADERS,
            params=params,
        )