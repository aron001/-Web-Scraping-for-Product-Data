import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

# Setup Selenium with ChromeDriver
def init_driver(headless=True):
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument('--headless')  # Run headless for faster scraping
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver

# Function to scrape data from a given website
def scrape_website(url, parser_function):
    driver = init_driver(headless=False)  # Run with headless=False for debugging
    driver.get(url)
    
    # Wait for the page to fully load
    time.sleep(10)  # Increase time if needed
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    data = parser_function(soup)  # Pass soup to parser function
    driver.quit()
    return data

# Warhammer (Element Games) scraping
def parse_element_games(soup):
    product_data = []
    
    # Debugging: Print the entire page source to verify structure
    # print(soup.prettify())  # Uncomment this to see the HTML structure

    # Find product containers by inspecting
    products = soup.find_all('div', class_='product-list-item')  # Adjust this if necessary
    print(f"Found {len(products)} products in Element Games")  # Debugging

    for product in products:
        title_tag = product.find('h3', class_='producttitle')  # Check this selector
        price_tag = product.find('span', class_='price')  # Check this selector
        stock_tag = product.find('div', class_='stock_popup') or product.find('img', src='//images/green-button.png')
        
        if title_tag and price_tag:
            title = title_tag.text.strip()
            price = price_tag.text.strip()
            stock = stock_tag.text.strip() if stock_tag else 'Out of Stock'
            product_data.append([title, 'N/A', price, stock])
    
    return product_data

# Wayland Games scraping
def parse_wayland_games(soup):
    product_data = []

    # Debugging: Print the entire page source to verify structure
    # print(soup.prettify())  # Uncomment this to see the HTML structure

    # Find product containers by inspecting
    products = soup.find_all('a', aria_label=True)  # Use the aria-label selector for titles
    print(f"Found {len(products)} products in Wayland Games")  # Debugging

    for product in products:
        title_tag = product
        price_tag = product.find_next('span', class_='Price_price__sfl_r Price_priceNow__OV_3o')  # Get the price
        stock_tag = product.find_next('span', text=lambda x: x and 'in stock' in x.lower())  # Get the stock

        if title_tag and price_tag:
            title = title_tag.text.strip()
            url = "https://www.waylandgames.co.uk" + title_tag['href']  # Construct the full URL
            price = price_tag.text.strip() if price_tag else 'Price not available'
            stock = stock_tag.text.strip() if stock_tag else 'Out of Stock'
            product_data.append([title, url, price, stock])

    return product_data

# Argos scraping
def parse_argos(soup):
    product_data = []
    
    # Find product containers based on the current structure
    products = soup.find_all('div', attrs={'data-test': 'component-product-card-title'})  # Check this selector
    
    for product in products:
        title_tag = product
        price_tag = product.find_next('strong')
        stock = 'In Stock'  # Argos stock logic can vary, adjust as needed
        
        if title_tag and price_tag:
            title = title_tag.text.strip()
            price = price_tag.text.strip()
            product_data.append([title, 'N/A', price, stock])
    
    return product_data

# Main function to scrape all websites
def main():
    urls = {
        "Element Games": "https://www.elementgames.co.uk/",
        "Wayland Games": "https://www.waylandgames.co.uk/",
        "Argos": "https://www.argos.co.uk/"
    }

    for site, url in urls.items():
        print(f"Scraping {site}...")
        data = scrape_website(url, globals()[f'parse_{site.lower().replace(" ", "_")}'])
        if data:  # Ensure data was fetched before saving
            df = pd.DataFrame(data, columns=["Product Title", "Product URL", "Price", "Stock Level"])
            df.to_csv(f"{site.lower().replace(' ', '_')}_products.csv", index=False)
            print(f"Data from {site} saved successfully.")
        else:
            print(f"No data found for {site}. Please check selectors or website structure.")

if __name__ == "__main__":
    main()
