#!/usr/bin/env python3
"""
Submit every URL in sitemap.xml to the IndexNow API.

Replaces an inline `python -c` block that silently reported success even when
all three endpoints rejected the submission (observed: Bing returned
`{"errorCode":"InvalidRequestParameters","message":"The key field is
required."}` on every run while the job stayed green).

Two rules this script enforces:

1. The key is read from exactly one place and verified against the key file
   on disk. IndexNow requires keyLocation's filename to equal the file's
   content, and the "key" field to match it. The repo previously carried
   three different values (secret, a fallback inside the script, and the key
   file's actual content), none of which agreed.
2. The job exits non-zero when no endpoint accepts the submission, so a
   broken key can never look like a successful run.
"""

import os
import sys
import glob
import xml.etree.ElementTree as ET

import requests

SITE_URL = "https://lishoulan.github.io/nextool-apps/"
SITEMAP_PATH = "sitemap.xml"
HOST = "lishoulan.github.io"
ENDPOINTS = [
    "https://api.indexnow.org/indexnow",
    "https://www.bing.com/indexnow",
    "https://yandex.com/indexnow",
]
MAX_URLS = 10000  # IndexNow caps urlList at 10,000 per request


def resolve_key():
    """Return the IndexNow key, or exit with a clear message.

    Prefers the secret, falls back to the key file committed in the repo.
    Verifies that the key file's name matches its content, which is what
    IndexNow's keyLocation check actually validates.
    """
    secret = os.environ.get("INDEXNOW_KEY", "").strip()

    candidates = glob.glob("*.txt")
    key_files = [p for p in candidates if "requirements" not in p and "robots" not in p]
    if not key_files:
        print("❌ No IndexNow key file found in the repository root.")
        sys.exit(1)

    for path in key_files:
        content = open(path, encoding="utf-8").read().strip()
        stem = os.path.splitext(os.path.basename(path))[0]
        if content and content != stem:
            print(f"⚠️  {path}: filename '{stem}' != content '{content}'.")
            print("   IndexNow validates keyLocation by matching name and content.")

    on_disk = open(key_files[0], encoding="utf-8").read().strip()

    if secret and on_disk and secret != on_disk:
        print(f"❌ INDEXNOW_KEY secret does not match {key_files[0]} on disk.")
        print(f"   secret={secret!r}  disk={on_disk!r}")
        print("   Fix the secret, or delete it to use the committed key file.")
        sys.exit(1)

    key = secret or on_disk
    print(f"🔑 Using key: {key} (source: {'secret' if secret else key_files[0]})")
    return key


def read_urls():
    if not os.path.exists(SITEMAP_PATH):
        print(f"❌ {SITEMAP_PATH} not found.")
        sys.exit(1)
    root = ET.parse(SITEMAP_PATH).getroot()
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    urls = []
    for url_elem in root.findall("sm:url", ns):
        loc = url_elem.find("sm:loc", ns)
        if loc is not None and loc.text:
            urls.append(loc.text.strip())
    if not urls:
        print("❌ No URLs found in sitemap.xml — nothing to submit.")
        sys.exit(1)
    return urls[:MAX_URLS]


def main():
    key = resolve_key()
    urls = read_urls()
    print(f"📄 Found {len(urls)} URLs in sitemap.xml")

    payload = {
        "host": HOST,
        "key": key,
        "keyLocation": f"{SITE_URL}{key}.txt",
        "urlList": urls,
    }
    headers = {"Content-Type": "application/json; charset=utf-8"}

    ok = 0
    for endpoint in ENDPOINTS:
        try:
            resp = requests.post(endpoint, json=payload, headers=headers, timeout=30)
            if resp.status_code in (200, 202, 204):
                print(f"✅ {endpoint} -> {resp.status_code}")
                ok += 1
            else:
                print(f"❌ {endpoint} -> {resp.status_code}")
                print(f"   {resp.text[:300]}")
        except Exception as exc:
            print(f"⚠️  {endpoint} -> {exc}")

    print(f"\nSubmitted to {ok}/{len(ENDPOINTS)} endpoints.")
    if ok == 0:
        print("❌ Every endpoint rejected the submission.")
        print("   Most likely cause: the key does not match the key file.")
        print(f"   Verify https://{HOST}/nextool-apps/{key}.txt returns exactly '{key}'.")
        sys.exit(1)
    print("✅ IndexNow submission accepted.")


if __name__ == "__main__":
    main()
