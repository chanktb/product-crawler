import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import os
import json

MAX_URLS = 500

def load_config():
    """Tải cấu hình từ tệp config.json."""
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Lỗi: Không tìm thấy tệp config.json!")
        return []

def fetch_urls(url_data):
    """
    Tải và phân tích các URL từ một trang web.
    Sử dụng selector được cung cấp trong cấu hình.
    """
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(url_data['url'], headers=headers, timeout=20)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
    except requests.exceptions.RequestException as e:
        print(f"Lỗi khi truy cập {url_data['url']}: {e}")
        return []

    links = []
    # Lấy tất cả các URL, không giới hạn
    for a in soup.select(url_data['selector']):
        href = a.get("href")
        if href and href not in links:
            links.append(href)

    return links

def save_urls(domain, new_urls):
    """Lưu các URL vào tệp của domain tương ứng và trả về số URL mới và tổng số URL."""
    filename = f"{domain}.txt"

    try:
        with open(filename, "r", encoding="utf-8") as f:
            existing_urls = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        existing_urls = []

    unique_new_urls = [u for u in new_urls if u not in existing_urls]

    all_urls = unique_new_urls + existing_urls

    all_urls = all_urls[:MAX_URLS]

    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(all_urls))

    print(f"[{domain}] Added {len(unique_new_urls)} new URLs. Total: {len(all_urls)}")
    # Trả về cả số lượng URL mới và tổng số URL
    return len(unique_new_urls), len(all_urls)

if __name__ == "__main__":
    TARGET_URLS = load_config()
    if not TARGET_URLS:
        exit(1)

    # Lưu cả số lượng URL mới và tổng số URL
    urls_summary = {}

    # Vòng lặp chính để crawl và lưu URL
    for url_data in TARGET_URLS:
        domain = urlparse(url_data['url']).netloc
        urls = fetch_urls(url_data)
        print(f"[{domain}] Found:", urls)
        new_urls_count, total_urls_count = save_urls(domain, urls)
        urls_summary[domain] = {'new_count': new_urls_count, 'total_count': total_urls_count}

    # Ghi tóm tắt vào last_file.txt
    with open("last_file.txt", "w", encoding="utf-8") as f:
        f.write("--- Summary of URLs ---\n")
        for domain, counts in urls_summary.items():
            f.write(f"{domain}: {counts['new_count']} new URLs added. Total {counts['total_count']} URLs.\n")

    print("\n--- Summary saved to last_file.txt ---")
