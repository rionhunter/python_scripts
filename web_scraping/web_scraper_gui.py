#!/usr/bin/env python3
"""
Web Scraper GUI
PyQt6 interface for the web scraping framework with full functionality access
"""

import sys
import json
from pathlib import Path
from typing import Optional

try:
    from PyQt6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QTabWidget, QLabel, QLineEdit, QPushButton, QTextEdit, QComboBox,
        QSpinBox, QCheckBox, QGroupBox, QFileDialog, QMessageBox,
        QProgressBar, QTableWidget, QTableWidgetItem, QSplitter,
        QHeaderView
    )
    from PyQt6.QtCore import Qt, QThread, pyqtSignal
    from PyQt6.QtGui import QFont, QTextOption
except ImportError:
    print("Error: PyQt6 not installed")
    print("Install with: pip install PyQt6")
    sys.exit(1)

# Import web scraper modules
try:
    from web_scraper import WebScraper, SiteCrawler, save_results
except ImportError:
    print("Error: web_scraper.py not found in the same directory")
    sys.exit(1)


class ScraperThread(QThread):
    """Worker thread for scraping operations"""
    
    finished = pyqtSignal(object)  # Results
    error = pyqtSignal(str)  # Error message
    progress = pyqtSignal(str)  # Progress message
    
    def __init__(self, scraper, operation, params):
        super().__init__()
        self.scraper = scraper
        self.operation = operation
        self.params = params
    
    def run(self):
        try:
            if self.operation == 'single':
                self.run_single_page()
            elif self.operation == 'crawl':
                self.run_crawler()
            elif self.operation == 'table':
                self.run_table_extraction()
        except Exception as e:
            self.error.emit(str(e))
    
    def run_single_page(self):
        """Scrape single page"""
        url = self.params['url']
        selector = self.params.get('selector')
        xpath = self.params.get('xpath')
        attribute = self.params.get('attribute')
        wait_for = self.params.get('wait_for')
        
        self.progress.emit(f"Fetching: {url}")
        html = self.scraper.fetch_page(url, wait_for=wait_for)
        
        if not html:
            self.error.emit("Failed to fetch page")
            return
        
        self.progress.emit("Parsing HTML...")
        soup = self.scraper.parse_html(html)
        
        if not soup:
            self.error.emit("Failed to parse HTML")
            return
        
        results = {}
        
        # Extract based on selector type
        if selector:
            self.progress.emit(f"Extracting with selector: {selector}")
            elements = self.scraper.select_css(soup, selector)
            if attribute:
                results['data'] = self.scraper.extract_attributes(elements, attribute)
            else:
                results['data'] = self.scraper.extract_text(elements)
        
        elif xpath:
            self.progress.emit(f"Extracting with XPath: {xpath}")
            elements = self.scraper.select_xpath(soup, xpath)
            if attribute:
                results['data'] = [elem.get(attribute) for elem in elements if hasattr(elem, 'get')]
            else:
                results['data'] = self.scraper.extract_text(elements)
        
        else:
            # Default: extract title and text
            results['url'] = url
            results['title'] = soup.title.string if soup.title else ''
            results['text'] = soup.get_text(separator='\n', strip=True)
            results['links'] = self.scraper.extract_links(soup, url)[:50]  # First 50 links
        
        results['url'] = url
        results['match_count'] = len(results.get('data', []))
        
        self.progress.emit("Extraction complete!")
        self.finished.emit(results)
    
    def run_crawler(self):
        """Crawl multiple pages"""
        url = self.params['url']
        max_depth = self.params.get('max_depth', 2)
        max_pages = self.params.get('max_pages', 100)
        same_domain = self.params.get('same_domain', True)
        
        self.progress.emit(f"Starting crawler from: {url}")
        crawler = SiteCrawler(self.scraper, max_depth=max_depth, max_pages=max_pages)
        
        # Override progress reporting
        original_crawl = crawler.crawl
        
        def crawl_with_progress(*args, **kwargs):
            results = []
            crawler.to_visit = [(url, 0)]
            
            while crawler.to_visit and len(crawler.visited) < crawler.max_pages:
                current_url, depth = crawler.to_visit.pop(0)
                
                if current_url in crawler.visited or depth > crawler.max_depth:
                    continue
                
                self.progress.emit(f"Crawling ({len(crawler.visited)+1}/{max_pages}): {current_url}")
                crawler.visited.add(current_url)
                
                # Fetch page
                html = self.scraper.fetch_page(current_url)
                if not html:
                    continue
                
                soup = self.scraper.parse_html(html)
                if not soup:
                    continue
                
                # Extract page data with meaningful content
                # Get main content (skip scripts, styles, etc.)
                for script in soup(['script', 'style', 'nav', 'footer', 'header']):
                    script.decompose()
                
                # Extract text from main content areas
                main_content = soup.find('main') or soup.find('article') or soup.find('body')
                if main_content:
                    text_content = main_content.get_text(separator='\n', strip=True)
                else:
                    text_content = soup.get_text(separator='\n', strip=True)
                
                # Get all headings for structure
                headings = [h.get_text(strip=True) for h in soup.find_all(['h1', 'h2', 'h3'])]
                
                # Get meta description if available
                meta_desc = ''
                meta_tag = soup.find('meta', attrs={'name': 'description'})
                if meta_tag and meta_tag.get('content'):
                    meta_desc = meta_tag['content']
                
                page_data = {
                    'url': current_url,
                    'depth': depth,
                    'title': soup.title.string if soup.title else '',
                    'description': meta_desc,
                    'headings': headings[:10],  # First 10 headings
                    'text': text_content[:2000],  # First 2000 chars of main content
                    'text_length': len(text_content),
                    'link_count': len(self.scraper.extract_links(soup, current_url))
                }
                results.append(page_data)
                
                # Find links for next level
                if depth < crawler.max_depth:
                    links = self.scraper.extract_links(soup, current_url)
                    for link in links:
                        if link not in crawler.visited:
                            from urllib.parse import urlparse
                            if same_domain:
                                link_domain = urlparse(link).netloc
                                start_domain = urlparse(url).netloc
                                if link_domain != start_domain:
                                    continue
                            crawler.to_visit.append((link, depth + 1))
            
            return results
        
        results = crawl_with_progress()
        
        self.progress.emit(f"Crawl complete! Found {len(results)} pages")
        self.finished.emit({'pages': results, 'total': len(results)})
    
    def run_table_extraction(self):
        """Extract table from page"""
        url = self.params['url']
        table_selector = self.params.get('table_selector', 'table')
        wait_for = self.params.get('wait_for')
        
        self.progress.emit(f"Fetching: {url}")
        html = self.scraper.fetch_page(url, wait_for=wait_for)
        
        if not html:
            self.error.emit("Failed to fetch page")
            return
        
        self.progress.emit("Parsing HTML and extracting table...")
        soup = self.scraper.parse_html(html)
        
        if not soup:
            self.error.emit("Failed to parse HTML")
            return
        
        table_data = self.scraper.scrape_table(soup, table_selector)
        
        if not table_data:
            self.error.emit(f"No table found with selector: {table_selector}")
            return
        
        self.progress.emit(f"Extracted {len(table_data)} rows")
        self.finished.emit({'url': url, 'table': table_data, 'row_count': len(table_data)})


