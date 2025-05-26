# tools/scrap_and_filter.py

import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import tldextract
import textwrap
from cohere import Client
from vector_database import build_or_update_vector_db

# Initialize Cohere client
cohere_client = Client('iMLodRM6PlzNKc02QXXDmZb0gMiPLmrXmHGE6FIm')  # Replace with your real key

visited_links = set()

def is_internal_link(base_url, link):
    parsed = urlparse(link)
    if parsed.scheme not in ("http", "https"):
        return False
    base_domain = tldextract.extract(base_url).registered_domain
    link_domain = tldextract.extract(link).registered_domain
    return base_domain == link_domain

def extract_visible_text(soup):
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    return soup.get_text(separator="\n", strip=True)

def scrape_page(url):
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
    except Exception as e:
        print(f"[ERROR] Failed to scrape {url}: {e}")
        return "", []

    soup = BeautifulSoup(resp.text, "html.parser")
    text = extract_visible_text(soup)

    links = []
    for a in soup.find_all("a", href=True):
        href = urljoin(url, a["href"])
        if is_internal_link(url, href):
            links.append(href)
    return text, links

def crawl_website(start_url, max_pages=None):
    if not start_url.startswith(("http://", "https://")):
        start_url = "https://" + start_url

    to_visit = [start_url]
    content_dump = []

    while to_visit and (max_pages is None or len(visited_links) < max_pages):
        url = to_visit.pop(0)
        if url in visited_links:
            continue

        print(f"[INFO] Scraping: {url}")
        text, links = scrape_page(url)
        if text:
            content_dump.append(f"\n--- Page: {url} ---\n{text}\n")
        visited_links.add(url)

        for link in links:
            if link not in visited_links:
                to_visit.append(link)

    os.makedirs("txt", exist_ok=True)
    raw_path = "txt/data_for_chatbot_xalt.txt"
    with open(raw_path, "w", encoding="utf-8") as f:
        f.write("".join(content_dump))
    print(f"[INFO] Raw scraped content saved to {raw_path}")
    return raw_path

def chunk_text(text, max_chunk_size=2000):
    return textwrap.wrap(text, max_chunk_size, break_long_words=False, break_on_hyphens=False)

def clean_text_with_ai(input_text):
    chunks = chunk_text(input_text)
    cleaned_chunks = []

    for i, chunk in enumerate(chunks):
        response = cohere_client.chat(
            model='command-r',
            message=f"""Please clean and reformat the following text without summarizing or removing important information. 
Remove exact duplicate lines, extra spaces, or broken formatting, but preserve the full content as much as possible:\n\n{chunk}"""
        )
        cleaned_chunks.append(response.text.strip())
        print(f"[INFO] Chunk {i+1}/{len(chunks)} cleaned.")

    return "\n\n".join(cleaned_chunks)

def scrape_and_clean_and_vectorize(start_url):
    raw_file = crawl_website(start_url)
    
    with open(raw_file, 'r', encoding='utf-8', errors='ignore') as file:
        raw_text = file.read()

    print("[INFO] Cleaning text using Cohere...")
    cleaned_text = clean_text_with_ai(raw_text)

    cleaned_path = "txt/cleaned_text.txt"
    with open(cleaned_path, 'w', encoding='utf-8') as f:
        f.write(cleaned_text)
    print(f"[✅] Cleaned content saved to {cleaned_path}")

    print("[INFO] Building vector database...")
    build_or_update_vector_db(txt_path=cleaned_path)

if __name__ == "__main__":
    website = input("Enter website URL: ")
    scrape_and_clean_and_vectorize(website)
