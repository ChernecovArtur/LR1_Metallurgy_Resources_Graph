import argparse
import json
from io import BytesIO
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from tabulate import tabulate
from warcio.archiveiterator import ArchiveIterator


INDEX_URL = "https://index.commoncrawl.org/CC-MAIN-2025-30-index"
CACHE_FILE = Path(__file__).with_name("cdx_cache.json")


def search_cdx(keywords, domain, limit):
    url_pattern = domain or keywords[0]

    params = {
        "url": url_pattern,
        "matchType": "domain",
        "output": "json",
        "filter": ["status:200", "mime:text/html"],
        "fl": "url,timestamp,filename,offset,length",
        "collapse": "urlkey",
        "limit": limit * 10,
    }

    records = None

    try:
        response = requests.get(
            INDEX_URL,
            params=params,
            timeout=15
        )
        response.raise_for_status()

        records = []
        for line in response.text.splitlines():
            if line.strip():
                records.append(json.loads(line))

        if records:
            CACHE_FILE.write_text(
                json.dumps(records, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )

    except (requests.RequestException, json.JSONDecodeError):
        print("CDX недоступен, использую сохранённый ответ")

    if records is None:
        if not CACHE_FILE.exists():
            return []

        records = json.loads(
            CACHE_FILE.read_text(encoding="utf-8")
        )

    words = [word.casefold() for word in keywords]
    domain_text = (domain or "").casefold().strip("/")
    results = []

    for record in records:
        url = record["url"].casefold()

        if domain_text and domain_text not in url:
            continue

        if all(word in url for word in words):
            results.append(record)

        if len(results) >= limit:
            break

    return results


def load_page(record):
    offset = int(record["offset"])
    length = int(record["length"])
    end = offset + length - 1

    warc_url = "https://data.commoncrawl.org/" + record["filename"]

    response = requests.get(
        warc_url,
        headers={"Range": f"bytes={offset}-{end}"},
        timeout=20
    )
    response.raise_for_status()

    archive = ArchiveIterator(BytesIO(response.content))

    for warc_record in archive:
        if warc_record.rec_type != "response":
            continue

        html = warc_record.content_stream().read()
        soup = BeautifulSoup(html, "html.parser")

        if soup.title:
            title = soup.title.get_text(" ", strip=True)
        else:
            title = "—"

        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()

        text = soup.get_text(" ", strip=True)
        return title, text

    return "—", ""


def main():
    parser = argparse.ArgumentParser(description="Поиск в Common Crawl")

    parser.add_argument(
        "keywords",
        nargs="+",
        help="Ключевые слова"
    )

    parser.add_argument(
        "--domain",
        help="Домен"
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Число результатов"
    )

    parser.add_argument(
        "--show-text",
        action="store_true",
        help="Показать текст страницы"
    )

    args = parser.parse_args()

    results = search_cdx(args.keywords, args.domain, args.limit)

    if not results:
        print("Ничего не найдено")
        return

    headers = ["URL", "Дата архивации", "Заголовок"]
    widths = [50, 14, 35]

    if args.show_text:
        headers.append("Фрагмент текста")
        widths.append(50)

    rows = []

    for result in results:
        timestamp = result["timestamp"]
        date = f"{timestamp[:4]}-{timestamp[4:6]}-{timestamp[6:8]}"

        row = [result["url"], date]

        if args.show_text:
            try:
                title, text = load_page(result)
                fragment = text[:200]
            except Exception:
                title = "—"
                fragment = "WARC сейчас недоступен"

            row.extend([title, fragment])
        else:
            row.append("—")

        rows.append(row)

    print(
        tabulate(
            rows,
            headers=headers,
            tablefmt="grid",
            maxcolwidths=widths
        )
    )


if __name__ == "__main__":
    main()