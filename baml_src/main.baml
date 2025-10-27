// BAML Configuration for Amazon Product Parser

class ProductInfo {
  cost float
  description string
}

// Define the LLM client (using Llama 8b as per user preference)
client<llm> LocalLlama {
  provider "openai-generic"
  options {
    model "llama3.1:8b"
    api_key "dummy-key-not-needed-for-local"
    base_url "http://localhost:11434/v1"
    max_tokens 500
    temperature 0.1
  }
}
// Main function to extract product information from HTML
function ExtractProductInfo(html_content: string) -> ProductInfo {
  client LocalLlama
  prompt #"
    {{ _.role("user") }}
    Extract the product cost and description from this HTML and respond with ONLY valid JSON.
    
    HTML:
    {{ html_content }}
    
    Respond with JSON:
    {"cost": <number>, "description": "<text>"}
  "#
}

test SimpleProductWithClearPrice {
  functions [ExtractProductInfo]
  args {
    html_content #"
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
    "#
  }
  @@assert({{ this.cost > 0 }})
  @@assert({{ this.cost > 240 and this.cost < 260 }})
  @@assert({{ this.description|length > 0 }})
}

test ProductWithDollarSign {
  functions [ExtractProductInfo]
  args {
    html_content #"
      <html>
        <body>
          <div id="productTitle">Sony WH-1000XM5 Wireless Headphones</div>
          <span class="price">$399.99</span>
        </body>
      </html>
    "#
  }
  @@assert({{ this.cost > 390 and this.cost < 410 }})
  @@assert({{ this.description|length > 0 }})
}

test ProductWithCommaInPrice {
  functions [ExtractProductInfo]
  args {
    html_content #"
      <html>
        <body>
          <h1>MacBook Pro 16-inch M3 Max</h1>
          <div class="price-tag">$3,499.00</div>
        </body>
      </html>
    "#
  }
  @@assert({{ this.cost > 3000 }})
  @@assert({{ this.cost > 3400 and this.cost < 3600 }})
  @@assert({{ this.description|length > 0 }})
}

test ProductWithMinimalHtml {
  functions [ExtractProductInfo]
  args {
    html_content #"
      <div>
        <p>Samsung Galaxy S24 Ultra</p>
        <p>Price: 1199.99</p>
      </div>
    "#
  }
  @@assert({{ this.cost > 0 }})
  @@assert({{ this.description|length > 0 }})
}

test ProductWithSalePrice {
  functions [ExtractProductInfo]
  args {
    html_content #"
      <html>
        <body>
          <h1 class="product-title">Kindle Paperwhite (16 GB)</h1>
          <span class="old-price" style="text-decoration: line-through;">$159.99</span>
          <span class="current-price">$129.99</span>
        </body>
      </html>
    "#
  }
  @@assert({{ this.cost > 0 }})
  @@assert({{ this.cost < 200 }})
  @@assert({{ this.description|length > 0 }})
}

test ProductWithComplexDescription {
  functions [ExtractProductInfo]
  args {
    html_content #"
      <html>
        <body>
          <div id="title-section">
            <h1>
              Logitech MX Master 3S - Wireless Performance Mouse with Ultra-fast Scrolling, 
              Ergonomic Design, 8K DPI, Track on Glass, Quiet Clicks, USB-C, Bluetooth, 
              Windows, Linux, Chrome - Pale Grey
            </h1>
          </div>
          <span class="price-symbol">$</span>
          <span class="price-value">99</span>
          <span class="price-cents">.99</span>
        </body>
      </html>
    "#
  }
  @@assert({{ this.cost > 90 and this.cost < 110 }})
  @@assert({{ this.description|length > 10 }})
}

test ProductWithWholeNumberPrice {
  functions [ExtractProductInfo]
  args {
    html_content #"
      <html>
        <body>
          <h1>Amazon Basics HDMI Cable</h1>
          <div class="price">$10</div>
        </body>
      </html>
    "#
  }
  @@assert({{ this.cost > 0 }})
  @@assert({{ this.cost >= 10 and this.cost <= 10 }})
  @@assert({{ this.description|length > 0 }})
}

test ProductWithNestedHtmlStructure {
  functions [ExtractProductInfo]
  args {
    html_content #"
      <html>
        <head><title>Product Page</title></head>
        <body>
          <div class="container">
            <div class="product-section">
              <div class="product-info">
                <div class="title-wrapper">
                  <h1 id="productTitle">
                    Anker 737 Power Bank (PowerCore 24K)
                  </h1>
                </div>
                <div class="pricing-wrapper">
                  <div class="price-container">
                    <span class="a-price" data-a-color="price">
                      <span class="a-offscreen">$149.99</span>
                      <span aria-hidden="true">
                        <span class="a-price-symbol">$</span>
                        <span class="a-price-whole">149</span>
                        <span class="a-price-decimal">.</span>
                        <span class="a-price-fraction">99</span>
                      </span>
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </body>
      </html>
    "#
  }
  @@assert({{ this.cost > 140 and this.cost < 160 }})
  @@assert({{ this.description|length > 0 }})
}

