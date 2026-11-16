from pathlib import Path

import requests


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

print("Страница загружена")
print("Размер HTML:", len(response.text))
print("Сохранено в cache/nlmk.html")