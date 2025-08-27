import requests
from bs4 import BeautifulSoup

URL = "https://orionshirt.com/"
OUTPUT_FILE = "latest.txt"

def fetch_urls():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    r = requests.get(URL, headers=headers, timeout=15)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    links = []
    # Lấy tối đa 8 sản phẩm mới nhất từ NEW ARRIVALS
    for a in soup.select(".product-small a.woocommerce-LoopProduct-link")[:8]:
        href = a.get("href")
        if href and href not in links:
            links.append(href)

    return links

def save_urls(urls):
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(urls))

if __name__ == "__main__":
    urls = fetch_urls()
    save_urls(urls)
