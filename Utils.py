import requests
from bs4 import BeautifulSoup, SoupStrainer
from datetime import datetime
import hashlib
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

print("Utils.py is loaded")

# Generate SHA-256 hash IDs for each document text
def generate_sha256_id(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

def get_page_source_Selenium(url):
    # Create options for headless mode (optional)
    options = Options()
    options.headless = True  # Run Chrome in headless mode (without opening a window)

    # Manually specify the path to ChromeDriver if it's not in your PATH
    driver = webdriver.Chrome(options=options)

    # Open the target RSS feed page
    driver.get(url)  # Replace this with the URL of your RSS feed

    # Get the page source (the entire HTML of the page)
    page_source = driver.page_source

    # Close the driver
    driver.quit()

    return page_source

def get_page_source_Requests(url):
    # Fetch the raw XML content
    response = requests.get(url)

    return response


def get_soup_from_url_html(url):    
    # Get the page source (the entire HTML of the page)
    page_source = get_page_source_Selenium(url)    

    # Parse the HTML/XML using BeautifulSoup
    soup = BeautifulSoup(page_source, 'html.parser')

    return soup

def get_soup_from_html(html):    
    # Parse the HTML/XML using BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')

    return soup

def get_soup_from_url_xml(url):
    # Fetch the raw XML content
    response = get_page_source_Requests(url)

    # Parse the XML using BeautifulSoup
    soup = BeautifulSoup(response.content, 'xml')

    return soup

def get_pinkbike_article_dict(html_soup):
    title = html_soup.find('div', class_='blog-title').text.strip('\n').strip()
    
    author = html_soup.select_one('div.blog-author a.bold').text
    
    date = html_soup.select_one('div.blog-meta span.f12').text.strip()
    # Define the format
    date_format = '%b %d, %Y'
    # Parse the date
    date = datetime.strptime(date, '%b %d, %Y')
    date = date.strftime('%m-%d-%Y')

    # Find the main blog div
    blog_div = html_soup.select_one('div.blog-body div.blog-section')
    # Remove all divs with the class "media" inside the blog div
    for media in blog_div.find_all('div', class_='media-media-width'):
        media.decompose()  # Decompose removes the tag and its content from the tree
    # Now get all text from the blog div (excluding media divs)
    blog_text = blog_div.get_text(separator=' ',strip=True)  # strip=True removes leading/trailing whitespaces

    return {'title': title, 'author': author, 'date': date, 'text': blog_text, 'sha256': generate_sha256_id(title + ': ' + blog_text)}

def get_pinkbike_article_links_list_from_rss(url):
    # Fetch the raw XML content
    response = requests.get(url)

    # Parse the XML content with BeautifulSoup
    soup = BeautifulSoup(response.content, 'xml')
    #print(soup)

    # Find all <item> tags
    items = soup.find_all('item')

    ret_list = []

    ignore_links_list = ['news/photo-', 'news/video-']
    ignore_titles_list = ['Replay: ']
    
    # Loop through each item and get the <link> inside it
    for item in items:
        title = item.find('title').text
        if any(ig in title for ig in ignore_titles_list):
            print('Ignoring title link:', link)
            continue
        
        link = item.find('link').text  # Extract the link text
        #print(link)
        if any(ig in link for ig in ignore_links_list):
            print('Ignoring link:', link)
            continue

        link = link.removesuffix('?trk=rss')

        ret_list.append(link)
    return ret_list

def get_pinkbike_article_links_list_from_trailforks(url):
    page_source = get_page_source_Selenium(url)
    soup = BeautifulSoup(page_source, 'html.parser', parse_only=SoupStrainer('a'))

    pblinks = []
    ignore_links_list = ['news/photo-', 'news/video-']

    #print(soup)
    pbnewslink = 'https://www.pinkbike.com/news/'
    for link in soup:
        if link.has_attr('href'):
            if pbnewslink in link['href']:
                pbnlink = link['href']
                pbnlink = pbnlink[pbnlink.find(pbnewslink):]
                pbnlink = pbnlink.removesuffix('&source=trailforksweb')

                if any(ig in pbnlink for ig in ignore_links_list):
                    print('Ignoring link:', pbnlink)
                    continue

                pblinks.append(pbnlink)
                
    pblinks = list(set(pblinks))     
    
    return list(set(pblinks))

