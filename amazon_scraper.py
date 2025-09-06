import matplotlib
matplotlib.use('Agg')
import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import smtplib
import time
import random
import re
from fake_useragent import UserAgent
import logging
import threading
from datetime import datetime
import json
import os
# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Function to generate a random User-Agent
def get_random_headers():
    ua = UserAgent()
    return {
        "User-Agent": ua.random,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }

# Extract Product ID from URL
def get_product_id(url):
    match = re.search(r"/dp/([A-Z0-9]+)", url)
    return match.group(1) if match else None

# Check if product is available
def is_product_available(soup):
    # Check for "Currently unavailable" message
    unavailable = soup.find("div", {"id": "availability"})
    if unavailable and "Currently unavailable" in unavailable.text:
        return False
    
    # Check for "Out of Stock" message
    out_of_stock = soup.find("span", {"class": "a-color-price"})
    if out_of_stock and "Out of Stock" in out_of_stock.text:
        return False
    
    return True

# Get Price & Product Name
def get_product_details(url, max_retries=3):
    headers = get_random_headers()
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            logger.info(f"Fetching data from URL: {url} (Attempt {retry_count + 1})")
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            if response.status_code != 200:
                logger.error(f"Error: Request failed with status code {response.status_code}")
                retry_count += 1
                time.sleep(random.uniform(5, 10))
                continue

            soup = BeautifulSoup(response.text, 'html.parser')

            # Check if product is available
            if not is_product_available(soup):
                logger.error("Product is currently unavailable or out of stock")
                return None, None, "Product is currently unavailable or out of stock"

            # Extract Product Name
            product_name = None
            try:
                product_name_element = soup.find("span", {"id": "productTitle"})
                if product_name_element:
                    product_name = product_name_element.text.strip()
                    logger.info(f"Found product name: {product_name}")
            except Exception as e:
                logger.error(f"Error extracting product name: {e}")
                # Continue without product name

            # Extract Price - Try multiple price selectors
            price = None
            price_selectors = [
                {"class": "a-price-whole"},
                {"class": "a-offscreen"},
                {"class": "a-price"},
                {"id": "priceblock_ourprice"},
                {"id": "priceblock_dealprice"},
                {"class": "a-color-price"},
                {"class": "a-text-price"}
            ]

            for selector in price_selectors:
                try:
                    price_element = soup.find("span", selector)
                    if price_element:
                        price_text = price_element.text.strip()
                        # Remove currency symbols and convert to float
                        price_text = re.sub(r'[^\d.]', '', price_text)
                        if price_text:
                            price = float(price_text)
                            logger.info(f"Found price: ${price}")
                            break
                except Exception as e:
                    logger.error(f"Error with price selector {selector}: {e}")
                    continue

            if price is None:
                logger.error("Could not find price with any selector")
                return None, None, "Could not find price"

            # If product name is not found, use product ID
            if not product_name:
                product_id = get_product_id(url)
                if product_id:
                    product_name = f"Product {product_id}"
                    logger.info(f"Using product ID as name: {product_name}")

            return product_name, price, None

        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {e}")
            retry_count += 1
            time.sleep(random.uniform(5, 10))
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            retry_count += 1
            time.sleep(random.uniform(5, 10))

    logger.error(f"Failed to fetch product details after {max_retries} attempts")
    return None, None, "Failed to fetch product details after multiple attempts"

# Save Price to CSV
def save_price_data(product_id, price):
    filename = f"price_history_{product_id}.csv"
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    df = pd.DataFrame([[timestamp, price]], columns=['Timestamp', 'Price'])

    try:
        if os.path.exists(filename):
            df_old = pd.read_csv(filename)
            df = pd.concat([df_old, df], ignore_index=True)
            logger.info(f"Updated price history for {product_id}")
        else:
            logger.info(f"Creating new price history file for {product_id}")

        df.to_csv(filename, index=False)
        logger.info(f"Price recorded for {product_id}: {price}")
    except Exception as e:
        logger.error(f"Error saving price data: {e}")

