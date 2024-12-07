from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import json
import requests
from bs4 import BeautifulSoup

app = FastAPI()

# Serve static files (like products_data.json)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Scrape data from Amazon
def scrape_amazon(product_name):
    search_query = product_name.replace(" ", "+")
    url = f"https://www.amazon.in/s?k={search_query}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36"
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")

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
    return products

# Save scraped data to a JSON file
def save_scraped_data(product_name):
    amazon_data = scrape_amazon(product_name)
    with open("static/products_data.json", "w") as f:
        json.dump({"products": amazon_data}, f, indent=4)

    return "Scraping completed and data saved!"

# Index route to serve the AR HTML page
@app.get("/", response_class=HTMLResponse)
async def index():
    with open('static/index.html', 'r') as f:
        return f.read()

# Scrape route to trigger scraping of products
@app.get("/scrape/{product_name}")
async def scrape(product_name: str):
    message = save_scraped_data(product_name)
    return {"message": message}