test ProductWithSpecialCharacters {
  functions [ExtractProductInfo]
  args {
    html_content #"
      <html>
        <body>
          <h1>ASUS ROG Strix G16 (2024) Gaming Laptop, 16" 16:10 FHD 165Hz</h1>
          <div class="price-block">
            <span>$1,649.99</span>
          </div>
        </body>
      </html>
    "#
  }
  @@assert({{ this.cost > 1000 }})
  @@assert({{ this.cost > 1600 and this.cost < 1700 }})
  @@assert({{ this.description|length > 5 }})
}

test ProductWithPriceInTextFormat {
  functions [ExtractProductInfo]
  args {
    html_content #"
      <html>
        <body>
          <h1>Portable SSD T7 Shield 1TB</h1>
          <div class="price-info">Price: $89.99</div>
        </body>
      </html>
    "#
  }
  @@assert({{ this.cost > 0 }})
  @@assert({{ this.cost > 80 and this.cost < 100 }})
  @@assert({{ this.description|length > 0 }})
}

test ProductWithMultiplePriceElements {
  functions [ExtractProductInfo]
  args {
    html_content #"
      <html>
        <body>
          <div class="product">
            <h2>Wireless Mouse</h2>
            <span class="shipping">Shipping: $5.99</span>
            <span class="price">Product Price: $29.99</span>
            <span class="tax">Tax: $2.50</span>
          </div>
        </body>
      </html>
    "#
  }
  @@assert({{ this.cost > 0 }})
  @@assert({{ this.description|length > 0 }})
}

test ProductWithAmazonTypicalStructure {
  functions [ExtractProductInfo]
  args {
    html_content #"
      <html>
        <body>
          <div id="dp" class="product-page">
            <div id="centerCol">
              <div id="title_feature_div">
                <h1 id="title" class="a-size-large a-spacing-none">
                  <span id="productTitle">
                    Echo Dot (5th Gen, 2022 release) | With bigger vibrant sound, helpful routines and Alexa | Deep Sea Blue
                  </span>
                </h1>
              </div>
              <div id="corePriceDisplay_desktop_feature_div">
                <div class="a-section">
                  <span class="a-price aok-align-center reinventPricePriceToPayPadding priceToPay">
                    <span class="a-offscreen">$49.99</span>
                    <span aria-hidden="true">
                      <span class="a-price-symbol">$</span>
                      <span class="a-price-whole">49<span class="a-price-decimal">.</span></span>
                      <span class="a-price-fraction">99</span>
                    </span>
                  </span>
                </div>
              </div>
            </div>
          </div>
        </body>
      </html>
    "#
  }
  @@assert({{ this.cost > 45 and this.cost < 55 }})
  @@assert({{ this.description|length > 0 }})
}

test ProductWithInternationalPrice {
  functions [ExtractProductInfo]
  args {
    html_content #"
      <html>
        <body>
          <h1>Café™ Smart Coffee Maker – Premium Edition®</h1>
          <div class="price">€89.99</div>
        </body>
      </html>
    "#
  }
  @@assert({{ this.cost > 0 }})
  @@assert({{ this.description|length > 0 }})
}

test ProductWithLongTitle {
  functions [ExtractProductInfo]
  args {
    html_content #"
      <html>
        <body>
          <h1 id="productTitle" class="a-size-large product-title-word-break">
            Apple 2024 MacBook Pro Laptop with M4 chip: Built for Apple Intelligence, 14.2-inch Liquid Retina XDR Display, 16GB Unified Memory, 512GB SSD Storage; Space Black; English (US)
          </h1>
          <span class="a-price">
            <span class="a-offscreen">$1,599.00</span>
            <span class="a-price-whole">1,599</span>
            <span class="a-price-decimal">.</span>
            <span class="a-price-fraction">00</span>
          </span>
        </body>
      </html>
    "#
  }
  @@assert({{ this.cost > 1500 and this.cost < 1650 }})
  @@assert({{ this.description|length > 20 }})
}

test ProductBundleWithMultipleItems {
  functions [ExtractProductInfo]
  args {
    html_content #"
      <html>
        <body>
          <h1>Gaming Bundle - Keyboard + Mouse + Headset</h1>
          <div class="bundle-info">
            <p>Save 20% when you buy together</p>
          </div>
          <div class="price-section">
            <span class="bundle-price">$159.99</span>
          </div>
        </body>
      </html>
    "#
  }
  @@assert({{ this.cost > 150 and this.cost < 170 }})
  @@assert({{ this.description|length > 0 }})
}
