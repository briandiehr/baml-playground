"""Test ExtractProductInfo function with simple examples."""

import pytest
from amzn_cost.baml_client import b


@pytest.mark.asyncio
async def test_simple_product_extraction():
    """Test basic product information extraction."""
    html_content = """
      <html>
        <body>
          <h1 id="title">Apple AirPods Pro (2nd Generation)</h1>
          <span class="a-price">
            <span class="a-price-whole">249</span>
            <span class="a-price-decimal">.</span>
            <span class="a-price-fraction">99</span>
          </span>
        </body>
      </html>
    """
    
    result = await b.ExtractProductInfo(html_content)
    
    # Check that both required fields are present
    assert hasattr(result, 'cost'), "Result should have 'cost' field"
    assert hasattr(result, 'description'), "Result should have 'description' field"
    
    # Check that cost is a valid number
    assert result.cost > 0, f"Cost should be positive, got {result.cost}"
    assert result.cost == 249.99, f"Cost should be 249.99, got {result.cost}"
    
    # Check that description is not empty
    assert len(result.description) > 0, "Description should not be empty"
    assert "AirPods" in result.description or "airpods" in result.description.lower(), \
        f"Description should mention AirPods, got: {result.description}"


@pytest.mark.asyncio
async def test_product_with_dollar_sign():
    """Test extraction when price has dollar sign."""
    html_content = """
      <html>
        <body>
          <div id="productTitle">Sony WH-1000XM5 Wireless Headphones</div>
          <span class="price">$399.99</span>
        </body>
      </html>
    """
    
    result = await b.ExtractProductInfo(html_content)
    
    assert result.cost > 0, f"Cost should be positive, got {result.cost}"
    assert result.cost == 399.99, f"Cost should be 399.99, got {result.cost}"
    assert len(result.description) > 0, "Description should not be empty"


@pytest.mark.asyncio
async def test_product_with_comma_in_price():
    """Test extraction with comma in price."""
    html_content = """
      <html>
        <body>
          <h1>MacBook Pro 16-inch M3 Max</h1>
          <div class="price-tag">$3,499.00</div>
        </body>
      </html>
    """
    
    result = await b.ExtractProductInfo(html_content)
    
    assert 3499 == result.cost, f"Cost should be 3499, got {result.cost}"
    assert len(result.description) > 0, "Description should not be empty"

