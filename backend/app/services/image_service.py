import requests

from app.utils.helper import safe_get

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/138.0 Safari/537.36"
    )
}


def check_website(url: str):
    """Return (reachable, status_code). Redirects are followed safely."""
    try:
        response = safe_get(url, headers=HEADERS, timeout=10, stream=True)
        status = response.status_code
        response.close()
        return status < 400, status
    except requests.exceptions.RequestException:
        return False, None
