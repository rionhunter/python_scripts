#!/usr/bin/env python3
"""
Web Scraper Framework
Comprehensive web scraping tool with Beautiful Soup + Selenium integration
Supports XPath/CSS selectors, dynamic content, rate limiting, and session management
"""

import argparse
import json
import time
import sys
from pathlib import Path
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Optional, Union
import re

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("Error: Required packages not installed.")
    print("Install with: pip install requests beautifulsoup4 lxml")
    sys.exit(1)

# Optional Selenium support
SELENIUM_AVAILABLE = False
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException
    SELENIUM_AVAILABLE = True
except ImportError:
    pass


class WebScraper:
    """Main web scraping class with session management and rate limiting"""
    
    def __init__(self, rate_limit: float = 1.0, use_selenium: bool = False, 
                 user_agent: Optional[str] = None):
        """
        Initialize web scraper
        
        Args:
            rate_limit: Minimum seconds between requests (politeness delay)
            use_selenium: Use Selenium for JavaScript-heavy sites
            user_agent: Custom user agent string
        """
        self.rate_limit = rate_limit
        self.last_request_time = 0
        self.use_selenium = use_selenium and SELENIUM_AVAILABLE
        
        # Set up session with headers
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': user_agent or 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Selenium driver (lazy initialization)
        self.driver = None
        
    def _respect_rate_limit(self):
        """Enforce rate limiting between requests"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.rate_limit:
            time.sleep(self.rate_limit - elapsed)
        self.last_request_time = time.time()
    
    def fetch_page(self, url: str, wait_for: Optional[str] = None) -> Optional[str]:
        """
        Fetch page content (with optional dynamic content support)
        
        Args:
            url: URL to fetch
            wait_for: CSS selector to wait for (Selenium only)
            
        Returns:
            Page HTML content or None on failure
        """
        self._respect_rate_limit()
        
        if self.use_selenium:
            return self._fetch_with_selenium(url, wait_for)
        else:
            return self._fetch_with_requests(url)
    
    def _fetch_with_requests(self, url: str) -> Optional[str]:
        """Fetch page using requests library"""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None
    
    def _fetch_with_selenium(self, url: str, wait_for: Optional[str] = None) -> Optional[str]:
        """Fetch page using Selenium (for JavaScript-heavy sites)"""
        if not SELENIUM_AVAILABLE:
            print("Selenium not available, falling back to requests")
            return self._fetch_with_requests(url)
        
        try:
            if self.driver is None:
                options = webdriver.ChromeOptions()
                options.add_argument('--headless')
                options.add_argument('--disable-gpu')
                self.driver = webdriver.Chrome(options=options)
            
            self.driver.get(url)
            
            # Wait for specific element if requested
            if wait_for:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, wait_for))
                )
            else:
                time.sleep(2)  # Default wait for page load
            
            return self.driver.page_source
        except Exception as e:
            print(f"Error fetching {url} with Selenium: {e}")
            return None
    
    def parse_html(self, html: str, parser: str = 'lxml') -> Optional[BeautifulSoup]:
        """
        Parse HTML content with BeautifulSoup
        
        Args:
            html: HTML string to parse
            parser: Parser to use ('lxml', 'html.parser', 'html5lib')
            
        Returns:
            BeautifulSoup object or None
        """
        try:
            return BeautifulSoup(html, parser)
        except Exception as e:
            print(f"Error parsing HTML: {e}")
            return None
    
    def select_css(self, soup: BeautifulSoup, selector: str) -> List:
        """
        Select elements using CSS selector
        
        Args:
            soup: BeautifulSoup object
            selector: CSS selector string
            
        Returns:
            List of matching elements
        """
        return soup.select(selector)
    
    def select_xpath(self, soup: BeautifulSoup, xpath: str) -> List:
        """
        Select elements using XPath (via lxml)
        
        Args:
            soup: BeautifulSoup object
            xpath: XPath expression
            
        Returns:
            List of matching elements
        """
        try:
            from lxml import etree, html as lxml_html
            tree = lxml_html.fromstring(str(soup))
            return tree.xpath(xpath)
        except ImportError:
            print("XPath requires lxml: pip install lxml")
            return []
        except Exception as e:
            print(f"XPath error: {e}")
            return []
    
    def extract_text(self, elements: List, strip: bool = True) -> List[str]:
        """Extract text from elements"""
        texts = []
        for elem in elements:
            text = elem.get_text() if hasattr(elem, 'get_text') else str(elem)
            if strip:
                text = text.strip()
            if text:
                texts.append(text)
        return texts
    
    def extract_attributes(self, elements: List, attr: str) -> List[str]:
        """Extract specific attribute from elements"""
        attrs = []
        for elem in elements:
            if hasattr(elem, 'get'):
                value = elem.get(attr)
                if value:
                    attrs.append(value)
        return attrs
    
    def extract_links(self, soup: BeautifulSoup, base_url: str = '') -> List[str]:
        """Extract all links from page"""
        links = []
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            if base_url:
                href = urljoin(base_url, href)
            links.append(href)
        return links
    
    def scrape_table(self, soup: BeautifulSoup, table_selector: str = 'table') -> List[Dict]:
        """
        Scrape HTML table into list of dictionaries
        
        Args:
            soup: BeautifulSoup object
            table_selector: CSS selector for table
            
        Returns:
            List of row dictionaries
        """
        table = soup.select_one(table_selector)
        if not table:
            return []
        
        # Get headers
        headers = []
        header_row = table.find('thead')
        if header_row:
            headers = [th.get_text(strip=True) for th in header_row.find_all('th')]
        else:
            first_row = table.find('tr')
            if first_row:
                headers = [th.get_text(strip=True) for th in first_row.find_all(['th', 'td'])]
        
        # Get rows
        rows = []
        tbody = table.find('tbody') or table
        for tr in tbody.find_all('tr'):
            cells = [td.get_text(strip=True) for td in tr.find_all(['td', 'th'])]
            if cells and len(cells) == len(headers):
                rows.append(dict(zip(headers, cells)))
        
        return rows
    
    def close(self):
        """Clean up resources"""
        if self.driver:
            self.driver.quit()
            self.driver = None
        self.session.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class SiteCrawler:
    """Recursive site crawler with link discovery"""
    
    def __init__(self, scraper: WebScraper, max_depth: int = 2, max_pages: int = 100):
        self.scraper = scraper
        self.max_depth = max_depth
        self.max_pages = max_pages
        self.visited = set()
        self.to_visit = []
    
    def crawl(self, start_url: str, same_domain_only: bool = True) -> List[Dict]:
        """
        Crawl site starting from URL
        
        Args:
            start_url: Starting URL
            same_domain_only: Only follow links on same domain
            
        Returns:
            List of page data dictionaries
        """
        start_domain = urlparse(start_url).netloc
        self.to_visit = [(start_url, 0)]
        results = []
        
        while self.to_visit and len(self.visited) < self.max_pages:
            url, depth = self.to_visit.pop(0)
            
            if url in self.visited or depth > self.max_depth:
                continue
            
            print(f"Crawling: {url} (depth: {depth})")
            self.visited.add(url)
            
            # Fetch page
            html = self.scraper.fetch_page(url)
            if not html:
                continue
            
            soup = self.scraper.parse_html(html)
            if not soup:
                continue
            
            # Extract page data
            page_data = {
                'url': url,
                'depth': depth,
                'title': soup.title.string if soup.title else '',
                'text': soup.get_text(separator=' ', strip=True)[:1000]  # First 1000 chars
            }
            results.append(page_data)
            
            # Find links for next level
            if depth < self.max_depth:
                links = self.scraper.extract_links(soup, url)
                for link in links:
                    if link not in self.visited:
                        # Check domain restriction
                        if same_domain_only:
                            link_domain = urlparse(link).netloc
                            if link_domain != start_domain:
                                continue
                        self.to_visit.append((link, depth + 1))
        
        return results


def save_results(data: Union[List, Dict], output_path: str, format: str = 'json'):
    """
    Save scraping results to file
    
    Args:
        data: Data to save
        output_path: Output file path
        format: Output format ('json', 'csv', 'txt')
    """
    output_path = Path(output_path)
    
    if format == 'json':
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    elif format == 'csv':
        import csv
        if isinstance(data, list) and data and isinstance(data[0], dict):
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
    
    elif format == 'txt':
        with open(output_path, 'w', encoding='utf-8') as f:
            if isinstance(data, list):
                for item in data:
                    f.write(str(item) + '\n')
            else:
                f.write(str(data))
    
    print(f"Results saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description='Web Scraper Framework - Extract data from websites',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Simple page scraping
  python web_scraper.py https://example.com -s "h1, p" -o output.json
  
  # Extract table data
  python web_scraper.py https://example.com/table -t "table.data" -o data.csv --format csv
  
  # Crawl site (multiple pages)
  python web_scraper.py https://example.com --crawl --max-depth 2 -o site_data.json
  
  # Use Selenium for dynamic content
  python web_scraper.py https://spa-app.com --selenium --wait-for ".content" -s ".items"
        """
    )
    
    parser.add_argument('url', help='URL to scrape')
    parser.add_argument('-s', '--selector', help='CSS selector to extract')
    parser.add_argument('-x', '--xpath', help='XPath expression to extract')
    parser.add_argument('-t', '--table', help='CSS selector for table to scrape')
    parser.add_argument('-a', '--attribute', help='Attribute to extract from selected elements')
    parser.add_argument('-o', '--output', help='Output file path')
    parser.add_argument('--format', choices=['json', 'csv', 'txt'], default='json',
                        help='Output format (default: json)')
    parser.add_argument('--selenium', action='store_true', help='Use Selenium for JavaScript sites')
    parser.add_argument('--wait-for', help='CSS selector to wait for (Selenium)')
    parser.add_argument('--crawl', action='store_true', help='Crawl multiple pages')
    parser.add_argument('--max-depth', type=int, default=2, help='Max crawl depth (default: 2)')
    parser.add_argument('--max-pages', type=int, default=100, help='Max pages to crawl (default: 100)')
    parser.add_argument('--rate-limit', type=float, default=1.0,
                        help='Seconds between requests (default: 1.0)')
    parser.add_argument('--user-agent', help='Custom user agent string')
    
    args = parser.parse_args()
    
    # Create scraper
    with WebScraper(rate_limit=args.rate_limit, use_selenium=args.selenium,
                    user_agent=args.user_agent) as scraper:
        
        if args.crawl:
            # Crawl mode
            crawler = SiteCrawler(scraper, max_depth=args.max_depth, max_pages=args.max_pages)
            results = crawler.crawl(args.url)
            
            if args.output:
                save_results(results, args.output, args.format)
            else:
                print(json.dumps(results, indent=2))
        
        else:
            # Single page scraping
            html = scraper.fetch_page(args.url, wait_for=args.wait_for)
            if not html:
                print("Failed to fetch page")
                return 1
            
            soup = scraper.parse_html(html)
            if not soup:
                print("Failed to parse HTML")
                return 1
            
            # Extract data based on arguments
            if args.table:
                results = scraper.scrape_table(soup, args.table)
            
            elif args.selector:
                elements = scraper.select_css(soup, args.selector)
                if args.attribute:
                    results = scraper.extract_attributes(elements, args.attribute)
                else:
                    results = scraper.extract_text(elements)
            
            elif args.xpath:
                elements = scraper.select_xpath(soup, args.xpath)
                if args.attribute:
                    results = [elem.get(args.attribute) for elem in elements if hasattr(elem, 'get')]
                else:
                    results = scraper.extract_text(elements)
            
            else:
                # Default: extract title and all text
                results = {
                    'url': args.url,
                    'title': soup.title.string if soup.title else '',
                    'text': soup.get_text(separator='\n', strip=True)
                }
            
            # Output results
            if args.output:
                save_results(results, args.output, args.format)
            else:
                if isinstance(results, (list, dict)):
                    print(json.dumps(results, indent=2, ensure_ascii=False))
                else:
                    for item in results:
                        print(item)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
