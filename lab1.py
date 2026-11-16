import csv
import inspect
from collections import namedtuple
from pathlib import Path

import requests
from bs4 import BeautifulSoup


if not hasattr(inspect, "getargspec"):
    ArgSpec = namedtuple("ArgSpec", "args varargs keywords defaults")

    def getargspec(func):
        spec = inspect.getfullargspec(func)
        return ArgSpec(spec.args, spec.varargs, spec.varkw, spec.defaults)

    inspect.getargspec = getargspec

from rutermextract import TermExtractor


HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; EducationalLab/1.0)"
}


def get_text(url, resource_id):
    """Скачивает страницу и забирает текст из нужных тегов."""
    cache_dir = Path("cache")
    cache_dir.mkdir(exist_ok=True)

    html_file = cache_dir / f"{resource_id}.html"

    if html_file.exists():
        html = html_file.read_text(encoding="utf-8")
    else:
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        response.encoding = response.apparent_encoding
        html = response.text
        html_file.write_text(html, encoding="utf-8")

    soup = BeautifulSoup(html, "lxml")

    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    parts = []

    for tag in soup.find_all(["p", "h1", "h2", "h3", "h4", "h5", "h6", "li"]):
        text = tag.get_text(" ", strip=True)

        if len(text) >= 25:
            parts.append(text)

    return "\n".join(parts)


def get_terms(text, extractor):
    terms = []

    for term in extractor(text, limit=40):
        normalized = str(term.normalized).replace("ё", "е")
        terms.append(normalized)

    return terms


def main():
    with open("sources.csv", encoding="utf-8-sig") as file:
        sources = list(csv.DictReader(file))

    extractor = TermExtractor()
    results = []
    errors = []

    for source in sources:
        try:
            text = get_text(source["url"], source["id"])
            terms = get_terms(text, extractor)

            if len(text) < 500 or len(terms) < 10:
                raise ValueError("Мало текста или терминов")

            results.append({
                "id": source["id"],
                "title": source["title"],
                "url": source["url"],
                "terms": "; ".join(terms),
            })
        except Exception as error:
            errors.append({
                "id": source["id"],
                "title": source["title"],
                "url": source["url"],
                "error": str(error),
            })

    with open("terms.csv", "w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["id", "title", "url", "terms"])
        writer.writeheader()
        writer.writerows(results)

    with open("errors.csv", "w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["id", "title", "url", "error"])
        writer.writeheader()
        writer.writerows(errors)

    print(f"Готово: {len(results)} ресурсов, ошибок: {len(errors)}")


if __name__ == "__main__":
    main()