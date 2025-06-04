# tools/scrap_and_filter.py

import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import tldextract
import textwrap
from cohere import Client
from vector_database import build_or_update_vector_db
#from utils.file_merge_utils import merge_txt_files

# --- Load Cohere API key securely ---
COHERE_API_KEY = os.getenv("COHERE_API_KEY", "your-default-api-key")  # Replace fallback with dummy if desired
cohere_client = Client(COHERE_API_KEY)

visited_links = set()

def is_internal_link(base_url, link):
    """Check if a link belongs to the same domain as the base URL."""
    parsed = urlparse(link)
    if parsed.scheme not in ("http", "https"):
        return False
    base_domain = tldextract.extract(base_url).registered_domain
    link_domain = tldextract.extract(link).registered_domain
    return base_domain == link_domain

def extract_visible_text(soup):
    """Extract only visible text from a parsed HTML document."""
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    return soup.get_text(separator="\n", strip=True)

def scrape_page(url):
    """Download and extract text and internal links from a single web page."""
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

def crawl_website(start_url, max_pages=None, output_path="txt/webscraper.txt"):
    """Recursively crawl internal pages starting from a URL and save text."""
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
            if link not in visited_links and link not in to_visit:
                to_visit.append(link)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("".join(content_dump))

    print(f"[INFO] Raw scraped content saved to {output_path}")
    return output_path

def chunk_text(text, max_chunk_size=2000):
    """Split long text into manageable chunks for AI processing."""
    return textwrap.wrap(text, max_chunk_size, break_long_words=False, break_on_hyphens=False)

def clean_text_with_ai(input_text):
    """Use Cohere to clean and reformat large text input chunk-by-chunk."""
    chunks = chunk_text(input_text)
    cleaned_chunks = []

    for i, chunk in enumerate(chunks):
        try:
            response = cohere_client.chat(
                model='command-r',
                message=(
                    "Please clean and reformat the following text without summarizing or removing important information. "
                    "Remove exact duplicate lines, extra spaces, or broken formatting, but preserve the full content:\n\n" + chunk
                )
            )
            cleaned_chunks.append(response.text.strip())
            print(f"[INFO] Chunk {i + 1}/{len(chunks)} cleaned.")
        except Exception as e:
            print(f"[ERROR] Failed to clean chunk {i + 1}: {e}")

    return "\n\n".join(cleaned_chunks)

def scrape_and_clean_and_vectorize(start_url):
    """Main pipeline: scrape > clean with AI > merge > vectorize."""
    raw_file = crawl_website(start_url)

    with open(raw_file, 'r', encoding='utf-8', errors='ignore') as f:
        raw_text = f.read()

    print("[INFO] Cleaning text using Cohere...")
    cleaned_text = clean_text_with_ai(raw_text)

    cleaned_path = "txt/cleaned_text.txt"
    with open(cleaned_path, 'w', encoding='utf-8') as f:
        f.write(cleaned_text)

    print(f"[✅] Cleaned content saved to {cleaned_path}")

    merged_path = merge_txt_files(
        folder_path = "txt",
        output_filename="datafile.txt",
        exclude_filenames=["webscraper.txt", "cleaned_text.txt", "merged.txt"]
        )
    
    print(f"[INFO] Merged txt files saved to {merged_path}")

    print("[INFO] Building vector database with merged content...")
    build_or_update_vector_db(txt_path=merged_path)

if __name__ == "__main__":
    website = input("Enter website URL: ")
    scrape_and_clean_and_vectorize(website)
