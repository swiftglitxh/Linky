# ╔════════════════════════════════════════════════════════════════════╗
# ║   SCRIPT NAME : target.py                                          ║
# ║   DESCRIPTION : Fetches a URL, extracts links, optionally brute-   ║
# ║                 forces paths from a wordlist, using Rich output    ║
# ║                                                                    ║
# ║   IMPORTS USED :                                                   ║
# ║     - argparse                        (CLI argument parsing)       ║
# ║     - requests                        (HTTP requests)              ║
# ║     - bs4.BeautifulSoup               (HTML parsing)               ║
# ║     - urllib.parse.urljoin            (resolve relative links)     ║
# ║     - rich.console.Console            (styled console output)      ║
# ║     - rich.table.Table                (tabular display)            ║
# ║     - rich.prompt.Prompt              (interactive user input)     ║
# ║                                                                    ║
# ║   AUTHOR  : SwiftGlitxh                                            ║
# ║   CREATED : 2026-10-17                                             ║
# ║   STATUS  : In Progress                                            ║
# ╚════════════════════════════════════════════════════════════════════╝

import argparse
import sys
from time import sleep

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt

console = Console()


def banner():
    console.print("""[cyan]
██╗     ██╗███╗   ██╗██╗  ██╗██╗   ██╗
██║     ██║████╗  ██║██║ ██╔╝╚██╗ ██╔╝
██║     ██║██╔██╗ ██║█████╔╝  ╚████╔╝
██║     ██║██║╚██╗██║██╔═██╗   ╚██╔╝
███████╗██║██║ ╚████║██║  ██╗   ██║
╚══════╝╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝   ╚═╝
""")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Fetch a URL, scrape its links, and optionally brute-force paths from a wordlist."
    )
    parser.add_argument("-u", "--url", help="Target URL (prompted if omitted)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("-o", "--output", help="Save results to this file")
    parser.add_argument("-w", "--wordlist", help="Path to a wordlist file to brute-force against the target URL")
    return parser.parse_args()


def scrape_links(target_url, verbose=False):
    r = requests.get(target_url, timeout=5)

    if r.status_code == 200:
        console.print(f"🟢 STATUS: [green]{r.status_code} OK")
        soup = BeautifulSoup(r.text, "html.parser")
        links = []

        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            full_url = urljoin(target_url, href)
            text = a_tag.get_text(strip=True) or "(no text)"
            links.append((text, full_url))
            if verbose:
                console.print(f"[dim]found: {full_url}")

        return links

    elif r.status_code == 404:
        console.print(f"🔴 STATUS: [red]{r.status_code} Not Found")
    else:
        console.print(f"🟡 STATUS: [yellow]{r.status_code}")

    return []


def brute_force_wordlist(target_url, wordlist_path, verbose=False):
    console.print(f"📂[cyan] Running wordlist: [white]{wordlist_path}")

    try:
        with open(wordlist_path, "r", encoding="utf-8", errors="ignore") as f:
            words = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        console.print(f"⚠️  [red]Wordlist not found: {wordlist_path}")
        return []

    found = []
    base = target_url.rstrip("/") + "/"

    for word in words:
        full_url = urljoin(base, word)
        try:
            r = requests.get(full_url, timeout=5)
            if verbose:
                console.print(f"[dim]{r.status_code} -> {full_url}")
            if r.status_code == 200:
                found.append((word, full_url, r.status_code))
                console.print(f"🟢 [green]{r.status_code}[/green] {full_url}")
        except requests.exceptions.RequestException:
            if verbose:
                console.print(f"[dim red]failed -> {full_url}")
            continue

    return found


def render_table(title, columns, rows):
    table = Table(title=title, show_lines=True)
    for col in columns:
        table.add_column(col, style="cyan" if col == columns[0] else "white")
    for row in rows:
        table.add_row(*[str(v) for v in row])
    console.print(table)


def save_output(path, lines):
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    console.print(f"💾 [green]Saved results to {path}")


def main():
    banner()
    args = parse_args()

    target_url = args.url or Prompt.ask("[cyan]🎯 Enter target URL")
    console.print(f"""💀[cyan] TARGET:[white] {target_url}""")

    output_lines = []

    try:
        if args.wordlist:
            results = brute_force_wordlist(target_url, args.wordlist, verbose=args.verbose)
            if results:
                render_table("Wordlist Hits", ["Word", "URL", "Status"], results)
                output_lines = [f"{status} {url}" for _, url, status in results]
            else:
                console.print("[yellow]No matching paths found.")

        else:
            links = scrape_links(target_url, verbose=args.verbose)
            if links:
                render_table(f"Links found on {target_url}", ["Link Text", "URL"], links)
                output_lines = [url for _, url in links]
            else:
                console.print("[yellow]No links found on this page.")

        if args.output and output_lines:
            save_output(args.output, output_lines)

    except requests.exceptions.RequestException as e:
        console.print(f"⚠️  [red]Request failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
