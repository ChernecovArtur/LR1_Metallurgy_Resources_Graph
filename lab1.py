from pathlib import Path

import requests
from bs4 import BeautifulSoup


url = "https://nlmk.com/ru/"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(url, headers=headers, timeout=30)
response.raise_for_status()
response.encoding = response.apparent_encoding

Path("cache").mkdir(exist_ok=True)

with open("cache/nlmk.html", "w", encoding="utf-8") as file:
    file.write(response.text)

soup = BeautifulSoup(response.text, "lxml")

# Это нам не нужно
for tag in soup(["script", "style", "noscript"]):
    tag.decompose()

parts = []

for tag in soup.find_all(["p", "h1", "h2", "h3", "h4", "h5", "h6", "li"]):
    text = tag.get_text(" ", strip=True)

    # Отбрасываем совсем короткие куски
    if len(text) >= 25:
        parts.append(text)

text = "\n".join(parts)

with open("cache/nlmk.txt", "w", encoding="utf-8") as file:
    file.write(text)

print("Текст извлечён")
print("Размер текста:", len(text))
print()
print(text[:1000])