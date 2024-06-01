import os
import time

import chromedriver_autoinstaller
from bs4 import BeautifulSoup
from flask import Flask
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

chromedriver_autoinstaller.install()

app = Flask(__name__)


@app.route("/")
def home():
    return "Home"

@app.route("/scrape")
def scrapeWebPage():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"),options=chrome_options)
    
    
    url = "https://www.harrisfarm.com.au/collections/online-grocery-shopping-australia"
    driver.get(url)
    time.sleep(10)
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    product_tiles = soup.find_all('li',class_='ais-Hits-item')
    
    products = []
    for product_tile in product_tiles:
        # Extract data from html content
        product_name = product_tile.find('p', class_='title').text.strip()
        total_price = product_tile.find('span', class_= "from_price").text.strip()
        unit = product_tile.find('span',class_="unit_price").find('small').text.strip()
        unit_price = product_tile.find('span', class_='compare_at_price unit_price').find('small').text.strip()
        
        # create data json and append to products list
        data = {}
        data['name']=product_name
        data['price']=total_price
        data['unit']= unit
        data['unit_price']=unit_price
        products.append(data)
    driver.quit()
    return products

@app.route("/scraping")
def scrapeData():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"),options=chrome_options)
    url = "https://www.harrisfarm.com.au/collections/online-grocery-shopping-australia"
    driver.get(url)
    time.sleep(10)
    return driver.page_source
    # soup = BeautifulSoup(driver.page_source, 'html.parser')
    # product_tiles = soup.find_all('li',class_='ais-Hits-item')
    # products = []
    # for product_tile in product_tiles:
    #     product_name = product_tile.find('p', class_='title').text.strip()
    #     total_price = product_tile.find('span', class_= "from_price").text.strip()
    #     unit_price = product_tile.find('span', class_='compare_at_price unit_price').find('small').text.strip()
    #     products.append((product_name,total_price,unit_price))
    # return driver.page_source
    
if __name__ == "__main__":
    app.run(debug=True)
