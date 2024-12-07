import requests
from bs4 import BeautifulSoup
def scrape_amazon(product_name):
    # Replace spaces with "+" for search query
    search_query = product_name.replace(" ", "+")
    url = f"https://www.amazon.in/s?k={search_query}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36"
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")

    # Extract product titles and prices
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

    return products[:5]  # Return top 5 results
if __name__ == "__main__":
    product_name = input("Enter product name to search on Amazon: ")
    results = scrape_amazon(product_name)
    for idx, product in enumerate(results, 1):
        print(f"{idx}. {product['title']} - ₹{product['price']}")
        print(f"   Link: {product['link']}")