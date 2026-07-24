import asyncio
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from playwright.async_api import Error as PlaywrightError, async_playwright
from PIL import Image

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp"}
SKIP_PATTERNS = ["favicon", "icon", "tracking", "pixel"]
MIN_IMAGE_WIDTH = 100
MIN_IMAGE_HEIGHT = 100

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/138.0 Safari/537.36"
    )
}


def is_supported_format(url: str) -> bool:
    parsed = urlparse(url)
    if parsed.scheme == "data":
        return False
    extension = Path(parsed.path).suffix.lower()
    return extension in SUPPORTED_EXTENSIONS


def is_skip_url(url: str) -> bool:
    lower_url = url.lower()
    if lower_url.startswith("data:"):
        return True
    if any(token in lower_url for token in SKIP_PATTERNS):
        return True
    if lower_url.endswith(".svg"):
        return True
    return False


def normalize_url(base_url: str, link: str) -> str | None:
    if not link:
        return None
    link = link.strip()
    if link.startswith("//"):
        link = f"https:{link}"
    absolute = urljoin(base_url, link)
    parsed = urlparse(absolute)
    if parsed.scheme not in {"http", "https"}:
        return None
    return absolute.split("#")[0]


def extract_css_urls(style_value: str) -> list[str]:
    urls = re.findall(r"url\(['\"]?(.*?)['\"]?\)", style_value, flags=re.IGNORECASE)
    return [url for url in urls if url]


def extract_json_ld_images(soup: BeautifulSoup) -> list[str]:
    results: list[str] = []
    scripts = soup.find_all("script", type="application/ld+json")
    for script in scripts:
        try:
            data = script.string
            if not data:
                continue
            import json
            payload = json.loads(data)
            if isinstance(payload, dict):
                payload = [payload]
            for item in payload:
                if isinstance(item, dict):
                    image_field = item.get("image")
                    if isinstance(image_field, str):
                        results.append(image_field)
                    elif isinstance(image_field, list):
                        results.extend([str(i) for i in image_field if isinstance(i, str)])
        except Exception:
            continue
    return results


async def render_page(url: str) -> str | None:
    try:
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=True)
            context = await browser.new_context(ignore_https_errors=True)
            page = await context.new_page()
            await page.set_extra_http_headers(HEADERS)
            await page.goto(url, wait_until="networkidle", timeout=30000)
            for _ in range(6):
                await page.evaluate("window.scrollBy(0, window.innerHeight)")
                await asyncio.sleep(1)
            await page.wait_for_load_state("networkidle", timeout=10000)
            content = await page.content()
            await browser.close()
            return content
    except PlaywrightError as exc:
        print("Renderer Error:", exc)
        return None
    except Exception as exc:
        print("Renderer Unexpected Error:", exc)
        return None


