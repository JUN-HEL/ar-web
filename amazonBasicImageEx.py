import requests
from bs4 import BeautifulSoup

def scrape_amazon_product(product_name):
    # Replace spaces with "+" for search query
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
        image = item.select_one("img")
        
        if title and price and image:
            products.append({
                "title": title.text.strip(),
                "price": price.text.strip(),
                "image_url": image["src"],  # Extracting image URL
                "link": "https://www.amazon.in" + item.select_one("h2 a")["href"]
            })
    
    return products[:5]  # Return top 5 results

# Test the function
product_name = "Acer Aspire 3 Intel Core i3"
products = scrape_amazon_product(product_name)
for product in products:
    print(f"Title: {product['title']}")
    print(f"Price: {product['price']}")
    print(f"Image URL: {product['image_url']}")
    print(f"Link: {product['link']}")
    print()
