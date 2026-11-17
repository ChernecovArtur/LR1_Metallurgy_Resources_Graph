import argparse


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
    print(args)


if __name__ == "__main__":
    main()