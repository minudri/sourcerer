"""Web scraping module for startup revenue tracker."""

import asyncio
import aiohttp
import requests
import feedparser
import time
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from loguru import logger
# import newspaper  # Removed due to compatibility issues

from .config import Config
from .database import Database, Article
from .revenue_analyzer import RevenueAnalyzer

class WebScraper:
    """Web scraper for extracting articles from news sources."""
    
    def __init__(self, database: Database):
        """Initialize the web scraper."""
        self.db = database
        self.revenue_analyzer = RevenueAnalyzer()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': Config.USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # Chrome options for Selenium
        self.chrome_options = Options()
        self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        self.chrome_options.add_argument('--disable-gpu')
        self.chrome_options.add_argument(f'--user-agent={Config.USER_AGENT}')
    
    def get_driver(self) -> webdriver.Chrome:
        """Get a Chrome WebDriver instance."""
        try:
            return webdriver.Chrome(
                ChromeDriverManager().install(),
                options=self.chrome_options
            )
        except Exception as e:
            logger.error(f"Failed to create Chrome driver: {e}")
            return None
    
    async def scrape_all_sources(self) -> List[Article]:
        """Scrape all configured news sources."""
        all_articles = []
        
        for source_name, source_config in Config.NEWS_SOURCES.items():
            logger.info(f"Scraping {source_name}...")
            try:
                articles = await self.scrape_source(source_name, source_config)
                all_articles.extend(articles)
                logger.info(f"Found {len(articles)} articles from {source_name}")
                
                # Delay between sources to be respectful
                await asyncio.sleep(Config.REQUEST_DELAY)
                
            except Exception as e:
                logger.error(f"Failed to scrape {source_name}: {e}")
                continue
        
        return all_articles
    
    async def scrape_source(self, source_name: str, source_config: Dict) -> List[Article]:
        """Scrape a single news source."""
        articles = []
        
        # Try RSS feed first if available
        if 'rss_feed' in source_config:
            try:
                rss_articles = await self.scrape_rss_feed(source_name, source_config['rss_feed'])
                articles.extend(rss_articles)
            except Exception as e:
                logger.warning(f"RSS scraping failed for {source_name}: {e}")
        
        # Fallback to web scraping
        if len(articles) < 10:  # If RSS didn't give us enough articles
            try:
                web_articles = await self.scrape_website(source_name, source_config)
                articles.extend(web_articles)
            except Exception as e:
                logger.warning(f"Web scraping failed for {source_name}: {e}")
        
        return articles
    
    async def scrape_rss_feed(self, source_name: str, rss_url: str) -> List[Article]:
        """Scrape articles from RSS feed."""
        articles = []
        
        try:
            feed = feedparser.parse(rss_url)
            
            for entry in feed.entries[:20]:  # Limit to last 20 articles
                # Skip if article already exists
                if self.db.article_exists(entry.link):
                    continue
                
                # Parse published date
                published_date = None
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    published_date = datetime(*entry.published_parsed[:6])
                
                # Skip articles older than 7 days
                if published_date and (datetime.now() - published_date).days > 7:
                    continue
                
                # Get full article content
                content = await self.get_article_content(entry.link, source_name)
                
                article = Article(
                    source=source_name,
                    title=entry.title,
                    url=entry.link,
                    content=content,
                    published_date=published_date
                )
                
                # Analyze for revenue information
                revenue_info = self.revenue_analyzer.analyze_article(article)
                if revenue_info:
                    article.revenue_found = True
                    article.revenue_amount = revenue_info['amount']
                    article.revenue_type = revenue_info['type']
                    article.company_name = revenue_info['company']
                
                articles.append(article)
                
                # Save to database
                self.db.save_article(article)
                
                # Delay between requests
                await asyncio.sleep(Config.REQUEST_DELAY)
        
        except Exception as e:
            logger.error(f"Error scraping RSS feed {rss_url}: {e}")
        
        return articles
    
    async def scrape_website(self, source_name: str, source_config: Dict) -> List[Article]:
        """Scrape articles directly from website."""
        articles = []
        base_url = source_config['base_url']
        
        try:
            # Try different search patterns
            for pattern in source_config.get('search_patterns', ['/']):
                search_url = urljoin(base_url, pattern)
                
                # Get page content
                response = self.session.get(search_url, timeout=30)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find article links
                article_links = self.extract_article_links(soup, source_config, base_url)
                
                for link in article_links[:10]:  # Limit to 10 articles per pattern
                    if self.db.article_exists(link):
                        continue
                    
                    # Get article content
                    content = await self.get_article_content(link, source_name)
                    
                    if content:
                        article = Article(
                            source=source_name,
                            title=self.extract_title_from_content(content),
                            url=link,
                            content=content
                        )
                        
                        # Analyze for revenue information
                        revenue_info = self.revenue_analyzer.analyze_article(article)
                        if revenue_info:
                            article.revenue_found = True
                            article.revenue_amount = revenue_info['amount']
                            article.revenue_type = revenue_info['type']
                            article.company_name = revenue_info['company']
                        
                        articles.append(article)
                        self.db.save_article(article)
                    
                    await asyncio.sleep(Config.REQUEST_DELAY)
        
        except Exception as e:
            logger.error(f"Error scraping website {base_url}: {e}")
        
        return articles
    
    def extract_article_links(self, soup: BeautifulSoup, source_config: Dict, base_url: str) -> List[str]:
        """Extract article links from a page."""
        links = []
        selectors = source_config.get('selectors', {})
        
        # Try different selectors to find article links
        possible_selectors = [
            selectors.get('articles', ''),
            'article a',
            '.article-link',
            '.post-title a',
            'h2 a',
            'h3 a',
            '.headline a'
        ]
        
        for selector in possible_selectors:
            if selector:
                try:
                    elements = soup.select(selector)
                    for element in elements:
                        href = element.get('href')
                        if href:
                            full_url = urljoin(base_url, href)
                            if self.is_valid_article_url(full_url):
                                links.append(full_url)
                except Exception:
                    continue
        
        return list(set(links))  # Remove duplicates
    
    def is_valid_article_url(self, url: str) -> bool:
        """Check if URL looks like a valid article URL."""
        # Skip certain patterns that are unlikely to be articles
        skip_patterns = [
            '/tag/', '/category/', '/author/', '/page/',
            '/search/', '/archive/', '/feed/', '/rss/',
            '.jpg', '.png', '.gif', '.pdf', '.css', '.js'
        ]
        
        for pattern in skip_patterns:
            if pattern in url.lower():
                return False
        
        return True
    
    async def get_article_content(self, url: str, source_name: str) -> str:
        """Extract full article content from URL."""
        try:
            # First try with newspaper3k for better content extraction
            article = newspaper.Article(url)
            article.download()
            article.parse()
            
            if article.text and len(article.text) > 200:
                return article.text
        
        except Exception as e:
            logger.debug(f"Newspaper3k failed for {url}: {e}")
        
        # Fallback to requests + BeautifulSoup
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "aside"]):
                script.decompose()
            
            # Try different content selectors
            content_selectors = [
                '.article-content',
                '.post-content',
                '.entry-content',
                '.content',
                'article',
                '.story-body',
                '.article-body'
            ]
            
            content = ""
            for selector in content_selectors:
                elements = soup.select(selector)
                if elements:
                    content = elements[0].get_text(strip=True)
                    if len(content) > 200:
                        break
            
            if not content:
                # Fallback to body text
                content = soup.get_text(strip=True)
            
            return content[:10000]  # Limit content length
        
        except Exception as e:
            logger.error(f"Failed to get content from {url}: {e}")
            return ""
    
    def extract_title_from_content(self, content: str) -> str:
        """Extract title from content if not available separately."""
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if line and len(line) < 200 and len(line) > 10:
                return line
        return "Untitled Article"
    
    async def scrape_with_selenium(self, url: str) -> str:
        """Use Selenium for JavaScript-heavy sites."""
        driver = self.get_driver()
        if not driver:
            return ""
        
        try:
            driver.get(url)
            
            # Wait for content to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "article"))
            )
            
            # Get page source and extract content
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            # Remove unwanted elements
            for element in soup(["script", "style", "nav", "footer", "aside"]):
                element.decompose()
            
            content = soup.get_text(strip=True)
            return content[:10000]
        
        except Exception as e:
            logger.error(f"Selenium scraping failed for {url}: {e}")
            return ""
        
        finally:
            driver.quit()
    
    def close(self):
        """Clean up resources."""
        self.session.close()