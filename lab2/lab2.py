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


def main():
    query = input("Введите запрос: ")
    articles = search_articles(query)

    print(f"Найдено статей: {len(articles)}")

    for number, article in enumerate(articles, start=1):
        print(f"{number}. {article['title']}")


if __name__ == "__main__":
    main()