def extract_image_urls(url: str, html: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    urls: set[str] = set()

    for img in soup.find_all("img"):
        for attr in ["src", "data-src", "data-original", "data-lazy-src"]:
            candidate = img.get(attr)
            if candidate:
                normalized = normalize_url(url, candidate)
                if normalized:
                    urls.add(normalized)
        srcset = img.get("srcset")
        if srcset:
            for part in srcset.split(","):
                candidate = part.strip().split(" ")[0]
                normalized = normalize_url(url, candidate)
                if normalized:
                    urls.add(normalized)

    for source in soup.find_all(["source", "video"]):
        candidate = source.get("src") or source.get("data-src") or source.get("data-lazy-src")
        if candidate:
            normalized = normalize_url(url, candidate)
            if normalized:
                urls.add(normalized)

    for picture in soup.find_all("picture"):
        for source in picture.find_all("source"):
            candidate = source.get("srcset") or source.get("data-src") or source.get("data-lazy-src")
            if candidate:
                for part in candidate.split(","):
                    candidate_url = part.strip().split(" ")[0]
                    normalized = normalize_url(url, candidate_url)
                    if normalized:
                        urls.add(normalized)

    for link in soup.find_all("link", rel=True):
        rel = link.get("rel")
        if isinstance(rel, list) and any("image" in item for item in rel):
            href = link.get("href")
            normalized = normalize_url(url, href)
            if normalized:
                urls.add(normalized)

    for meta in soup.find_all("meta"):
        if meta.get("property") in {"og:image", "twitter:image", "twitter:image:src"} or meta.get("name") in {"og:image", "twitter:image", "twitter:image:src"}:
            content = meta.get("content")
            normalized = normalize_url(url, content)
            if normalized:
                urls.add(normalized)

    for tag in soup.find_all(True):
        style = tag.get("style")
        if style:
            for css_url in extract_css_urls(style):
                normalized = normalize_url(url, css_url)
                if normalized:
                    urls.add(normalized)

    for style_block in soup.find_all("style"):
        style_text = style_block.string or ""
        for css_url in extract_css_urls(style_text):
            normalized = normalize_url(url, css_url)
            if normalized:
                urls.add(normalized)

    urls.update(extract_json_ld_images(soup))
    filtered_urls = [u for u in urls if not is_skip_url(u) and is_supported_format(u)]
    return list(filtered_urls)


def download_image(session: requests.Session, image_url: str, index: int) -> dict[str, Any] | None:
    max_attempts = 3
    for attempt in range(1, max_attempts + 1):
        try:
            response = session.get(image_url, headers=HEADERS, timeout=15, stream=True, allow_redirects=True)
            if response.status_code != 200:
                print(f"Download failed ({attempt}) {image_url}: {response.status_code}")
                continue
            content_type = response.headers.get("Content-Type", "")
            if "image" not in content_type and not is_supported_format(image_url):
                print(f"Skipping non-image content: {image_url}")
                return None
            extension = Path(urlparse(image_url).path).suffix.lower()
            if extension not in SUPPORTED_EXTENSIONS:
                extension = ".jpg"
            filename = f"image_{index}{extension}"
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            with open(filepath, "wb") as file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)
            width = height = None
            try:
                with Image.open(filepath) as img:
                    width, height = img.size
                if width < MIN_IMAGE_WIDTH or height < MIN_IMAGE_HEIGHT:
                    print(f"Skipping small image: {image_url} ({width}x{height})")
                    os.remove(filepath)
                    return None
            except Exception:
                pass
            return {
                "filename": filename,
                "image_url": image_url,
                "saved_path": filepath,
                "width": width,
                "height": height,
            }
        except requests.RequestException as exc:
            print(f"Download exception ({attempt}) for {image_url}: {exc}")
            continue
        except Exception as exc:
            print(f"Unexpected download error for {image_url}: {exc}")
            break
    return None


def scrape_images(url: str) -> list[dict[str, Any]]:
    print("=" * 50)
    print("Scraping Started...")
    print("Website:", url)
    print("Saving Images To:", UPLOAD_FOLDER)

    html = None
    try:
        html = asyncio.run(render_page(url))
    except Exception as exc:
        print("Render exception:", exc)

    if not html:
        try:
            response = requests.get(url, headers=HEADERS, timeout=20, allow_redirects=True)
            response.raise_for_status()
            html = response.text
            print("Fallback to plain request HTML")
        except Exception as exc:
            print("Website Error:", exc)
            return []

    image_urls = extract_image_urls(url, html)
    print(f"Total candidate images found: {len(image_urls)}")

    unique_urls = []
    seen = set()
    for image_url in image_urls:
        if image_url not in seen:
            seen.add(image_url)
            unique_urls.append(image_url)

    print(f"Unique supported images after filtering: {len(unique_urls)}")

    results: list[dict[str, Any]] = []
    with requests.Session() as session:
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(download_image, session, url, idx + 1) for idx, url in enumerate(unique_urls)]
            for future in futures:
                result = future.result()
                if result:
                    results.append(result)
                    print("Downloaded:", result["filename"])
                else:
                    print("Skipped or failed download")

    print("=" * 50)
    print("Downloaded Images:", len(results))
    print("=" * 50)
    return results
