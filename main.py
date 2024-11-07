import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time

visited_urls = set()

# Function to extract all the links from a page
def get_all_links(url):
    """ Get all the links on the page """
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)

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

    except requests.RequestException as e:
        st.error(f"Error fetching the URL: {e}")
        return []

# Function to crawl the website and collect pages
def crawl_website(start_url, max_depth=3):
    """ Recursively crawl the website up to a certain depth """
    urls_to_visit = {start_url}
    all_links = set()

    while urls_to_visit:
        url = urls_to_visit.pop()

        if url not in visited_urls:
            visited_urls.add(url)
            st.write(f"Visiting: {url}")
            links = get_all_links(url)
            all_links.update(links)

            # Add the links to the stack if we haven't visited them yet
            for link in links:
                if link not in visited_urls:
                    urls_to_visit.add(link)

        time.sleep(1)  # Be polite to the server (add a small delay between requests)

    return all_links

# Streamlit UI
st.title("Website Page Crawler")

# Input for the website URL
url = st.text_input("Enter the website URL to crawl", "")

if url:
    st.write(f"Crawling the website: {url}... Please wait.")
    pages = crawl_website(url)

    if pages:
        st.write("Found the following pages:")
        for page in pages:
            st.write(page)
    else:
        st.write("No pages found or there was an error during crawling.")
