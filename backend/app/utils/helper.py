from urllib.parse import urlparse


def is_valid_url(url: str) -> bool:
    """
    Check if the URL has a valid format.
    """

    parsed = urlparse(url)

    return all([parsed.scheme, parsed.netloc])