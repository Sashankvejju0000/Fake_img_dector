import requests


def check_website(url: str):
    """
    Check if the website is reachable.
    """

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/138.0 Safari/537.36"
        )
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            return True, response.status_code

        return False, response.status_code

    except requests.exceptions.RequestException:
        return False, None