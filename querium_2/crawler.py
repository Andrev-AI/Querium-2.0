import requests
from bs4 import BeautifulSoup
from urllib.robotparser import RobotFileParser
from urllib.parse import urljoin, urlparse
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Crawler:
    def __init__(self, start_url, max_depth=3, max_pages=100, max_workers=10, selenium_workers=2, save_interval=10):
        self.start_url = start_url
        self.max_depth = max_depth
        self.max_pages = max_pages
        self.visited = set()
        self.results = []
        self.robot_parsers = {}
        self.max_workers = max_workers
        self.selenium_workers = selenium_workers
        self.save_interval = save_interval
        self.pages_crawled = 0
        self.session = requests.Session()
        retries = Retry(total=5, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])
        self.session.mount('http://', HTTPAdapter(max_retries=retries))
        self.session.mount('https://', HTTPAdapter(max_retries=retries))
        self.selenium_pool = []

    def init_selenium(self):
        options = Options()
        options.add_argument("-headless")
        options.set_preference("network.cookie.cookieBehavior", 0)  # Accept all cookies
        driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=options)
        return driver

    def accept_cookies(self, driver):
        try:
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Accept') or contains(text(), 'Aceitar')]"))
            ).click()
        except:
            logging.info("No cookie acceptance button found or not clickable")

    def fetch_page(self, url, use_selenium=False):
        if use_selenium:
            driver = self.selenium_pool.pop()
            try:
                driver.get(url)
                self.accept_cookies(driver)
                html = driver.page_source
                return html
            except Exception as e:
                logging.error(f"Selenium request failed: {e}")
                return None
            finally:
                self.selenium_pool.append(driver)
        else:
            try:
                response = self.session.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
                if response.status_code == 200:
                    return response.text
                else:
                    return None
            except requests.RequestException as e:
                logging.error(f"Request failed: {e}")
                return None

    def parse_robots(self, url):
        parsed_url = urlparse(url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        if base_url not in self.robot_parsers:
            robots_url = urljoin(base_url, "/robots.txt")
            rp = RobotFileParser()
            rp.set_url(robots_url)
            try:
                rp.read()
            except Exception as e:
                logging.error(f"Failed to read robots.txt: {e}")
            self.robot_parsers[base_url] = rp
        return self.robot_parsers[base_url]

    def is_allowed(self, url):
        rp = self.parse_robots(url)
        return rp.can_fetch("*", url)

    def extract_info(self, url, html):
        soup = BeautifulSoup(html, 'html.parser')
        title = soup.find('title').text.strip() if soup.find('title') else 'No Title'
        text = ' '.join([p.text.strip() for p in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])])
        links = list(set([urljoin(url, a['href']) for a in soup.find_all('a', href=True)]))
        
        pub_time = None
        meta_time = soup.find('meta', property='article:published_time')
        if meta_time:
            pub_time = meta_time['content']
        else:
            for name in ['pubdate', 'publishdate', 'timestamp', 'date']:
                meta = soup.find('meta', attrs={'name': name})
                if meta:
                    pub_time = meta['content']
                    break
        
        if pub_time:
            try:
                pub_time = datetime.fromisoformat(pub_time).isoformat()
            except ValueError:
                logging.warning(f"Could not parse publication time: {pub_time}")
                pub_time = None

        return {
            'url': url,
            'title': title,
            'text': text,
            'links': links,
            'pub_time': pub_time,
            'crawl_time': datetime.now().isoformat()
        }

    def save_results(self, filename='results.json'):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=4, ensure_ascii=False)
        logging.info(f"Saved {len(self.results)} results to {filename}")
        self.results.clear()

    def crawl(self, url, depth=0):
        if depth > self.max_depth or len(self.visited) >= self.max_pages or url in self.visited:
            return []

        if not self.is_allowed(url):
            return []

        logging.info(f"Crawling: {url}")
        self.visited.add(url)

        use_selenium = False
        html = self.fetch_page(url)
        if not html or "javascript required" in html.lower():
            use_selenium = True
            html = self.fetch_page(url, use_selenium=True)

        if html:
            info = self.extract_info(url, html)
            self.results.append(info)
            self.pages_crawled += 1
            
            if self.pages_crawled % self.save_interval == 0:
                self.save_results(f'partial_results_{self.pages_crawled}.json')
            
            return info['links']
        
        time.sleep(1)  # Respectful crawling
        return []

    def run(self):
        for _ in range(self.selenium_workers):
            self.selenium_pool.append(self.init_selenium())

        try:
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                future_to_url = {executor.submit(self.crawl, self.start_url): self.start_url}
                while future_to_url and len(self.visited) < self.max_pages:
                    for future in as_completed(future_to_url):
                        url = future_to_url.pop(future)
                        try:
                            links = future.result()
                            depth = urlparse(url).path.count('/')
                            if depth < self.max_depth:
                                for link in links:
                                    if link not in self.visited and len(future_to_url) < self.max_workers:
                                        future_to_url[executor.submit(self.crawl, link)] = link
                        except Exception as exc:
                            logging.error(f"Exception for {url}: {exc}")
        finally:
            for driver in self.selenium_pool:
                driver.quit()
            
        self.save_results('final_results.json')

if __name__ == "__main__":
    start_url = "https://example.com"
    crawler = Crawler(start_url, max_depth=10, max_pages=150, max_workers=6, selenium_workers=2, save_interval=30)
    crawler.run()