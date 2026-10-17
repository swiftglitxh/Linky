# Linky — target.py
<img width="2048" height="768" alt="image" src="https://github.com/user-attachments/assets/160f9117-eabc-4271-b3f8-cdf223021fde" />

A command-line recon tool that fetches a target URL, scrapes all links from the page, and can optionally brute-force paths against a wordlist. Output is styled with [Rich](https://github.com/Textualize/rich) for readable terminal tables.

## Features

- **Link scraping** — parses a target page's HTML and extracts every `<a href>` link, resolving relative URLs to absolute ones.
- **Wordlist brute-forcing** — appends each line of a wordlist to the target URL and reports which paths return a `200 OK`.
- **Status-aware output** — color-coded status reporting (green for `200`, red for `404`, yellow for anything else).
- **Rich tables** — results are rendered in bordered, line-divided tables instead of raw console dumps.
- **File output** — save found links or wordlist hits to a text file.
- **Verbose mode** — see every request made, not just successful hits.

## Requirements

- Python 3.8+
- [`requests`](https://pypi.org/project/requests/)
- [`beautifulsoup4`](https://pypi.org/project/beautifulsoup4/)
- [`rich`](https://pypi.org/project/rich/)

Install dependencies:

```bash
pip install requests beautifulsoup4 rich
```

## Usage

```bash
python target.py [-u URL] [-v] [-o OUTPUT] [-w WORDLIST]
```

### Arguments

| Flag | Long form | Description |
|------|-----------|--------------|
| `-u` | `--url` | Target URL. If omitted, you'll be prompted for it interactively. |
| `-v` | `--verbose` | Print every request made (including misses and failures), not just hits. |
| `-o` | `--output` | Save results (found links or wordlist hits) to the given file, one per line. |
| `-w` | `--wordlist` | Path to a wordlist file. When set, the tool brute-forces paths against the target instead of scraping links. |

### Examples

**Interactive mode — prompts for a URL, scrapes links:**

```bash
python target.py
```

**Scrape links from a specific URL, with verbose logging:**

```bash
python target.py -u https://example.com -v
```

**Brute-force a wordlist against the target and save hits to a file:**

```bash
python target.py -u https://example.com -w wordlist.txt -o results.txt -v
```

## How it works

1. Displays the banner and resolves the target URL (from `-u` or an interactive prompt).
2. Sends a `GET` request to the target with a 5-second timeout.
3. Based on the response status:
   - `200` → proceeds to either link-scraping or wordlist brute-forcing.
   - `404` → reports "Not Found" and stops.
   - Any other code → reports the status and stops.
4. **Link mode** (default): parses the HTML with BeautifulSoup, extracts all anchor tags, resolves relative links with `urljoin`, and displays them in a table.
5. **Wordlist mode** (`-w`): reads each line of the wordlist, requests `<target>/<word>`, and reports any path that returns `200`.
6. If `-o` is set, results are written to the specified file.

## Notes & Limitations

- Requests are sent **sequentially**, not concurrently — large wordlists will be slow. Consider adding threading (e.g. `concurrent.futures`) if you need speed.
- There's no built-in rate limiting or delay between requests in wordlist mode — add one if you need to be gentler on a target.
- `-w` mode only checks for `200` responses; it doesn't currently report other interesting codes like `301`/`403`.

## ⚠️ Responsible use

Only run the link-scraping or wordlist brute-force modes against targets you own or are explicitly authorized to test. Unsolicited scanning, path enumeration, or crawling of systems without permission may violate a site's terms of service or applicable computer-access laws, depending on your jurisdiction.

## Author

`<your name here>`
