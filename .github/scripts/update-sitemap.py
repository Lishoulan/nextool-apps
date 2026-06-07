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


def discover_urls():
    """Scan the repository for all HTML pages and build URL list."""
    urls = []

    # Root index.html
    root_index = os.path.join(REPO_ROOT, "index.html")
    if os.path.exists(root_index):
        urls.append(("", "weekly", PRIORITY_MAP.get("", "1.0")))

    # Tool directories with index.html
    for entry in sorted(os.listdir(REPO_ROOT)):
        entry_path = os.path.join(REPO_ROOT, entry)
        if os.path.isdir(entry_path) and entry not in (".github", "css", "js", "icons", "blog"):
            index_file = os.path.join(entry_path, "index.html")
            if os.path.exists(index_file):
                priority = PRIORITY_MAP.get(entry, DEFAULT_TOOL_PRIORITY)
                changefreq = "monthly"
                urls.append((entry, changefreq, priority))

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


def update_sitemap():
    """Read existing sitemap, merge with discovered URLs, and write back."""
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
