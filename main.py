import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time

visited_urls = set()

# Function to extract all the links and other metadata from a page
def get_page_data(url):
    """ Extract all links, title, and meta description from the page """
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)

        # Parse the HTML content of the page
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract page title
        title = soup.title.string if soup.title else 'No Title Found'

        # Extract meta description
        meta_desc = None
        if soup.find("meta", {"name": "description"}):
            meta_desc = soup.find("meta", {"name": "description"}).get("content")
        elif soup.find("meta", {"property": "og:description"}):
            meta_desc = soup.find("meta", {"property": "og:description"}).get("content")

        links = set()
        for anchor in soup.find_all('a', href=True):
            link = anchor['href']

            # Join relative URL with the base URL
            full_url = urljoin(url, link)

            # Only add the URL if it is on the same domain
            if urlparse(full_url).netloc == urlparse(url).netloc:
                links.add(full_url)

        return {
            "url": url,
            "title": title,
            "meta_description": meta_desc,
            "links": links
        }

    except requests.RequestException as e:
        st.error(f"Error fetching the URL: {e}")
        return None

# Function to crawl the website and collect pages with more data
def crawl_website(start_url, max_depth=3):
    """ Recursively crawl the website up to a certain depth, collecting links and metadata """
    urls_to_visit = {start_url}
    all_data = []

    while urls_to_visit:
        url = urls_to_visit.pop()

        if url not in visited_urls:
            visited_urls.add(url)
            st.write(f"Visiting: {url}")
            page_data = get_page_data(url)

            if page_data:
                # Add page data (title, description, links)
                all_data.append(page_data)

                # Add the links to the stack if we haven't visited them yet
                for link in page_data['links']:
                    if link not in visited_urls:
                        urls_to_visit.add(link)

        time.sleep(1)  # Be polite to the server (add a small delay between requests)

    return all_data

# Streamlit UI
st.title("Website Page Crawler")

# Input for the website URL
url = st.text_input("Enter the website URL to crawl", "")

if url:
    st.write(f"Crawling the website: {url}... Please wait.")
    data = crawl_website(url)

    if data:
        st.write("Found the following pages and their metadata:")
        for page in data:
            st.write(f"URL: {page['url']}")
            st.write(f"Title: {page['title']}")
            st.write(f"Meta Description: {page['meta_description'] if page['meta_description'] else 'No meta description found'}")
            st.write(f"Links found on this page:")
            for link in page['links']:
                st.write(link)
            st.write("---")
    else:
        st.write("No pages found or there was an error during crawling.")
