import ipaddress
import socket
from urllib.parse import urljoin, urlparse

import requests


def is_valid_url(url: str) -> bool:
    """Check if the URL has a valid format."""
    parsed = urlparse(url)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def normalize_input_url(url: str) -> str:
    """Trim whitespace and add https:// when the user forgot the scheme."""
    url = (url or "").strip()
    if url and "://" not in url:
        url = "https://" + url
    return url


def is_public_url(url: str) -> bool:
    """Return whether *url* resolves only to publicly routable addresses.

    The API fetches user-provided pages and their images, so accepting loopback
    or private addresses would allow callers to probe services on the API host.
    """
    if not is_valid_url(url):
        return False

    hostname = urlparse(url).hostname
    if not hostname or hostname.lower() == "localhost":
        return False

    try:
        addresses = {
            result[4][0]
            for result in socket.getaddrinfo(hostname, None, type=socket.SOCK_STREAM)
        }
    except socket.gaierror:
        return False

    if not addresses:
        return False

    for address in addresses:
        if not ipaddress.ip_address(address).is_global:
            return False

    return True


def safe_get(url: str, headers=None, timeout=15, stream=False, max_redirects=5):
    """requests.get that follows redirects manually and re-validates every hop.

    Many sites/CDNs answer with 301/302. Blocking redirects entirely made
    those sites look "unreachable"; following them blindly would reopen the
    SSRF hole. Each hop must be a public URL.
    """
    current = url
    for _ in range(max_redirects + 1):
        if not is_public_url(current):
            raise requests.exceptions.InvalidURL(f"Blocked non-public URL: {current}")
        response = requests.get(
            current, headers=headers, timeout=timeout, stream=stream, allow_redirects=False
        )
        if response.status_code in {301, 302, 303, 307, 308}:
            location = response.headers.get("Location")
            response.close()
            if not location:
                raise requests.exceptions.RequestException("Redirect without Location")
            current = urljoin(current, location)
            continue
        return response
    raise requests.exceptions.TooManyRedirects(f"Too many redirects for {url}")
