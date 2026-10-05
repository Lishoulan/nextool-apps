#!/usr/bin/env python3
"""
Sitemap auto-updater for NextTool.
Scans all index.html and blog HTML files, updates sitemap.xml with:
- Current date as lastmod for all entries
- Adds missing URLs discovered from the file system
"""

import os
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

BASE_URL = "https://lishoulan.github.io/nextool-apps"
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SITEMAP_PATH = os.path.join(REPO_ROOT, "sitemap.xml")
TODAY = datetime.now(timezone.utc).strftime("%Y-%m-%d")

# Priority mapping for different page types
PRIORITY_MAP = {
    "": "1.0",          # Root homepage
    "blog": "0.7",      # Blog index
    "compare": "0.7",
    "landing": "0.8",
    "pricing": "0.8",
    "referral": "0.7",
    "company-website": "0.7",
    "api-docs": "0.8",
    "launch-plan": "0.7",
    "payment-guide": "0.7",
    "admin": "0.5",
}

# Default priority for tool pages
DEFAULT_TOOL_PRIORITY = "0.8"
DEFAULT_BLOG_PRIORITY = "0.6"

# Set at import time by _detect_incomplete_checkout() once the constants above
# are defined; referenced by self_url_exists() to avoid destructive pruning.
_INCOMPLETE_CHECKOUT = False


# Non-page directories: skipped when discovering pages (blog is handled
# explicitly, so it is indexed on purpose and must not be filtered out).
NON_PAGE_DIRS = {
    ".github", "css", "js", "icons", "reports", "launch-plan", "company-website",
    "admin",
}

# Pages that must never appear in the sitemap, even if a previous run added
# them. "admin" is an internal control panel and should not be crawlable.
EXCLUDE_FROM_SITEMAP = {
    "admin",
}

# Standalone HTML pages at repo root worth indexing.
ROOT_PAGES = {
    "premium.html": ("0.8", "monthly"),
    "services.html": ("0.8", "monthly"),
}


def discover_urls():
    """Scan the repository for all HTML pages and build URL list."""
    urls = []

    # Root index.html
    root_index = os.path.join(REPO_ROOT, "index.html")
    if os.path.exists(root_index):
        urls.append(("", "weekly", PRIORITY_MAP.get("", "1.0")))

    # Directories with index.html (tool pages, compare/, pricing/, ...)
    for entry in sorted(os.listdir(REPO_ROOT)):
        entry_path = os.path.join(REPO_ROOT, entry)
        if os.path.isdir(entry_path) and entry not in NON_PAGE_DIRS and entry != "blog":
            index_file = os.path.join(entry_path, "index.html")
            if os.path.exists(index_file):
                priority = PRIORITY_MAP.get(entry, DEFAULT_TOOL_PRIORITY)
                changefreq = "monthly"
                urls.append((entry, changefreq, priority))

    # Standalone root-level pages (premium.html, services.html, ...)
    for fname, (priority, changefreq) in ROOT_PAGES.items():
        if os.path.exists(os.path.join(REPO_ROOT, fname)):
            urls.append((fname, changefreq, priority))

    # Second-level pages inside content directories.
    # compare/ and landing/ both target high-intent queries ("smallpdf
    # alternative", "free pdf tools") and were previously never submitted,
    # while carrying canonical tags that asked to be indexed.
    for subdir in ("compare", "landing"):
        sub_path = os.path.join(REPO_ROOT, subdir)
        if not os.path.isdir(sub_path):
            continue
        priority = PRIORITY_MAP.get(subdir, "0.7")
        for fname in sorted(os.listdir(sub_path)):
            if fname.endswith(".html") and fname != "index.html":
                urls.append((f"{subdir}/{fname}", "monthly", priority))

    # Legacy article archive: blog/articles/*.html are canonical-tagged and
    # linked from the blog index, so they belong in the sitemap too.
    articles_dir = os.path.join(REPO_ROOT, "blog", "articles")
    if os.path.isdir(articles_dir):
        for fname in sorted(os.listdir(articles_dir)):
            if fname.endswith(".html") and fname != "index.html":
                urls.append((f"blog/articles/{fname}", "monthly", DEFAULT_BLOG_PRIORITY))

    # Blog index
    blog_index = os.path.join(REPO_ROOT, "blog", "index.html")
    if os.path.exists(blog_index):
        urls.append(("blog", "weekly", PRIORITY_MAP.get("blog", "0.7")))

    # Blog HTML articles
    blog_dir = os.path.join(REPO_ROOT, "blog")
    if os.path.isdir(blog_dir):
        for fname in sorted(os.listdir(blog_dir)):
            if fname.endswith(".html") and fname != "index.html":
                blog_path = f"blog/{fname}"
                urls.append((blog_path, "monthly", DEFAULT_BLOG_PRIORITY))

    return urls


def self_url_exists(loc: str) -> bool:
    """Check whether a sitemap URL still maps to a file on disk.

    "/foo/"  -> <root>/foo/index.html
    "/a.html"-> <root>/a.html

    Guards against a partial checkout: if scanning the repo root turns up
    far fewer tool directories than the sitemap already lists, assume the
    tree is incomplete and report "everything exists" so a bad checkout can
    never wipe the sitemap.
    """
    rel = loc[len(BASE_URL):].lstrip("/") if loc.startswith(BASE_URL) else loc
    if not rel:
        return os.path.exists(os.path.join(REPO_ROOT, "index.html"))
    if rel.endswith("/"):
        rel = rel.rstrip("/") + "/index.html"
    if os.path.exists(os.path.join(REPO_ROOT, rel)):
        return True
    return _INCOMPLETE_CHECKOUT


