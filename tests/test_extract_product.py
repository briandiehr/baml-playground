"""Test ExtractProductInfo function with simple examples."""

import pytest
import json
import subprocess
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


@pytest.mark.slow
def test_end_to_end_cli():
    """
    End-to-end test: Call the CLI command like an end user would.
    
    This test:
    1. Runs the `amzn-cost` CLI command with a real Amazon URL
    2. Validates the JSON output
    3. Checks that cost and description are extracted correctly
    
    Note: This test requires:
    - Internet connection to fetch Amazon page
    - Local Llama instance running on localhost:11434
    - The test may take 10-30 seconds due to network and LLM processing time
    """
    # Use a stable Amazon product URL (Amazon Basics products tend to be stable)
    amazon_url = "https://www.amazon.com/Amazon-Basics-Male-USB-Cable/dp/B00NH13S44/"
    
    print(f"\n🚀 Running CLI: amzn-cost --product={amazon_url}")
    
    # Run the CLI command
    result = subprocess.run(
        ["poetry", "run", "amzn-cost", f"--product={amazon_url}"],
        capture_output=True,
        text=True,
        timeout=60  # 60 second timeout
    )
    
    # Check that command executed successfully
    assert result.returncode == 0, f"CLI command failed with return code {result.returncode}\nStderr: {result.stderr}"
    
    print(f"✅ CLI executed successfully")
    
    # Extract JSON from output (last line that looks like JSON)
    # BAML may output logs before the JSON result
    json_line = None
    for line in result.stdout.strip().split('\n'):
        line = line.strip()
        if line.startswith('{') and line.endswith('}'):
            json_line = line
    
    if not json_line:
        pytest.fail(f"No JSON output found in CLI output.\nOutput was: {result.stdout}")
    
    print(f"📤 JSON output: {json_line}")
    
    # Parse JSON output
    try:
        output = json.loads(json_line)
    except json.JSONDecodeError as e:
        pytest.fail(f"Failed to parse JSON output: {e}\nJSON was: {json_line}")
    
    # Validate the output structure
    assert "cost" in output, f"Output should have 'cost' field. Got: {output}"
    assert "description" in output, f"Output should have 'description' field. Got: {output}"
    
    cost = output["cost"]
    description = output["description"]
    
    print(f"\n📦 Extracted Product Information:")
    print(f"   Cost: ${cost}")
    print(f"   Description: {description}")
    
    # Validate cost
    assert isinstance(cost, (int, float)), f"Cost should be a number, got {type(cost)}"
    assert cost > 0, f"Cost should be positive, got {cost}"
    assert cost < 1000, f"Cost seems unreasonably high for this product: ${cost}"
    
    # Validate description
    assert isinstance(description, str), f"Description should be a string, got {type(description)}"
    assert len(description) > 5, f"Description seems too short: '{description}'"
    
    # For this specific product, we know it's a USB cable
    description_lower = description.lower()
    assert any(keyword in description_lower for keyword in ['usb', 'cable', 'amazon', 'basics']), \
        f"Description should contain relevant keywords, got: {description}"
    
    print("\n✅ End-to-end CLI test passed!")
    print(f"   Successfully tested the complete user workflow")
    print(f"   CLI → Scraper → BAML → Local Llama → JSON output")

