import requests

from app.utils.helper import is_public_url


def check_website(url: str):
    """
    Check if the website is reachable.
    """

    if not is_public_url(url):
        return False, None

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/138.0 Safari/537.36"
        )
    }

    try:
        response = requests.get(url, headers=headers, timeout=10, allow_redirects=False)

        if response.status_code == 200:
            return True, response.status_code

        return False, response.status_code

    except requests.exceptions.RequestException:
        return False, None