def _detect_incomplete_checkout() -> bool:
    """True when the working tree looks too sparse to trust deletions."""
    try:
        entries = [
            e for e in os.listdir(REPO_ROOT)
            if os.path.isdir(os.path.join(REPO_ROOT, e))
            and e not in NON_PAGE_DIRS
            and os.path.exists(os.path.join(REPO_ROOT, e, "index.html"))
        ]
    except OSError:
        return True
    # A real checkout of this site has 25+ page directories. Far fewer means
    # something went wrong with the checkout, so don't prune anything.
    return len(entries) < 10


def update_sitemap():
    """Read existing sitemap, merge with discovered URLs, and write back."""
    global _INCOMPLETE_CHECKOUT
    _INCOMPLETE_CHECKOUT = _detect_incomplete_checkout()
    if _INCOMPLETE_CHECKOUT:
        print("  ⚠️  Working tree looks incomplete — skipping stale-URL cleanup.")

    # Discover all URLs from file system
    discovered = discover_urls()
    discovered_locs = {f"{BASE_URL}/{path}/" if path and not path.endswith(".html") and "/" not in path else (f"{BASE_URL}/{path}" if path else f"{BASE_URL}/") for path, _, _ in discovered}

    # Normalize: for non-blog directories, ensure trailing slash
    normalized_discovered = {}
    for path, changefreq, priority in discovered:
        if not path:
            loc = f"{BASE_URL}/"
        elif path.endswith(".html"):
            loc = f"{BASE_URL}/{path}"
        else:
            loc = f"{BASE_URL}/{path}/"
        normalized_discovered[loc] = (path, changefreq, priority)

    # Parse existing sitemap
    existing_locs = set()
    if os.path.exists(SITEMAP_PATH):
        tree = ET.parse(SITEMAP_PATH)
        root = tree.getroot()
        ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}

        for url_elem in root.findall("sm:url", ns):
            loc_elem = url_elem.find("sm:loc", ns)
            if loc_elem is not None:
                loc = loc_elem.text.strip()

                # Drop entries that must no longer be indexed (e.g. admin/).
                rel = loc[len(BASE_URL):].lstrip("/") if loc.startswith(BASE_URL) else loc
                if rel.split("/")[0] in EXCLUDE_FROM_SITEMAP:
                    print(f"  ➖ Removing excluded URL: {loc}")
                    root.remove(url_elem)
                    continue

                # Drop entries whose page no longer exists on disk, so a
                # deleted/renamed page does not linger as a 404 in the sitemap.
                if not self_url_exists(loc):
                    print(f"  ➖ Removing stale URL (page missing): {loc}")
                    root.remove(url_elem)
                    continue

                existing_locs.add(loc)

                # Update or add lastmod
                lastmod_elem = url_elem.find("sm:lastmod", ns)
                if lastmod_elem is None:
                    lastmod_elem = ET.SubElement(url_elem, "{http://www.sitemaps.org/schemas/sitemap/0.9}lastmod")
                lastmod_elem.text = TODAY

        # Add missing URLs
        for loc, (path, changefreq, priority) in normalized_discovered.items():
            if loc not in existing_locs:
                print(f"  ➕ Adding missing URL: {loc}")
                url_elem = ET.SubElement(root, "{http://www.sitemaps.org/schemas/sitemap/0.9}url")

                loc_elem = ET.SubElement(url_elem, "{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
                loc_elem.text = loc

                lastmod_elem = ET.SubElement(url_elem, "{http://www.sitemaps.org/schemas/sitemap/0.9}lastmod")
                lastmod_elem.text = TODAY

                changefreq_elem = ET.SubElement(url_elem, "{http://www.sitemaps.org/schemas/sitemap/0.9}changefreq")
                changefreq_elem.text = changefreq

                priority_elem = ET.SubElement(url_elem, "{http://www.sitemaps.org/schemas/sitemap/0.9}priority")
                priority_elem.text = priority
    else:
        # Create new sitemap from scratch
        ns = "http://www.sitemaps.org/schemas/sitemap/0.9"
        root = ET.Element(f"{{{ns}}}urlset")
        root.set("xmlns", ns)

        for loc, (path, changefreq, priority) in sorted(normalized_discovered.items()):
            url_elem = ET.SubElement(root, f"{{{ns}}}url")

            loc_elem = ET.SubElement(url_elem, f"{{{ns}}}loc")
            loc_elem.text = loc

            lastmod_elem = ET.SubElement(url_elem, f"{{{ns}}}lastmod")
            lastmod_elem.text = TODAY

            changefreq_elem = ET.SubElement(url_elem, f"{{{ns}}}changefreq")
            changefreq_elem.text = changefreq

            priority_elem = ET.SubElement(url_elem, f"{{{ns}}}priority")
            priority_elem.text = priority

    # Write the sitemap with proper formatting
    ET.indent(root, space="  ")
    tree = ET.ElementTree(root)
    tree.write(SITEMAP_PATH, encoding="UTF-8", xml_declaration=True)

    # Post-process: ensure proper formatting (ElementTree adds ns0 prefix workaround)
    with open(SITEMAP_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # Remove any ns0: prefixes that ElementTree might add
    content = content.replace("ns0:", "")
    content = re.sub(r'\s+xmlns:ns0="[^"]*"', '', content)
    # Ensure xmlns is correct
    content = content.replace(
        '<urlset>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    )

    with open(SITEMAP_PATH, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✅ Sitemap updated with lastmod={TODAY}")


if __name__ == "__main__":
    update_sitemap()
