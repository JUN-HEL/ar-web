import requests
import random
import time
from bs4 import BeautifulSoup
import json

# List of User-Agents for rotation
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36 Edg/91.0.864.67",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"
]

# Function to scrape Amazon
def scrape_amazon(product_name):
    search_query = product_name.replace(" ", "+")
    url = f"https://www.amazon.in/s?k={search_query}"

    headers = {
        "User-Agent": random.choice(user_agents)
    }

    retries = 3
    for _ in range(retries):
        try:
            response = requests.get(url, headers=headers)
            print(f"Amazon status code: {response.status_code}")  # Debugging
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

            if not products:
                print("No products found on Amazon.")  # Debugging

            return products[:5]

        except Exception as e:
            print(f"Error fetching Amazon data: {e}")
            time.sleep(2)  # Wait before retrying
    return []

# Function to save data to JSON file
def save_to_json(data, filename='products_data.json'):
    try:
        with open(filename, 'w') as file:
            json.dump(data, file, indent=4)
        print(f"Data has been saved to '{filename}'")
    except Exception as e:
        print(f"Error saving data to JSON: {e}")

if __name__ == "__main__":
    product_name = input("Enter product name to search: ")

    # Scraping data from Amazon
    print("Scraping Amazon...")
    amazon_results = scrape_amazon(product_name)

    # Combined data
    combined_data = {
        "amazon": amazon_results
    }

    # Saving data to a JSON file
    save_to_json(combined_data)

    # Displaying results
    if amazon_results:
        print("\nAmazon Products:")
        for idx, product in enumerate(amazon_results, 1):
            print(f"{idx}. {product['title']} - ₹{product['price']}")
            print(f"   Link: {product['link']}")
    else:
        print("\nNo Amazon results found.")
