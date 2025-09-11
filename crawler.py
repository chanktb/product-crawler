import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import os
import json
from datetime import datetime
import pytz

MAX_URLS = 1000
# Ngưỡng để chạy toàn bộ
FULL_RUN_THRESHOLD = 5 
COUNTER_FILE = "run_counter.json"

def load_config():
    # ... (giữ nguyên hàm này)
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Lỗi: Không tìm thấy tệp config.json!")
        return []

def fetch_urls(url_data):
    # ... (giữ nguyên hàm này)
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(url_data['url'], headers=headers, timeout=20)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
    except requests.exceptions.RequestException as e:
        print(f"Lỗi khi truy cập {url_data['url']}: {e}")
        return []
    links = []
    for a in soup.select(url_data['selector']):
        href = a.get("href")
        if href and href not in links:
            links.append(href)
    return links

def save_urls(domain, new_urls):
    # ... (giữ nguyên hàm này)
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
    return len(unique_new_urls), len(all_urls)

def read_counter():
    """Đọc số đếm từ file."""
    try:
        with open(COUNTER_FILE, 'r') as f:
            data = json.load(f)
            return data.get("priority_runs_count", 0)
    except (FileNotFoundError, json.JSONDecodeError):
        return 0

def write_counter(count):
    """Ghi số đếm mới vào file."""
    with open(COUNTER_FILE, 'w') as f:
        json.dump({"priority_runs_count": count}, f, indent=2)

if __name__ == "__main__":
    TARGET_URLS = load_config()
    if not TARGET_URLS:
        exit(1)

    urls_summary = {}
    
    # Đọc số lần chạy ưu tiên đã thực hiện
    run_count = read_counter()
    print(f"--- Current priority run count: {run_count}/{FULL_RUN_THRESHOLD} ---")

    # Tách các URL
    priority_url_data = None
    other_urls_data = []
    for url_data in TARGET_URLS:
        if url_data.get("priority"):
            priority_url_data = url_data
        else:
            other_urls_data.append(url_data)

    # Quyết định chế độ chạy
    is_full_run = (run_count >= FULL_RUN_THRESHOLD)

    # Luôn chạy trang priority trước
    if priority_url_data:
        try:
            domain = urlparse(priority_url_data['url']).netloc
            urls = fetch_urls(priority_url_data)
            new_urls, total_urls = save_urls(domain, urls)
            urls_summary[domain] = {'new_count': new_urls, 'total_count': total_urls}
        except Exception as e:
            print(f"!!! LỖI NGHIÊM TRỌNG khi xử lý priority URL: {e}")

    # Nếu là "full run" thì chạy các trang còn lại
    if is_full_run:
        print("\n--- Threshold reached. Performing a full run for all domains. ---")
        for url_data in other_urls_data:
            try:
                domain = urlparse(url_data['url']).netloc
                urls = fetch_urls(url_data)
                new_urls, total_urls = save_urls(domain, urls)
                urls_summary[domain] = {'new_count': new_urls, 'total_count': total_urls}
            except Exception as e:
                print(f"!!! LỖI NGHIÊM TRỌNG khi xử lý {url_data.get('url', 'URL không xác định')}: {e}")
        
        # Reset bộ đếm sau khi chạy full run
        write_counter(0)
    else:
        print("\n--- Priority-only run. Skipping other domains. ---")
        # Tăng bộ đếm
        write_counter(run_count + 1)

    # Ghi tóm tắt (nếu có)
    if urls_summary:
        vn_timezone = pytz.timezone('Asia/Ho_Chi_Minh')
        timestamp = datetime.now(vn_timezone).strftime('%Y-%m-%d %H:%M:%S %Z')
        with open("last_file.txt", "w", encoding="utf-8") as f:
            f.write("--- Summary of Last Product Crawl ---\n")
            f.write(f"Generated at: {timestamp}\n\n")
            for domain, counts in sorted(urls_summary.items()):
                f.write(f"{domain}: {counts['new_count']} new URLs added. Total {counts['total_count']} URLs.\n")
        print("\n--- Summary saved to last_file.txt ---")
