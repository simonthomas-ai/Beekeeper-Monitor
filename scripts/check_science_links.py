#!/usr/bin/env python3
"""Check published science page and referenced external sources (network required)."""
import argparse
from html.parser import HTMLParser
from pathlib import Path
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
    def handle_starttag(self, tag, attrs):
        if tag == "a":
            href = dict(attrs).get("href", "")
            if href.startswith("https://"):
                self.links.append(href)

def check(url, attempts=2):
    for attempt in range(attempts):
        try:
            req = Request(url, headers={"User-Agent": "VespaGuard-Research-Link-Check/1.0 (GitHub Actions)", "Accept": "text/html,application/pdf,*/*"})
            with urlopen(req, timeout=25) as response:
                status = response.status
                if status < 400:
                    return "OK", str(status)
        except HTTPError as exc:
            if exc.code in (401, 403, 429):
                return "REVIEW", f"HTTP {exc.code}: server blocks or limits automated access"
            result = f"HTTP {exc.code}"
        except (URLError, TimeoutError, OSError) as exc:
            result = str(exc)[:160]
        if attempt + 1 < attempts:
            time.sleep(3)
    return "FAIL", result

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--public", action="store_true")
    parser.add_argument("--strict-external", action="store_true")
    args = parser.parse_args()
    source = Path("wissen/wissenschaft-hornissen-bienen.html")
    if not source.is_file():
        print("FAIL: science page missing")
        return 1
    page = Links()
    page.feed(source.read_text(encoding="utf-8"))
    urls = list(dict.fromkeys(page.links))
    if not urls:
        print("FAIL: no sources found")
        return 1
    checks = []
    if args.public:
        checks.append(("PUBLIC", "https://simonthomas-ai.github.io/Beekeeper-Monitor/wissen/wissenschaft-hornissen-bienen.html"))
    checks.extend(("SOURCE", url) for url in urls)
    failures = 0
    for kind, url in checks:
        status, reason = check(url, attempts=3 if kind == "PUBLIC" else 2)
        print(f"{kind} {status}: {url} ({reason})", flush=True)
        if status == "FAIL" and (kind == "PUBLIC" or args.strict_external):
            failures += 1
    print(f"Checked {len(urls)} external scientific links; automatic access restrictions are REVIEW, not proof of broken links.")
    return 1 if failures else 0

if __name__ == "__main__":
    sys.exit(main())
