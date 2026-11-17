import argparse
import json

import requests


def search_cdx(keywords, domain, limit):
    collections_response = requests.get(
        "https://index.commoncrawl.org/collinfo.json",
        timeout=30
    )
    collections_response.raise_for_status()

    index_url = collections_response.json()[0]["cdx-api"]

    # Если домен не указан, первое слово как домен
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

    response = requests.get(
        index_url,
        params=params,
        timeout=60
    )
    response.raise_for_status()

    records = []
    for line in response.text.splitlines():
        if line.strip():
            records.append(json.loads(line))

    words = [word.casefold() for word in keywords]
    results = []

    for record in records:
        url = record["url"].casefold()

        if all(word in url for word in words):
            results.append(record)

        if len(results) >= limit:
            break

    return results


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

    for result in results:
        print(result["timestamp"], result["url"])


if __name__ == "__main__":
    main()