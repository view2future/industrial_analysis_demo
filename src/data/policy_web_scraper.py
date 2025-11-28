#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Policy Web Scraper Module
Scrape policy articles from URLs provided via email
"""

import requests
from bs4 import BeautifulSoup
import logging
from typing import Dict, Optional
import time
import urllib.parse
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


logger = logging.getLogger(__name__)


class PolicyWebScraper:
    """
    Web scraper for policy articles from URLs
    """

    def __init__(self):
        """Initialize the policy web scraper"""
        self.session = self._create_session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def _create_session(self):
        """Create a requests session with retry strategy"""
        session = requests.Session()
        
        # Define retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session

    def scrape_policy_content(self, url: str) -> Optional[Dict]:
        """
        Scrape policy content from a given URL
        
        Args:
            url: URL to scrape
            
        Returns:
            Dictionary containing scraped content or None if failed
        """
        try:
            logger.info(f"🔍 Scraping policy content from: {url}")
            
            # Make request with headers
            response = self.session.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            # Parse HTML content
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title = self._extract_title(soup)
            
            # Extract content
            content = self._extract_content(soup)
            
            # Extract metadata
            metadata = self._extract_metadata(soup, url)
            
            # Clean content
            clean_content = self._clean_content(content)
            
            result = {
                'url': url,
                'title': title,
                'content': clean_content,
                'metadata': metadata,
                'scraped_at': time.time(),
                'status': 'success'
            }
            
            logger.info(f"✅ Successfully scraped policy: {title[:50]}...")
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Request error while scraping {url}: {e}")
            return {
                'url': url,
                'error': f'Request error: {str(e)}',
                'status': 'error'
            }
        except Exception as e:
            logger.error(f"❌ Error scraping {url}: {e}")
            return {
                'url': url,
                'error': f'Parsing error: {str(e)}',
                'status': 'error'
            }

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract title from the page"""
        try:
            # Try common title selectors
            title_selectors = [
                'h1',  # Most common
                '.title',  # Class-based titles
                '#title',  # ID-based titles
                'title',  # HTML title tag
                '[class*="title"]',  # Titles with "title" in class name
                '[class*="headline"]'  # Headlines
            ]
            
            for selector in title_selectors:
                element = soup.select_one(selector)
                if element and element.get_text(strip=True):
                    return element.get_text(strip=True)
            
            # Fallback to HTML title
            title_tag = soup.find('title')
            if title_tag:
                return title_tag.get_text(strip=True)
            
            return "未找到标题"
        except Exception as e:
            logger.warning(f"Error extracting title: {e}")
            return "未找到标题"

    def _extract_content(self, soup: BeautifulSoup) -> str:
        """Extract main content from the page"""
        try:
            # Remove unwanted elements first
            for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'advertisement']):
                element.decompose()
            
            # Try common content selectors
            content_selectors = [
                '.article-content',  # Common content class
                '.post-content',     # Blog post content
                '.content',          # Generic content
                '.main-content',     # Main content area
                '.entry-content',    # WordPress content
                '.article-body',     # Article body
                'article',           # HTML5 article tag
                '.text-content',     # Text content
                '.policy-content',   # Policy specific
                '[class*="content"]', # Content with "content" in class name
                'main'               # Main tag
            ]
            
            for selector in content_selectors:
                elements = soup.select(selector)
                if elements:
                    content_parts = []
                    for element in elements:
                        content_parts.append(element.get_text())
                    if content_parts:
                        return '\n'.join(content_parts)
            
            # If no specific content found, try paragraph tags
            paragraphs = soup.find_all(['p', 'div', 'section'])
            content_parts = []
            
            for p in paragraphs:
                text = p.get_text(strip=True)
                if text and len(text) > 50:  # Only include substantial text blocks
                    content_parts.append(text)
            
            if content_parts:
                return '\n'.join(content_parts)
            
            # Fallback to body content
            body = soup.find('body')
            if body:
                return body.get_text()
            
            return ""
        except Exception as e:
            logger.warning(f"Error extracting content: {e}")
            return ""

    def _extract_metadata(self, soup: BeautifulSoup, url: str) -> Dict:
        """Extract metadata from the page"""
        metadata = {
            'url': url,
            'domain': urllib.parse.urlparse(url).netloc,
            'author': '',
            'publish_date': '',
            'source': urllib.parse.urlparse(url).netloc
        }
        
        try:
            # Extract author
            author_selectors = [
                '[class*="author"]',
                '[rel="author"]',
                '.byline',
                '.author',
                '[name="author"]',
                'meta[name="author"]'
            ]
            
            for selector in author_selectors:
                element = soup.select_one(selector)
                if element:
                    if element.name == 'meta':
                        metadata['author'] = element.get('content', '')
                    else:
                        metadata['author'] = element.get_text(strip=True)
                    if metadata['author']:
                        break
            
            # Extract publish date
            date_selectors = [
                '[class*="date"]',
                '[class*="time"]',
                'time',
                '[name="date"]',
                'meta[name="publish"]',
                'meta[name="pubdate"]',
                'meta[property="article:published_time"]'
            ]
            
            for selector in date_selectors:
                element = soup.select_one(selector)
                if element:
                    if element.name == 'meta':
                        date_value = element.get('content', element.get('datetime', ''))
                    else:
                        date_value = element.get_text(strip=True)
                    
                    if date_value:
                        metadata['publish_date'] = date_value
                        break
        
        except Exception as e:
            logger.warning(f"Error extracting metadata: {e}")
        
        return metadata

    def _clean_content(self, content: str) -> str:
        """Clean and normalize the scraped content"""
        if not content:
            return ""
        
        # Remove extra whitespace
        import re
        cleaned = re.sub(r'\s+', ' ', content)
        
        # Remove common navigation elements that might have slipped through
        patterns_to_remove = [
            r'上一篇.*?下一篇',
            r'相关推荐.*',
            r'网友评论.*',
            r'分享到.*',
            r'关注我们.*',
            r'回到顶部.*'
        ]
        
        for pattern in patterns_to_remove:
            cleaned = re.sub(pattern, '', cleaned, flags=re.DOTALL | re.IGNORECASE)
        
        return cleaned.strip()

    def batch_scrape_urls(self, urls: list) -> list:
        """Scrape multiple URLs and return results"""
        results = []
        
        for i, url in enumerate(urls):
            logger.info(f"Progress: {i+1}/{len(urls)} - Scraping: {url}")
            
            result = self.scrape_policy_content(url)
            results.append(result)
            
            # Add small delay to be respectful to servers
            time.sleep(1)
        
        return results

    def validate_url(self, url: str) -> bool:
        """Validate if URL is potentially a policy document"""
        try:
            parsed = urllib.parse.urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                return False
            
            # Check for common policy document indicators
            lower_url = url.lower()
            policy_indicators = [
                'policy', '政策', 'guidance', '指引', 'notice', '通知', 
                'regulation', '法规', 'rule', '规则', 'standard', '标准',
                'goverment', '政府', 'official', '官方', 'document', '文件'
            ]
            
            return any(indicator in lower_url for indicator in policy_indicators)
            
        except Exception:
            return False


if __name__ == "__main__":
    # Test the scraper
    logging.basicConfig(level=logging.INFO)
    
    scraper = PolicyWebScraper()
    
    # Test with a sample URL (this would be from email)
    test_urls = [
        "https://example.com/sample-policy",  # Placeholder
    ]
    
    for url in test_urls:
        print(f"\nTesting URL: {url}")
        result = scraper.scrape_policy_content(url)
        if result:
            print(f"Title: {result.get('title', 'N/A')[:50]}")
            print(f"Content length: {len(result.get('content', ''))} characters")
            print(f"Status: {result.get('status', 'N/A')}")
    
    print("\n✅ Policy web scraper module ready!")