# Analyze Price Data
def analyze_prices(product_id):
    filename = f"price_history_{product_id}.csv"

    try:
        if not os.path.exists(filename):
            logger.error(f"No data available for product {product_id}")
            return None, None, None

        df = pd.read_csv(filename)
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        avg_price = df['Price'].mean()
        max_price = df['Price'].max()
        min_price = df['Price'].min()

        logger.info(f"Price analysis for {product_id}:")
        logger.info(f"Average: ${avg_price:.2f}")
        logger.info(f"Maximum: ${max_price:.2f}")
        logger.info(f"Minimum: ${min_price:.2f}")

        # Plot Price Trend
        sns.set_style("darkgrid")
        plt.figure(figsize=(10, 5))
        sns.lineplot(data=df, x='Timestamp', y='Price', marker='o')
        plt.title(f"Price Trend for {product_id}")
        plt.xlabel("Date")
        plt.ylabel("Price")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(f"static/price_trend_{product_id}.png")
        plt.close()

        return avg_price, max_price, min_price
    except Exception as e:
        logger.error(f"Error analyzing prices for {product_id}: {e}")
        return None, None, None

# Save product data to JSON
def save_product_data(product_data):
    try:
        with open('product_data.json', 'w') as f:
            json.dump(product_data, f)
        logger.info("Product data saved successfully")
    except Exception as e:
        logger.error(f"Error saving product data: {e}")

# Load product data from JSON
def load_product_data():
    try:
        if os.path.exists('product_data.json'):
            with open('product_data.json', 'r') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Error loading product data: {e}")
    return {}

# Send Email Notification
def send_email(subject, body, recipient_email, sender_email, sender_password):
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        message = f'Subject: {subject}\n\n{body}'
        server.sendmail(sender_email, recipient_email, message)
        server.quit()
        logger.info("Email sent successfully!")
    except Exception as e:
        logger.error(f"Error sending email: {e}")

# Continuous Scraping Function
def start_continuous_scraping(product_data, interval_minutes=2):
    def scrape_loop():
        while True:
            try:
                for product_id, data in product_data.items():
                    url = data['url']
                    logger.info(f"Scraping product {product_id}")
                    
                    product_name, current_price, error = get_product_details(url)
                    if error:
                        logger.error(f"Error for product {product_id}: {error}")
                        continue
                        
                    if current_price is not None:
                        save_price_data(product_id, current_price)
                        avg_price, max_price, min_price = analyze_prices(product_id)
                        
                        # Update product data
                        product_data[product_id].update({
                            'name': product_name,
                            'current_price': current_price,
                            'avg_price': avg_price,
                            'max_price': max_price,
                            'min_price': min_price,
                            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        })
                        
                        # Save updated product data
                        save_product_data(product_data)
                        
                        # Check for significant price changes
                        if current_price < data.get('min_price', float('inf')):
                            logger.info(f"Price drop detected for {product_id}")
                            # Add your notification logic here
                    
                    # Add random delay between requests to avoid rate limiting
                    time.sleep(random.uniform(5, 10))
                
                logger.info(f"Completed scraping cycle. Next cycle in {interval_minutes} minutes.")
                time.sleep(interval_minutes * 60)
                
            except Exception as e:
                logger.error(f"Error in scraping loop: {e}")
                time.sleep(60)  # Wait a minute before retrying

    # Start the scraping thread
    scraping_thread = threading.Thread(target=scrape_loop, daemon=True)
    scraping_thread.start()
    return scraping_thread

# Main Function to Check Price and Notify
def check_and_notify(url, recipient_email, sender_email, sender_password):
    product_id = get_product_id(url)
    if not product_id:
        logger.error("Invalid URL: Cannot extract Product ID")
        return None, None, None, None

    product_name, current_price, error = get_product_details(url)

    if error:
        logger.error(f"Error for product {product_id}: {error}")
        return product_name, None, None, None, None

    if current_price is not None:
        save_price_data(product_id, current_price)
        avg_price, max_price, min_price = analyze_prices(product_id)

        # Send Email if Price Drops
        if current_price == min_price:
            send_email(
                f"Price Drop Alert for {product_name}!",
                f"The product is at its lowest price: ${current_price}",
                recipient_email, sender_email, sender_password
            )

        return product_name, current_price, avg_price, max_price, min_price
    else:
        logger.error("Failed to retrieve price")
        return product_name, None, None, None, None
