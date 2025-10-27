"""Product information parser using BAML."""

from typing import Any

try:
    from baml_py import b
    from baml_client import BamlClient
    from baml_client.types import ProductInfo
    BAML_AVAILABLE = True
except ImportError:
    BAML_AVAILABLE = False
    # Fallback type definition
    class ProductInfo:
        def __init__(self, cost: float, description: str):
            self.cost = cost
            self.description = description


class ProductParser:
    """Handles parsing Amazon product information using BAML."""
    
    def __init__(self):
        """Initialize the BAML client."""
        if not BAML_AVAILABLE:
            raise RuntimeError(
                "BAML client not generated. Please run: poetry run baml-cli generate"
            )
        self.client = BamlClient()
    
    def parse_product(self, html_content: str) -> Any:
        """
        Parse product information from HTML using BAML.
        
        Args:
            html_content: Raw HTML from the Amazon product page
            
        Returns:
            ProductInfo object containing cost and description
        """
        result = b.ExtractProductInfo(html_content)
        return result

