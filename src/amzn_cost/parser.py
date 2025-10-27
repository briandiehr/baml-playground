"""Product information parser using BAML."""

import asyncio
import logging
import os
from typing import Any

# Suppress BAML logging to stdout
logging.getLogger("baml_py").setLevel(logging.ERROR)
os.environ["BAML_LOG_LEVEL"] = "ERROR"

try:
    from .baml_client import b
    from .baml_client.types import ProductInfo
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
    
    def parse_product(self, html_content: str) -> Any:
        """
        Parse product information from HTML using BAML.
        
        Args:
            html_content: Raw HTML from the Amazon product page
            
        Returns:
            ProductInfo object containing cost and description
        """
        # Run the async function synchronously
        result = asyncio.run(b.ExtractProductInfo(html_content))
        return result