class WebScraperGUI(QMainWindow):
    """Main GUI window for web scraper"""
    
    def __init__(self):
        super().__init__()
        self.scraper = None
        self.thread = None
        self.current_results = None
        
        self.setWindowTitle("Web Scraper - PyQt6 GUI")
        self.setGeometry(100, 100, 1200, 800)
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Create tab widget
        tabs = QTabWidget()
        main_layout.addWidget(tabs)
        
        # Add tabs
        tabs.addTab(self.create_single_page_tab(), "Single Page")
        tabs.addTab(self.create_crawler_tab(), "Site Crawler")
        tabs.addTab(self.create_table_tab(), "Table Extractor")
        tabs.addTab(self.create_settings_tab(), "Settings")
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
        # Status bar
        self.statusBar().showMessage("Ready")
    
    def create_single_page_tab(self):
        """Create single page scraping tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)
        
        # URL input
        url_group = QGroupBox("URL")
        url_layout = QHBoxLayout()
        url_group.setLayout(url_layout)
        
        self.single_url = QLineEdit()
        self.single_url.setPlaceholderText("https://example.com")
        url_layout.addWidget(self.single_url)
        
        layout.addWidget(url_group)
        
        # Selector options
        selector_group = QGroupBox("Extraction Options")
        selector_layout = QVBoxLayout()
        selector_group.setLayout(selector_layout)
        
        # CSS Selector
        css_layout = QHBoxLayout()
        css_layout.addWidget(QLabel("CSS Selector:"))
        self.single_css = QLineEdit()
        self.single_css.setPlaceholderText("div.content, h1, p")
        css_layout.addWidget(self.single_css)
        selector_layout.addLayout(css_layout)
        
        # XPath
        xpath_layout = QHBoxLayout()
        xpath_layout.addWidget(QLabel("XPath:"))
        self.single_xpath = QLineEdit()
        self.single_xpath.setPlaceholderText("//div[@class='content']//p")
        xpath_layout.addWidget(self.single_xpath)
        selector_layout.addLayout(xpath_layout)
        
        # Attribute
        attr_layout = QHBoxLayout()
        attr_layout.addWidget(QLabel("Extract Attribute:"))
        self.single_attr = QLineEdit()
        self.single_attr.setPlaceholderText("href, src, data-id (optional)")
        attr_layout.addWidget(self.single_attr)
        selector_layout.addLayout(attr_layout)
        
        # Wait for element (Selenium)
        wait_layout = QHBoxLayout()
        wait_layout.addWidget(QLabel("Wait For (Selenium):"))
        self.single_wait = QLineEdit()
        self.single_wait.setPlaceholderText(".loaded-content (optional)")
        wait_layout.addWidget(self.single_wait)
        selector_layout.addLayout(wait_layout)
        
        layout.addWidget(selector_group)
        
        # Selenium options
        selenium_group = QGroupBox("Selenium Options")
        selenium_layout = QVBoxLayout()
        selenium_group.setLayout(selenium_layout)
        
        self.single_use_selenium = QCheckBox("Use Selenium (for JavaScript-heavy sites)")
        self.single_use_selenium.setChecked(False)
        selenium_layout.addWidget(self.single_use_selenium)
        
        selenium_help = QLabel("⚠️ Note: Selenium requires installation of selenium package and browser driver")
        selenium_help.setStyleSheet("color: #666; font-style: italic; font-size: 9pt;")
        selenium_layout.addWidget(selenium_help)
        
        layout.addWidget(selenium_group)
        
        # Action buttons
        btn_layout = QHBoxLayout()
        
        self.single_scrape_btn = QPushButton("Scrape Page")
        self.single_scrape_btn.clicked.connect(self.run_single_scrape)
        btn_layout.addWidget(self.single_scrape_btn)
        
        self.single_export_btn = QPushButton("Export Results")
        self.single_export_btn.clicked.connect(self.export_results)
        self.single_export_btn.setEnabled(False)
        btn_layout.addWidget(self.single_export_btn)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        # Results display
        results_group = QGroupBox("Results")
        results_layout = QVBoxLayout()
        results_group.setLayout(results_layout)
        
        self.single_results = QTextEdit()
        self.single_results.setReadOnly(True)
        self.single_results.setFont(QFont("Courier", 9))
        results_layout.addWidget(self.single_results)
        
        layout.addWidget(results_group)
        
        return widget
    
    def create_crawler_tab(self):
        """Create site crawler tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)
        
        # URL input
        url_group = QGroupBox("Starting URL")
        url_layout = QHBoxLayout()
        url_group.setLayout(url_layout)
        
        self.crawler_url = QLineEdit()
        self.crawler_url.setPlaceholderText("https://example.com")
        url_layout.addWidget(self.crawler_url)
        
        layout.addWidget(url_group)
        
        # Crawler options
        options_group = QGroupBox("Crawler Options")
        options_layout = QVBoxLayout()
        options_group.setLayout(options_layout)
        
        # Max depth
        depth_layout = QHBoxLayout()
        depth_layout.addWidget(QLabel("Max Depth:"))
        self.crawler_depth = QSpinBox()
        self.crawler_depth.setRange(1, 10)
        self.crawler_depth.setValue(2)
        depth_layout.addWidget(self.crawler_depth)
        depth_layout.addStretch()
        options_layout.addLayout(depth_layout)
        
        # Max pages
        pages_layout = QHBoxLayout()
        pages_layout.addWidget(QLabel("Max Pages:"))
        self.crawler_pages = QSpinBox()
        self.crawler_pages.setRange(1, 1000)
        self.crawler_pages.setValue(100)
        pages_layout.addWidget(self.crawler_pages)
        pages_layout.addStretch()
        options_layout.addLayout(pages_layout)
        
        # Same domain only
        self.crawler_same_domain = QCheckBox("Same Domain Only")
        self.crawler_same_domain.setChecked(True)
        options_layout.addWidget(self.crawler_same_domain)
        
        layout.addWidget(options_group)
        
        # Selenium options
        selenium_group = QGroupBox("Selenium Options")
        selenium_layout = QVBoxLayout()
        selenium_group.setLayout(selenium_layout)
        
        self.crawler_use_selenium = QCheckBox("Use Selenium (for JavaScript-heavy sites)")
        self.crawler_use_selenium.setChecked(False)
        selenium_layout.addWidget(self.crawler_use_selenium)
        
        # Wait for element
        wait_layout = QHBoxLayout()
        wait_layout.addWidget(QLabel("Wait For Element:"))
        self.crawler_wait = QLineEdit()
        self.crawler_wait.setPlaceholderText(".loaded-content (optional)")
        wait_layout.addWidget(self.crawler_wait)
        selenium_layout.addLayout(wait_layout)
        
        selenium_help = QLabel("⚠️ Note: Selenium requires installation of selenium package and browser driver")
        selenium_help.setStyleSheet("color: #666; font-style: italic; font-size: 9pt;")
        selenium_layout.addWidget(selenium_help)
        
        layout.addWidget(selenium_group)
        
        # Action buttons
        btn_layout = QHBoxLayout()
        
        self.crawler_start_btn = QPushButton("Start Crawling")
        self.crawler_start_btn.clicked.connect(self.run_crawler)
        btn_layout.addWidget(self.crawler_start_btn)
        
        self.crawler_export_btn = QPushButton("Export Results")
        self.crawler_export_btn.clicked.connect(self.export_results)
        self.crawler_export_btn.setEnabled(False)
        btn_layout.addWidget(self.crawler_export_btn)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        # Results display
        results_group = QGroupBox("Crawled Pages")
        results_layout = QVBoxLayout()
        results_group.setLayout(results_layout)
        
        self.crawler_results = QTextEdit()
        self.crawler_results.setReadOnly(True)
        self.crawler_results.setFont(QFont("Courier", 9))
        results_layout.addWidget(self.crawler_results)
        
        layout.addWidget(results_group)
        
        return widget
    
    def create_table_tab(self):
        """Create table extraction tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)
        
        # URL input
        url_group = QGroupBox("URL")
        url_layout = QHBoxLayout()
        url_group.setLayout(url_layout)
        
        self.table_url = QLineEdit()
        self.table_url.setPlaceholderText("https://example.com/table")
        url_layout.addWidget(self.table_url)
        
        layout.addWidget(url_group)
        
        # Table options
        options_group = QGroupBox("Table Options")
        options_layout = QVBoxLayout()
        options_group.setLayout(options_layout)
        
        # Table selector
        selector_layout = QHBoxLayout()
        selector_layout.addWidget(QLabel("Table Selector:"))
        self.table_selector = QLineEdit()
        self.table_selector.setPlaceholderText("table (CSS selector)")
        self.table_selector.setText("table")
        selector_layout.addWidget(self.table_selector)
        options_layout.addLayout(selector_layout)
        
        layout.addWidget(options_group)
        
        # Selenium options
        selenium_group = QGroupBox("Selenium Options")
        selenium_layout = QVBoxLayout()
        selenium_group.setLayout(selenium_layout)
        
        self.table_use_selenium = QCheckBox("Use Selenium (for JavaScript-heavy sites)")
        self.table_use_selenium.setChecked(False)
        selenium_layout.addWidget(self.table_use_selenium)
        
        # Wait for element
        wait_layout = QHBoxLayout()
        wait_layout.addWidget(QLabel("Wait For Element:"))
        self.table_wait = QLineEdit()
        self.table_wait.setPlaceholderText(".table-loaded (optional)")
        wait_layout.addWidget(self.table_wait)
        selenium_layout.addLayout(wait_layout)
        
        selenium_help = QLabel("⚠️ Note: Selenium requires installation of selenium package and browser driver")
        selenium_help.setStyleSheet("color: #666; font-style: italic; font-size: 9pt;")
        selenium_layout.addWidget(selenium_help)
        
        layout.addWidget(selenium_group)
        
        # Action buttons
        btn_layout = QHBoxLayout()
        
        self.table_extract_btn = QPushButton("Extract Table")
        self.table_extract_btn.clicked.connect(self.run_table_extraction)
        btn_layout.addWidget(self.table_extract_btn)
        
        self.table_export_btn = QPushButton("Export to CSV")
        self.table_export_btn.clicked.connect(lambda: self.export_results('csv'))
        self.table_export_btn.setEnabled(False)
        btn_layout.addWidget(self.table_export_btn)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        # Results display (table widget)
        results_group = QGroupBox("Extracted Table")
        results_layout = QVBoxLayout()
        results_group.setLayout(results_layout)
        
        self.table_results = QTableWidget()
        self.table_results.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        results_layout.addWidget(self.table_results)
        
        layout.addWidget(results_group)
        
        return widget
    
    def create_settings_tab(self):
        """Create settings tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)
        
        # Scraper settings
        scraper_group = QGroupBox("Scraper Settings")
        scraper_layout = QVBoxLayout()
        scraper_group.setLayout(scraper_layout)
        
        # Rate limit
        rate_layout = QHBoxLayout()
        rate_layout.addWidget(QLabel("Rate Limit (seconds):"))
        self.rate_limit = QSpinBox()
        self.rate_limit.setRange(0, 10)
        self.rate_limit.setValue(1)
        self.rate_limit.setSingleStep(1)
        rate_layout.addWidget(self.rate_limit)
        rate_layout.addStretch()
        scraper_layout.addLayout(rate_layout)
        
        # Use Selenium
        self.use_selenium = QCheckBox("Use Selenium by default (for JavaScript sites)")
        scraper_layout.addWidget(self.use_selenium)
        
        selenium_note = QLabel("ℹ️ Note: Each tab has its own Selenium toggle that overrides this default")
        selenium_note.setStyleSheet("color: #0066cc; font-style: italic; font-size: 9pt; margin-left: 20px;")
        selenium_note.setWordWrap(True)
        scraper_layout.addWidget(selenium_note)
        
        # User agent
        ua_layout = QVBoxLayout()
        ua_layout.addWidget(QLabel("User Agent:"))
        self.user_agent = QLineEdit()
        self.user_agent.setPlaceholderText("Mozilla/5.0 ... (default)")
        ua_layout.addWidget(self.user_agent)
        scraper_layout.addLayout(ua_layout)
        
        layout.addWidget(scraper_group)
        
        # Export settings
        export_group = QGroupBox("Export Settings")
        export_layout = QVBoxLayout()
        export_group.setLayout(export_layout)
        
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("Default Format:"))
        self.export_format = QComboBox()
        self.export_format.addItems(['json', 'csv', 'txt'])
        format_layout.addWidget(self.export_format)
        format_layout.addStretch()
        export_layout.addLayout(format_layout)
        
        layout.addWidget(export_group)
        
        layout.addStretch()
        
        # Apply button
        apply_btn = QPushButton("Apply Settings")
        apply_btn.clicked.connect(self.apply_settings)
        layout.addWidget(apply_btn)
        
        return widget
    
    def get_scraper(self, use_selenium_override=None):
        """Get or create scraper instance with current settings"""
        if self.scraper:
            self.scraper.close()
        
        rate_limit = self.rate_limit.value()
        # Use override if provided, otherwise use global setting
        use_selenium = use_selenium_override if use_selenium_override is not None else self.use_selenium.isChecked()
        user_agent = self.user_agent.text().strip() or None
        
        self.scraper = WebScraper(
            rate_limit=rate_limit,
            use_selenium=use_selenium,
            user_agent=user_agent
        )
        
        return self.scraper
    
    def apply_settings(self):
        """Apply settings"""
        self.statusBar().showMessage("Settings applied", 3000)
        QMessageBox.information(self, "Settings", "Settings will be applied on next scraping operation")
    
    def run_single_scrape(self):
        """Run single page scraping"""
        url = self.single_url.text().strip()
        
        if not url:
            QMessageBox.warning(self, "Error", "Please enter a URL")
            return
        
        params = {
            'url': url,
            'selector': self.single_css.text().strip() or None,
            'xpath': self.single_xpath.text().strip() or None,
            'attribute': self.single_attr.text().strip() or None,
            'wait_for': self.single_wait.text().strip() or None,
            'use_selenium': self.single_use_selenium.isChecked()
        }
        
        self.start_scraping('single', params, self.single_results, self.single_export_btn)
    
    def run_crawler(self):
        """Run site crawler"""
        url = self.crawler_url.text().strip()
        
        if not url:
            QMessageBox.warning(self, "Error", "Please enter a starting URL")
            return
        
        params = {
            'url': url,
            'max_depth': self.crawler_depth.value(),
            'max_pages': self.crawler_pages.value(),
            'same_domain': self.crawler_same_domain.isChecked(),
            'use_selenium': self.crawler_use_selenium.isChecked(),
            'wait_for': self.crawler_wait.text().strip() or None
        }
        
        self.start_scraping('crawl', params, self.crawler_results, self.crawler_export_btn)
    
    def run_table_extraction(self):
        """Run table extraction"""
        url = self.table_url.text().strip()
        
        if not url:
            QMessageBox.warning(self, "Error", "Please enter a URL")
            return
        
        params = {
            'url': url,
            'table_selector': self.table_selector.text().strip(),
            'wait_for': self.table_wait.text().strip() or None,
            'use_selenium': self.table_use_selenium.isChecked()
        }
        
        self.start_scraping('table', params, self.table_results, self.table_export_btn)
    
    def start_scraping(self, operation, params, results_widget, export_btn):
        """Start scraping operation in thread"""
        # Disable buttons
        self.single_scrape_btn.setEnabled(False)
        self.crawler_start_btn.setEnabled(False)
        self.table_extract_btn.setEnabled(False)
        export_btn.setEnabled(False)
        
        # Show progress
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate
        
        # Clear results
        if isinstance(results_widget, QTextEdit):
            results_widget.clear()
        else:
            results_widget.setRowCount(0)
            results_widget.setColumnCount(0)
        
        # Create and start thread with per-tab selenium setting
        use_selenium = params.get('use_selenium', False)
        scraper = self.get_scraper(use_selenium_override=use_selenium)
        self.thread = ScraperThread(scraper, operation, params)
        self.thread.finished.connect(lambda r: self.scraping_finished(r, results_widget, export_btn))
        self.thread.error.connect(self.scraping_error)
        self.thread.progress.connect(self.update_progress)
        self.thread.start()
    
    def scraping_finished(self, results, results_widget, export_btn):
        """Handle scraping completion"""
        self.current_results = results
        
        # Display results
        if isinstance(results_widget, QTextEdit):
            # Format output based on result type
            if 'pages' in results:
                # Crawler results - format nicely
                output = f"=== CRAWL RESULTS ===\n"
                output += f"Total pages crawled: {results['total']}\n\n"
                
                for i, page in enumerate(results['pages'], 1):
                    output += f"\n{'='*80}\n"
                    output += f"PAGE {i}: {page['url']}\n"
                    output += f"{'='*80}\n"
                    output += f"Depth: {page['depth']}\n"
                    output += f"Title: {page.get('title', 'N/A')}\n"
                    
                    if page.get('description'):
                        output += f"Description: {page['description']}\n"
                    
                    output += f"Content Length: {page.get('text_length', 0)} characters\n"
                    output += f"Links Found: {page.get('link_count', 0)}\n"
                    
                    if page.get('headings'):
                        output += f"\nHeadings:\n"
                        for heading in page['headings']:
                            output += f"  • {heading}\n"
                    
                    output += f"\nContent Preview:\n"
                    output += f"{'-'*80}\n"
                    text_preview = page.get('text', '')[:1000]
                    output += f"{text_preview}\n"
                    
                    if len(page.get('text', '')) > 1000:
                        output += f"\n... (showing first 1000 of {page.get('text_length', 0)} characters)\n"
                
                results_widget.setPlainText(output)
            else:
                # Other results - default JSON formatting
                results_widget.setPlainText(json.dumps(results, indent=2, ensure_ascii=False))
        else:
            # Table display
            table_data = results.get('table', [])
            if table_data:
                self.display_table(table_data, results_widget)
        
        # Enable buttons
        self.single_scrape_btn.setEnabled(True)
        self.crawler_start_btn.setEnabled(True)
        self.table_extract_btn.setEnabled(True)
        export_btn.setEnabled(True)
        
        # Hide progress
        self.progress_bar.setVisible(False)
        
        # Update status
        if 'match_count' in results:
            self.statusBar().showMessage(f"Found {results['match_count']} matches")
        elif 'total' in results:
            self.statusBar().showMessage(f"Crawled {results['total']} pages")
        elif 'row_count' in results:
            self.statusBar().showMessage(f"Extracted {results['row_count']} rows")
        else:
            self.statusBar().showMessage("Scraping complete")
        
        # Cleanup
        if self.scraper:
            self.scraper.close()
    
    def scraping_error(self, error_msg):
        """Handle scraping error"""
        QMessageBox.critical(self, "Error", f"Scraping failed:\n{error_msg}")
        
        # Enable buttons
        self.single_scrape_btn.setEnabled(True)
        self.crawler_start_btn.setEnabled(True)
        self.table_extract_btn.setEnabled(True)
        
        # Hide progress
        self.progress_bar.setVisible(False)
        
        self.statusBar().showMessage("Error occurred")
        
        # Cleanup
        if self.scraper:
            self.scraper.close()
    
    def update_progress(self, message):
        """Update progress message"""
        self.statusBar().showMessage(message)
    
    def display_table(self, table_data, table_widget):
        """Display table data in QTableWidget"""
        if not table_data:
            return
        
        # Get headers
        headers = list(table_data[0].keys())
        
        # Set dimensions
        table_widget.setRowCount(len(table_data))
        table_widget.setColumnCount(len(headers))
        table_widget.setHorizontalHeaderLabels(headers)
        
        # Fill data
        for row_idx, row_data in enumerate(table_data):
            for col_idx, header in enumerate(headers):
                value = row_data.get(header, '')
                item = QTableWidgetItem(str(value))
                table_widget.setItem(row_idx, col_idx, item)
    
    def export_results(self, format=None):
        """Export current results to file"""
        if not self.current_results:
            QMessageBox.warning(self, "Error", "No results to export")
            return
        
        # Get format
        if format is None:
            format = self.export_format.currentText()
        
        # Get save path
        ext_map = {'json': 'JSON Files (*.json)', 'csv': 'CSV Files (*.csv)', 'txt': 'Text Files (*.txt)'}
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Results", "", ext_map.get(format, 'All Files (*.*)')
        )
        
        if not file_path:
            return
        
        try:
            save_results(self.current_results, file_path, format)
            QMessageBox.information(self, "Success", f"Results exported to:\n{file_path}")
            self.statusBar().showMessage(f"Exported to {Path(file_path).name}", 3000)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Export failed:\n{str(e)}")
    
    def closeEvent(self, event):
        """Handle window close"""
        if self.scraper:
            self.scraper.close()
        event.accept()


def main():
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    window = WebScraperGUI()
    window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
