import ipaddress
import socket
from urllib.parse import urlparse


def is_valid_url(url: str) -> bool:
    """
    Check if the URL has a valid format.
    """

    parsed = urlparse(url)

    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


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
        ip = ipaddress.ip_address(address)
        if not ip.is_global:
            return False

    return True
