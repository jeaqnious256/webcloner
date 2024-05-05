import os
import sys
from bs4 import BeautifulSoup # type: ignore
import requests
from urllib.parse import urlparse, urljoin

class WebCloner:
    def __init__(self, url):
        self.url = url
        self.domain_name = urlparse(url).netloc
        self.visited_urls = set() 

    def get_full_url(self, path):
        return urljoin(self.url, path)
    
    def valid_url(self, url):
        return urlparse(url).netloc == self.domain_name
    

    def save_page(self, url, path):
        try:
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            f.write(chunk)
        except Exception as e:
            print(f"Error saving {url}: {e}")

    def crawl(self, url=None):
        if url is None:
            url = self.url

        if url in self.visited_urls:
            return

        self.visited_urls.add(url)

        print(f"Visiting {url}")

        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return

        soup = BeautifulSoup(response.text, 'html.parser')

        path = urlparse(url).path
        if not path.endswith('html'):
            path = os.path.join(path, 'index.html')

        self.save_page(url, os.path.join(self.domain_name, path.lstrip('/')))


        for tag, attribute in [('img', 'src'), ('link', 'href'), ('a', 'href')]:
            for resource in soup.find_all(tag):
                if attribute in resource.attrs:
                    resource_url = urljoin(url, resource[attribute])
                    if self.valid_url(resource_url):
                        f_path = os.path.join(self.domain_name, urlparse(resource_url).path.lstrip('/'))
                        self.crawl(resource_url)

                    else:
                        self.save_page(resource_url, f_path)

if len(sys.argv) < 2:
    print("Usage: python webcloner.py <url>")
    sys.exit(1)
    
if __name__ == '__main__':
    url = sys.argv[1]
    clone = WebCloner(url)
    clone.crawl()