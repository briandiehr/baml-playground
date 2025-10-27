"""Amazon product page scraper."""

import requests
import re
from typing import Optional


class AmazonScraper:
    """Scraper for fetching Amazon product pages."""
    
    def __init__(self, timeout: int = 10):
        """
        Initialize the scraper.
        
        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
    
    def fetch_product_page(self, url: str) -> str:
        """
        Fetch HTML content from an Amazon product page.
        
        Args:
            url: Amazon product URL
            
        Returns:
            Raw HTML content as string
            
        Raises:
            ValueError: If URL is not an Amazon product URL
            requests.RequestException: If fetching fails
        """
        if not self._is_valid_amazon_url(url):
            raise ValueError(f"Invalid Amazon product URL: {url}")
        
        try:
            response = requests.get(
                url,
                headers=self.headers,
                timeout=self.timeout,
                allow_redirects=True
            )
            response.raise_for_status()
            return response.text
            
        except requests.RequestException as e:
            raise requests.RequestException(f"Failed to fetch Amazon page: {str(e)}")
    
    def _is_valid_amazon_url(self, url: str) -> bool:
        """
        Check if URL is a valid Amazon product URL.
        
        Args:
            url: URL to validate
            
        Returns:
            True if valid Amazon URL, False otherwise
        """
        return 'amazon.com' in url.lower() or 'amazon.' in url.lower()
    
    def clean_html(self, html: str) -> str:
        """
        Extract only product title and price from HTML using BeautifulSoup.
        This creates minimal HTML to avoid token limits.
        
        Args:
            html: Raw HTML content
            
        Returns:
            Minimal HTML with only product title and price
        """
        from bs4 import BeautifulSoup
        
        # Parse HTML
        soup = BeautifulSoup(html, 'lxml')
        
        # Try to find product title
        title = "Product title not found"
        title_selectors = [
            ('id', 'productTitle'),
            ('id', 'title'),
            ('class', 'product-title'),
        ]
        
        for attr, value in title_selectors:
            title_elem = soup.find(['h1', 'span', 'div'], {attr: value})
            if title_elem:
                title = title_elem.get_text(strip=True)
                break
        
        # Try to find product price
        price = "Price not found"
        price_selectors = [
            ('class', 'a-price'),
            ('class', 'price'),
            ('class', 'priceblock_ourprice'),
            ('id', 'priceblock_ourprice'),
        ]
        
        for attr, value in price_selectors:
            price_elem = soup.find(['span', 'div'], {attr: value})
            if price_elem:
                price = price_elem.get_text(strip=True)
                break
        
        # Construct minimal HTML
        minimal_html = f"""<html>
<body>
<h1 id="productTitle">{title}</h1>
<span class="price">{price}</span>
</body>
</html>"""
        
        return minimal_html

