import requests
from bs4 import BeautifulSoup

URL = "https://example.com"  # thay bằng site của bạn
OUTPUT_FILE = "latest.txt"

def fetch_urls():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    r = requests.get(URL, headers=headers, timeout=10)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    links = []
    # chỉnh selector cho đúng với site bạn
    for a in soup.select("a.product-link")[:8]:
        href = a.get("href")
        if href:
            if href.startswith("/"):
                href = URL.rstrip("/") + href
            links.append(href)

    return links

def save_urls(urls):
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(urls))

if __name__ == "__main__":
    urls = fetch_urls()
    save_urls(urls)
