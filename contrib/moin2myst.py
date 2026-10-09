#!/usr/bin/env python3
"""Convert MoinMoin static HTML wiki pages to Sphinx MyST Markdown.

Usage:
    python contrib/moin2myst.py [--raw-dir moin] [--out-dir converted]

Stages per file:
    1. Extract content from div#content, strip MoinMoin chrome
    2. Decode MoinMoin filename encoding ((20) -> space, (2f) -> /, etc.)
    3. Convert HTML to Markdown via pandoc
"""

# Based on a script by Python Software Foundation
# https://github.com/psf/wiki/blob/main/scripts/convert.py

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import urllib.parse
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from bs4 import BeautifulSoup


PANDOC_RECIPE = [
    "pandoc",
    "--from", "html",
    "--to", "gfm-raw_html",
    "--wrap", "none",
    "--no-highlight",
]

IN_EXT = ".html"
IN_GLOB = "*.html"
OUT_EXT = ".md"
OUT_GLOB = "*.md"

SMILEY_MAP = {
    '(./)': '✅',
    '{X}': '❌',
    '/!\\': '⚠️',
    '<!>': '❗',
    '{i}': 'ℹ️',
}


def decode_moinmoin_filename(filename: str) -> str:
    """Decode MoinMoin (XX) hex encoding to actual characters.

    Examples:
        'Admin(2f)DNS.html' -> 'Admin/DNS'
        'A(20)new(20)module.html' -> 'A new module'
        'boost(2e)python.html' -> 'boost.python'
    """
    stem = filename.removesuffix(IN_EXT)
    decoded = re.sub(
        r"\(([0-9a-fA-F]{2,})\)",
        lambda m: bytes.fromhex(m.group(1)).decode("utf-8", errors="replace"),
        stem,
    )
    return decoded


def sanitize_path(decoded_name: str) -> str:
    """Make decoded name safe for filesystem paths."""
    sanitized = decoded_name \
        .replace(":", "_") \
        .replace("?", "_") \
        .replace("*", "_") \
        .replace('"', "_") \
        .replace("<", "_") \
        .replace(">", "_") \
        .replace("|", "_")
    sanitized = re.sub(r"\s+", " ", sanitized).strip().lower()
    return sanitized


def extract_content(html_path: Path) -> tuple[str, str]:
    """Extract (title, inner_html) from a MoinMoin page."""
    html = html_path.read_text("utf-8", errors="replace")

    # Some pages have unclosed <img> tag, bs4's html.parser incorrectly parses such tags
    soup = BeautifulSoup(html, "html5lib")

    # Title from <title> tag
    title_tag = soup.find("title")
    title = title_tag.text.rsplit(" - ", 1)[0].strip() if title_tag else html_path.stem

    # Content div
    content_div = soup.find("div", id="content")
    if not content_div:
        return title, ""

    # Remove MoinMoin artifacts
    for tag in content_div.find_all("span", class_="anchor"):
        tag.decompose()
    for tag in content_div.find_all("div", id="pagebottom"):
        tag.decompose()
    # Remove inline table of contents (Shibuya sidebar handles this)
    for tag in content_div.find_all("div", class_="table-of-contents"):
        tag.decompose()

    # Convert MoinMoin "Graphical Smileys" into emoji
    # see https://moinmo.in/HelpOnSmileys
    for text, emoji in SMILEY_MAP.items():
        for tag in content_div.find_all("img", alt=text, title=text):
            tag.replace_with(emoji)

    # Return inner HTML only (not the <div id="content"> wrapper)
    return title, content_div.decode_contents()


def html_to_markdown(html_content: str) -> str:
    """Convert HTML fragment to Markdown via pandoc."""
    result = subprocess.run(
        PANDOC_RECIPE,
        input=html_content,
        capture_output=True,
        timeout=30,
        check=False,  # we check exit code manually
        text=True,
    )
    if result.returncode != 0:
        return f"<!-- pandoc error: {result.stderr.strip()} -->\n\n{html_content}"
    output = result.stdout
    # Strip any remaining pandoc attribute blocks that MyST can't parse
    return output


