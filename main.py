import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time

# Set to avoid revisiting URLs
visited_urls = set()

def get_all_links(url):
    """ Get all the links on the page """
    response = requests.get(url)
    if response.status_code != 200:
        return []

    # Parse the HTML content of the page
    soup = BeautifulSoup(response.text, 'html.parser')
    
    links = set()
    for anchor in soup.find_all('a', href=True):
        link = anchor['href']
        
        # Join relative URL with the base URL
        full_url = urljoin(url, link)
        
        # Only add the URL if it is on the same domain
        if urlparse(full_url).netloc == urlparse(url).netloc:
            links.add(full_url)
    
    return links

def crawl_website(start_url, max_depth=3):
    """ Recursively crawl the website up to a certain depth """
    urls_to_visit = {start_url}
    all_links = set()
    
    while urls_to_visit:
        url = urls_to_visit.pop()
        
        if url not in visited_urls:
            visited_urls.add(url)
            print(f"Visiting: {url}")
            links = get_all_links(url)
            all_links.update(links)
            
            # Add the links to the stack if we haven't visited them yet
            for link in links:
                if link not in visited_urls:
                    urls_to_visit.add(link)
        
        # Limit the crawl depth to avoid unnecessary recursion
        time.sleep(1)  # Be polite to the server (don't hit it too fast)

    return all_links

if __name__ == "__main__":
    start_url = "https://chatgpt.com"  # Change this to the website you want to crawl
    print("Crawling the website...")
    pages = crawl_website(start_url)
    
    print("\nCrawl completed. Found the following pages:")
    for page in pages:
        print(page)
