"""CLI interface for amzn-cost."""

import json
import click
from .scraper import AmazonScraper
from .parser import ProductParser


@click.command()
@click.option(
    "--product",
    required=True,
    help="Amazon product URL",
)
def main(product: str):
    """
    Fetch Amazon product price and description.
    
    Example:
        amzn-cost --product=https://www.amazon.com/product-name/dp/XXXXXXXXXX/
    """
    try:
        # Scrape the Amazon product page
        scraper = AmazonScraper()
        html_content = scraper.fetch_product_page(product)
        
        # Clean HTML to remove JavaScript, CSS, and keep only product content
        cleaned_html = scraper.clean_html(html_content)
        
        # Parse using BAML
        parser = ProductParser()
        result = parser.parse_product(cleaned_html)
        
        # Output as JSON
        output = {
            "cost": result.cost,
            "description": result.description
        }
        click.echo(json.dumps(output))
        
    except Exception as e:
        click.echo(json.dumps({"error": str(e)}), err=True)
        raise click.Abort()


if __name__ == "__main__":
    main()