def build_filename_map(raw_dir: Path) -> dict[str, str]:
    """First pass: scan all HTML files, build old_filename -> new_path mapping."""
    mapping = {}
    for html_file in sorted(raw_dir.glob(IN_GLOB)):
        old_name = html_file.name
        decoded = decode_moinmoin_filename(old_name)
        sanitized = sanitize_path(decoded)
        mapping[old_name] = sanitized
        # Also map the URL-decoded variant
        mapping[urllib.parse.quote(old_name, safe="")] = sanitized
    return mapping


def fix_links(markdown: str, filename_map: dict[str, str]) -> str:
    """Rewrite internal wiki links to point to new Markdown paths."""

    def replace_link(match: re.Match) -> str:
        text = match.group(1)
        url = match.group(2)

        # Skip external links, anchors, mailto
        if url.startswith(("http://", "https://", "mailto:", "#", "ftp://")):
            return match.group(0)

        # Separate anchor
        anchor = ""
        if "#" in url:
            url, anchor = url.rsplit("#", 1)
            anchor = "#" + anchor

        # Strip leading ./ or /
        url = url.lstrip("./")

        # URL-decode for lookup
        url_decoded = urllib.parse.unquote(url)

        # Try lookup in filename_map
        for candidate in [url, url_decoded, url + IN_EXT, url_decoded + IN_EXT]:
            if candidate in filename_map:
                new_path = filename_map[candidate]
                return f"[{text}]({new_path}{anchor})"

        return match.group(0)

    return re.sub(r"\[([^\]]*)\]\(([^)]+)\)", replace_link, markdown)


def convert_file(html_file: Path, out_dir: Path, filename_map: dict[str, str]) -> str | None:
    """Convert a single HTML file to Markdown. Returns output path or None on skip."""
    title, html_content = extract_content(html_file)
    if not html_content.strip():
        return None

    markdown = html_to_markdown(html_content)
    markdown = fix_links(markdown, filename_map)

    hide_header = "---\nsd_hide_title: true\n---"
    import_notice = (
        "```{admonition} Legacy Wiki Page\n"
        ":class: note\n\n"
        "This page was migrated from the old MoinMoin-based wiki. "
        "Information may be outdated or no longer applicable. "
        "Be sure to update this page and remove this notice.\n"
        "```"
    )
    markdown = f"{hide_header}\n\n# {title}\n\n{import_notice}\n\n{markdown}"

    # Determine output path
    new_name = filename_map.get(html_file.name, html_file.stem)
    out_path = out_dir / (new_name + OUT_EXT)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(markdown, encoding="utf-8")
    return str(out_path)


def convert_all(raw_dir: Path, out_dir: Path) -> None:
    """Full conversion pipeline."""
    out_dir.mkdir(parents=True, exist_ok=True)

    html_files = sorted(raw_dir.glob(IN_GLOB))
    print(f"Found {len(html_files)} input files")

    print("Building filename map...")
    filename_map = build_filename_map(raw_dir)

    print(f"Converting {len(html_files)} files...")
    converted = 0
    skipped = 0
    workers = os.cpu_count() or 4
    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = {
            executor.submit(convert_file, f, out_dir, filename_map): f
            for f in html_files
        }
        for future in as_completed(futures):
            result = future.result()
            if result:
                converted += 1
            else:
                skipped += 1

    print(f"Converted: {converted}, Skipped: {skipped}")

    print("Done!")


def main() -> None:
    # XXX maybe rip the dirs out, instead convert individual files
    parser = argparse.ArgumentParser(description="Convert MoinMoin HTML to Sphinx Markdown")
    parser.add_argument("--raw-dir", default="moin", help="Path to raw HTML directory")
    parser.add_argument("--out-dir", default="converted", help="Path to output directory")
    args = parser.parse_args()

    raw_dir = Path(args.raw_dir).resolve()
    out_dir = Path(args.out_dir).resolve()

    if not raw_dir.exists():
        print(f"Error: Raw directory {raw_dir} not found.")
        raise SystemExit(1)

    try:
        subprocess.run(["pandoc", "--version"], capture_output=True, check=True)
    except FileNotFoundError:
        print("Error: pandoc not found.")
        sys.exit(1)

    convert_all(raw_dir, out_dir)


if __name__ == "__main__":
    main()
