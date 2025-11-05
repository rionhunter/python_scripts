# Web Scraping Framework

Comprehensive web scraping toolkit with Beautiful Soup + Selenium integration.

## Features

- **Multiple scraping modes**: Single page or recursive crawler
- **Dynamic content support**: Selenium integration for JavaScript-heavy sites
- **Selector flexibility**: CSS selectors and XPath support
- **Rate limiting**: Polite scraping with configurable delays
- **Session management**: Persistent cookies and headers
- **Table extraction**: Automatic HTML table to JSON conversion
- **Link discovery**: Recursive crawling with domain restrictions
- **Export formats**: JSON, CSV, TXT
- **GUI Interface**: PyQt6 graphical interface for easy access to all features

## Installation

```bash
cd web_scraping
pip install -r requirements.txt
```

**Note**: Selenium is optional. For JavaScript-heavy sites, you'll also need ChromeDriver.

## GUI Interface

Launch the graphical interface for easy web scraping:

```bash
python web_scraper_gui.py
```

### GUI Features

- **Single Page Tab**: Extract data from individual pages
  - CSS selector and XPath support
  - Attribute extraction
  - Wait for dynamic content (Selenium)
  - Live results preview

- **Site Crawler Tab**: Crawl multiple pages recursively
  - Configurable depth and page limits
  - Same-domain restriction option
  - Progress tracking
  - Batch export

- **Table Extractor Tab**: Extract HTML tables
  - Visual table preview
  - Direct CSV export
  - Custom table selectors

- **Settings Tab**: Configure scraper behavior
  - Rate limiting
  - Selenium toggle
  - Custom user agent
  - Export format preferences

## Usage Examples

### GUI Usage

1. Launch GUI: `python web_scraper_gui.py`
2. Select appropriate tab (Single Page, Crawler, or Table)
3. Enter URL and configure options
4. Click scrape/extract button
5. View results and export if needed

### Command Line Usage

### Basic Page Scraping

```bash
# Extract all h1 and p tags
python web_scraper.py https://example.com -s "h1, p" -o output.json

# Extract specific elements and save to file
python web_scraper.py https://example.com -s ".article-title" -o titles.json

# Extract with XPath
python web_scraper.py https://example.com -x "//div[@class='content']//p" -o content.json

# Extract text from page
python web_scraper.py https://example.com
```

### Table Scraping

```bash
# Extract HTML table to JSON
python web_scraper.py https://example.com/data -t "table.data-table" -o data.json

# Extract table to CSV
python web_scraper.py https://example.com/table -t "table" -o data.csv --format csv

# Multiple tables (first match)
python web_scraper.py https://example.com -t "table" -o output.json
```

### Attribute Extraction

```bash
# Extract all links (href attributes)
python web_scraper.py https://example.com -s "a" -a href -o links.json

# Extract image sources
python web_scraper.py https://example.com -s "img" -a src -o images.json

# Extract data attributes
python web_scraper.py https://example.com -s "[data-id]" -a data-id -o ids.json
```

### Site Crawling

```bash
# Crawl entire site (max depth 2)
python web_scraper.py https://example.com --crawl --max-depth 2 -o site_data.json

# Crawl with custom limits
python web_scraper.py https://example.com --crawl --max-depth 3 --max-pages 50 -o crawl.json

# Crawl and extract specific elements from each page
python web_scraper.py https://example.com --crawl -s "article" --max-depth 2
```

### Dynamic Content (Selenium)

```bash
# Scrape JavaScript-rendered page
python web_scraper.py https://spa-app.com --selenium -s ".dynamic-content"

# Wait for specific element to load
python web_scraper.py https://ajax-site.com --selenium --wait-for ".loaded-content" -s ".items"

# Crawl JavaScript-heavy site
python web_scraper.py https://spa-site.com --crawl --selenium --max-depth 2
```

### Rate Limiting & Politeness

```bash
# Custom rate limit (2 seconds between requests)
python web_scraper.py https://example.com --crawl --rate-limit 2.0

# Custom user agent
python web_scraper.py https://example.com --user-agent "MyBot/1.0"
```

## Advanced Usage

### Python API

```python
from web_scraper import WebScraper, SiteCrawler

# Create scraper with custom settings
with WebScraper(rate_limit=1.5, use_selenium=False) as scraper:
    # Fetch page
    html = scraper.fetch_page('https://example.com')
    soup = scraper.parse_html(html)
    
    # CSS selector extraction
    titles = scraper.select_css(soup, 'h2.title')
    title_texts = scraper.extract_text(titles)
    
    # XPath extraction
    paragraphs = scraper.select_xpath(soup, '//p[@class="content"]')
    
    # Extract links
    links = scraper.extract_links(soup, base_url='https://example.com')
    
    # Extract table
    table_data = scraper.scrape_table(soup, 'table.data')

# Crawl site
with WebScraper(rate_limit=1.0) as scraper:
    crawler = SiteCrawler(scraper, max_depth=2, max_pages=50)
    results = crawler.crawl('https://example.com', same_domain_only=True)
```

## Command-Line Options

```
positional arguments:
  url                   URL to scrape

optional arguments:
  -s, --selector        CSS selector to extract
  -x, --xpath           XPath expression to extract
  -t, --table           CSS selector for table to scrape
  -a, --attribute       Attribute to extract from selected elements
  -o, --output          Output file path
  --format {json,csv,txt}
                        Output format (default: json)
  --selenium            Use Selenium for JavaScript sites
  --wait-for            CSS selector to wait for (Selenium)
  --crawl               Crawl multiple pages
  --max-depth           Max crawl depth (default: 2)
  --max-pages           Max pages to crawl (default: 100)
  --rate-limit          Seconds between requests (default: 1.0)
  --user-agent          Custom user agent string
```

## Tips & Best Practices

1. **Start simple**: Test with basic selectors before crawling
2. **Respect robots.txt**: Check site's crawling policies
3. **Use rate limiting**: Don't overwhelm servers (1-2 seconds minimum)
4. **Identify yourself**: Use descriptive user agent
5. **Handle errors**: Some pages may fail, that's normal
6. **Test selectors**: Use browser DevTools to verify CSS/XPath
7. **Selenium for SPAs**: Use --selenium for React/Vue/Angular apps
8. **Check legality**: Ensure scraping is allowed by site terms

## Troubleshooting

**Selenium not working?**
- Install ChromeDriver: Download from https://chromedriver.chromium.org/
- Add to PATH or same directory as script

**Empty results?**
- Check selector with browser DevTools
- Try --selenium for dynamic content
- Increase --wait-for timeout

**Getting blocked?**
- Increase --rate-limit
- Use custom --user-agent
- Check robots.txt compliance

## Dependencies

- **requests**: HTTP requests
- **beautifulsoup4**: HTML parsing
- **lxml**: Fast XML/HTML parser, XPath support
- **selenium** (optional): JavaScript rendering
