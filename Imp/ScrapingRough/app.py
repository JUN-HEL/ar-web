from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import requests
import random
import time
from bs4 import BeautifulSoup
from typing import List

# FastAPI app instance
app = FastAPI()

# List of User-Agents for rotation
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36 Edg/91.0.864.67",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"
]

# Data model for the product
class Product(BaseModel):
    title: str
    price: str
    link: str

# Function to scrape Amazon
def scrape_amazon(product_name: str):
    search_query = product_name.replace(" ", "+")
    url = f"https://www.amazon.in/s?k={search_query}"

    headers = {
        "User-Agent": random.choice(user_agents)
    }

    retries = 3
    for _ in range(retries):
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Raise an exception for HTTP errors

            soup = BeautifulSoup(response.content, "html.parser")
            
            # Extract products
            products = []
            for item in soup.select(".s-main-slot .s-result-item"):
                title = item.select_one("h2 a span")
                price = item.select_one(".a-price-whole")
                if title and price:
                    products.append({
                        "title": title.text.strip(),
                        "price": price.text.strip(),
                        "link": "https://www.amazon.in" + item.select_one("h2 a")["href"]
                    })

            return products[:5]

        except Exception as e:
            print(f"Error fetching Amazon data: {e}")
            time.sleep(2)  # Wait before retrying
    return []

# FastAPI endpoint for scraping Amazon
@app.post("/search", response_model=List[Product])
async def search_endpoint(request: Request):
    data = await request.form()
    product_name = data.get("product_name")

    amazon_results = scrape_amazon(product_name)

    # Return the scraped data
    return amazon_results

# Serve the HTML page
@app.get("/", response_class=HTMLResponse)
async def get_homepage():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Product Scraper</title>
        <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    </head>
    <body>
        <h1>Search for Products</h1>
        <form id="searchForm">
            <input type="text" id="product_name" name="product_name" placeholder="Enter product name" required>
            <button type="submit">Search</button>
        </form>

        <div id="results"></div>

        <script>
            $(document).ready(function() {
                $('#searchForm').on('submit', function(event) {
                    event.preventDefault();
                    var product_name = $('#product_name').val();

                    $.post('/search', { product_name: product_name }, function(data) {
                        $('#results').empty(); // Clear previous results
                        if (data.length > 0) {
                            data.forEach(function(product, index) {
                                $('#results').append(
                                    '<h3>' + product.title + '</h3>' +
                                    '<p>Price: ₹' + product.price + '</p>' +
                                    '<a href="' + product.link + '" target="_blank">View Product</a><hr>'
                                );
                            });
                        } else {
                            $('#results').append('<p>No products found.</p>');
                        }
                    });
                });
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
