import urllib.request
import json
import threading
import time
from bs4 import BeautifulSoup

competitors = {}
lock = threading.Lock()


def fetch_html(url):
    """
    Fetch the HTML content of a given URL.
    """
    try:
        with urllib.request.urlopen(url) as response:
            return response.read()
        
    except Exception:
        return None


def scrape_competitor(competitor_id):
    """
    Scrape a single competitor's details.
    """
    url = f"https://sonkal.cz/osobni_karta/{competitor_id}"
    
    html = fetch_html(url)
    if not html:
        print(f"Skipping ID {competitor_id}: No response")
        return
    
    soup = BeautifulSoup(html, 'html.parser')
    name_tag = soup.find("h2")
    if name_tag:
        full_name = name_tag.text.strip()
    
        name_parts = full_name.split(" ", 1)
        first_name = name_parts[0].strip()
        last_name = name_parts[1].strip() if len(name_parts) > 1 else ""
    
        with lock:
            competitors[full_name] = {"id": competitor_id, "first_name": first_name, "last_name": last_name}
    
        print(f"Found: {full_name} - ID: {competitor_id}")
    
    else:
        print(f"Skipping ID {competitor_id}: No competitor found")
    
    time.sleep(0.1)  


def scrape_competitors(start_id=1, end_id=750, max_threads=10, output_file="competitors.json"):
    """
    Scrape competitor names using a limited number of threads.
    """
    threads = []
    
    for competitor_id in range(start_id, end_id + 1):
        while threading.active_count() >= max_threads:
            time.sleep(0.1)  

        thread = threading.Thread(target=scrape_competitor, args=(competitor_id,))
        threads.append(thread)
        thread.start()

    for t in threads:
        t.join()

    print("All threads where closed.")

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(competitors, f, ensure_ascii=False, indent=4)
    
    print(f"Scraped {len(competitors)} competitors and saved to {output_file}.")
    return competitors

if __name__ == "__main__":
    scrape_competitors()