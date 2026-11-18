import json
from pathlib import Path

import requests


API_URL = "https://ru.wikipedia.org/w/api.php"
HEADERS = {
    "User-Agent": "EducationalLab/1.0"
}


def search_articles(query, limit=35):
    params = {
        "action": "query",
        "format": "json",
        "formatversion": "2",
        "list": "search",
        "srsearch": query,
        "srlimit": limit,
    }

    response = requests.get(
        API_URL,
        params=params,
        headers=HEADERS,
        timeout=30
    )
    response.raise_for_status()

    return response.json()["query"]["search"]


def get_articles(search_results):
    titles = [article["title"] for article in search_results]

    params = {
        "action": "query",
        "format": "json",
        "formatversion": "2",
        "prop": "extracts|links|images|pageimages|pageprops|info",
        "explaintext": "1",
        "pllimit": "max",
        "imlimit": "max",
        "pithumbsize": "500",
        "inprop": "url",
        "titles": "|".join(titles),
    }

    response = requests.get(
        API_URL,
        params=params,
        headers=HEADERS,
        timeout=60
    )
    response.raise_for_status()

    articles = []

    for page in response.json()["query"]["pages"]:
        article = {
            "title": page["title"],
            "url": page.get("fullurl", ""),
            "text": page.get("extract", ""),
            "links": [
                link["title"]
                for link in page.get("links", [])
            ],
            "images": [
                image["title"]
                for image in page.get("images", [])
            ],
            "thumbnail": page.get("thumbnail", {}).get("source"),
            "wikidata_id": page.get("pageprops", {}).get("wikibase_item"),
        }
        articles.append(article)

    return articles


def main():
    query = input("Введите запрос: ")

    search_results = search_articles(query)
    articles = get_articles(search_results)

    result = {
        "query": query,
        "articles": articles,
    }

    output_file = Path(__file__).with_name("wikipedia.json")
    output_file.write_text(
        json.dumps(result, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    print(f"Сохранено статей: {len(articles)}")
    print(f"Файл: {output_file.name}")


if __name__ == "__main__":
    main()