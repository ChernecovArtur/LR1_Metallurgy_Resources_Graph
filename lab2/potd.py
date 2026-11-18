from datetime import date
from pathlib import Path

import requests
from bs4 import BeautifulSoup


API_URL = "https://commons.wikimedia.org/w/api.php"
HEADERS = {
    "User-Agent": "EducationalLab/1.0"
}


def get_json(params):
    response = requests.get(
        API_URL,
        params=params,
        headers=HEADERS,
        timeout=30
    )
    response.raise_for_status()
    return response.json()


date_iso = date.today().isoformat()
caption_title = f"Template:Potd/{date_iso} (en)"
image_title = f"Template:Potd/{date_iso}"

caption_data = get_json({
    "action": "parse",
    "format": "json",
    "formatversion": "2",
    "prop": "text",
    "page": caption_title,
})

caption_html = caption_data["parse"]["text"]
soup = BeautifulSoup(caption_html, "html.parser")
description_tag = soup.find("div", class_="description")

if description_tag:
    description = description_tag.get_text(" ", strip=True)
else:
    description = soup.get_text(" ", strip=True)

image_data = get_json({
    "action": "query",
    "format": "json",
    "formatversion": "2",
    "prop": "images",
    "titles": image_title,
})

filename = image_data["query"]["pages"][0]["images"][0]["title"]

image_info = get_json({
    "action": "query",
    "format": "json",
    "formatversion": "2",
    "prop": "imageinfo",
    "iiprop": "url|extmetadata",
    "titles": filename,
})

info = image_info["query"]["pages"][0]["imageinfo"][0]

if not description:
    description = info.get("extmetadata", {}).get(
        "ImageDescription", {}
    ).get("value", "")
    description = BeautifulSoup(
        description,
        "html.parser"
    ).get_text(" ", strip=True)

image_response = requests.get(
    info["url"],
    headers=HEADERS,
    timeout=60
)
image_response.raise_for_status()

folder = Path(__file__).parent
local_name = filename.removeprefix("File:").replace(" ", "_")
image_path = folder / local_name
description_path = image_path.with_suffix(".txt")

image_path.write_bytes(image_response.content)
description_path.write_text(description, encoding="utf-8")

print(f"Дата: {date_iso}")
print(f"Изображение: {image_path.name}")
print(f"Описание: {description_path.name}")