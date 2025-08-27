import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import os

# Bạn có thể thêm nhiều domain ở đây
TARGET_URLS = [
    "https://orionshirt.com/",
    # "https://example.com/",
]

MAX_URLS = 200  # tối đa 200 URL / domain

def fetch_urls(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers, timeout=20)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    links = []
    # Selector cho WooCommerce product
    for a in soup.select(".product-small a.woocommerce-LoopProduct-link")[:8]:
        href = a.get("href")
        if href and href not in links:
            links.append(href)

    return links

def save_urls(domain, new_urls):
    filename = f"{domain}.txt"

    try:
        with open(filename, "r", encoding="utf-8") as f:
            existing_urls = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        existing_urls = []

    # Bỏ trùng
    unique_new_urls = [u for u in new_urls if u not in existing_urls]

    # Ghi mới lên đầu
    all_urls = unique_new_urls + existing_urls

    # Giới hạn tối đa
    all_urls = all_urls[:MAX_URLS]

    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(all_urls))

    print(f"[{domain}] Added {len(unique_new_urls)} new URLs. Total: {len(all_urls)}")

if __name__ == "__main__":
    for url in TARGET_URLS:
        domain = urlparse(url).netloc
        urls = fetch_urls(url)
        print(f"[{domain}] Found:", urls)
        save_urls(domain, urls)

