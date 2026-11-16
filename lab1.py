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


url = "https://nlmk.com/ru/"

headers = {
    "User-Agent": "Mozilla/5.0 (compatible; EducationalLab/1.0)"
}

response = requests.get(url, headers=headers, timeout=30)
response.raise_for_status()
response.encoding = response.apparent_encoding

Path("cache").mkdir(exist_ok=True)

with open("cache/nlmk.html", "w", encoding="utf-8") as file:
    file.write(response.text)

soup = BeautifulSoup(response.text, "lxml")

for tag in soup(["script", "style", "noscript"]):
    tag.decompose()

parts = []

for tag in soup.find_all(["p", "h1", "h2", "h3", "h4", "h5", "h6", "li"]):
    text = tag.get_text(" ", strip=True)

    if len(text) >= 25:
        parts.append(text)

text = "\n".join(parts)

with open("cache/nlmk.txt", "w", encoding="utf-8") as file:
    file.write(text)

extractor = TermExtractor()
terms = []

for term in extractor(text, limit=30):
    normalized = str(term.normalized).replace("ё", "е")
    terms.append(normalized)

with open("cache/nlmk_terms.txt", "w", encoding="utf-8") as file:
    file.write("\n".join(terms))

print("Размер текста:", len(text))
print("Терминов:", len(terms))
print()

for term in terms:
    print("-", term)