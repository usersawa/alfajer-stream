import json
import re
from datetime import datetime, timezone

import requests

SOURCE_URL = "https://tv.alfajertv.com/webos/?channel=fajer1-hd2"
OUTPUT_FILE = "stream.json"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Linux; Android 10) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0 Mobile Safari/537.36"
    )
}

M3U8_PATTERN = re.compile(
    r'https?://live\.alfajertv\.com/[^"\'>\s]+\.m3u8(?:\?[^"\'>\s]+)?',
    re.I
)


def extract_stream(html):
    matches = M3U8_PATTERN.findall(html)

    if not matches:
        return None

    # Prefer the signed URL containing md5 and expires
    for url in matches:
        if "md5=" in url and "expires=" in url:
            return url

    return matches[0]


def get_expires(url):
    match = re.search(r"(?:[?&])expires=(\d+)", url)

    if not match:
        return None

    return int(match.group(1))


def main():
    response = requests.get(
        SOURCE_URL,
        headers=HEADERS,
        timeout=30
    )

    response.raise_for_status()

    stream_url = extract_stream(response.text)

    if not stream_url:
        raise RuntimeError(
            "لم يتم العثور على رابط M3U8 داخل صفحة المصدر."
        )

    expires = get_expires(stream_url)

    data = {
        "channel": "fajer1-hd2",
        "stream": stream_url,
        "expires": expires,
        "updated_at": datetime.now(timezone.utc).isoformat()
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("Stream updated:")
    print(stream_url)

    if expires:
        print(f"Expires: {expires}")


if __name__ == "__main__":
    main()
