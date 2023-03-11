import asyncio
from time import time
from typing import List

import redis as redis
import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from Model.AmazonOperationalScrapper import AmazonOperationalScrapper

from Service.NotToDelete import get_title, get_price_Amazon

redis_client = redis.Redis(
    host='redis-12457.c93.us-east-1-3.ec2.cloud.redislabs.com',
    port=12457,
    password='LzwBDIEMPTPC3WSf29nOuER5itpalbsJ')

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Product(BaseModel):
    name: str = Field(...)
    description: List[str] = Field([])
    ratingStar: str = Field(...)
    ratingCount: str = Field(...)
    price: float = Field(...)
    exchange: str = Field(...)
    image: List[str] = Field([])
    link: str = Field(...)


class ProductList(BaseModel):
    status: int = Field(...)
    products: List[Product] = Field(...)
    served_through_cache: bool = Field(...)


@app.get("/amazon/v2/{search}", response_model=ProductList)
async def search_amazon_products(search: str):
    try:
        search_query_cache = search.replace(" ", "")
        # Check if search query is in Redis cache
        cached_products = redis_client.get("amazon_product_" + search_query_cache)
        if cached_products is not None:
            # Return cached data to the client
            print("In Cache")
            asyncio.create_task(_update_cache_and_return_products(search_query_cache, search, True))
            return {"status": 200, "products": eval(cached_products.decode()), "served_through_cache": True}

        # Run the rest of the code in the background
        products = await _update_cache_and_return_products(search_query_cache, search, False)

        # Return the product list to the client
        return {"status": 200, "products": products, "served_through_cache": False}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def _update_cache_and_return_products(search_query_cache: str, search: str, isUpdated: bool):
    try:
        links_list = []
        scrapper = AmazonOperationalScrapper()

        products_page_1 = await scrapper.getAmazonContentForPage(links_list, "1", search)
        products_page_2 = await scrapper.getAmazonContentForPage(links_list, "2", search)

        products = products_page_1 + products_page_2

        print(len(products))
        # Store products in Redis cache
        redis_client.set("amazon_product_" + search_query_cache, str(products))
        if isUpdated:
            print("Updated Cache" + search_query_cache)
        else:
            print("Added New Cache" + search_query_cache)

        # Return the product list to the client
        return products
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/amazon/{search}")
async def root_Amazon(search: str):
    # Headers for request
    HEADERS = ({'User-Agent':
                    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
                'Accept-Language': 'en-US'})

    nospaces = search.replace(" ", "+")
    # The webpage URL
    URL = "https://www.amazon.in/s?k=" + nospaces

    # HTTP Request
    webpage = requests.get(URL, headers=HEADERS)

    # Soup Object containing all data
    soup = BeautifulSoup(webpage.content, "lxml")

    # Fetch links as List of Tag Objects
    links = soup.find_all("a", attrs={'class': 'a-link-normal s-no-outline'})

    # Store the links
    links_list = []

    # Loop for extracting links from Tag Objects
    for link in links:
        links_list.append(link.get('href'))

    arr = []
    i = 0
    # Loop for extracting product details from each link
    for link in links_list:
        start = int(time() * 1000)

        new_webpage = requests.get("https://www.amazon.in" + link, headers=HEADERS)

        new_soup = BeautifulSoup(new_webpage.content, "lxml")

        # Function calls to display all necessary product information
        # print("Product Title =", get_title(new_soup))
        # print("Product Price =", get_price(new_soup))
        # print("Product Rating =", get_rating(new_soup))
        # print("Number of Product Reviews =", get_review_count(new_soup))
        # print("Availability =", get_availability(new_soup))
        # print(link)
        # print()
        arr.append(get_title(new_soup) + ", " + get_price_Amazon(new_soup) + " , " + link)
        end = int(time() * 1000)
        print(end - start)

    print(len(arr))
    return arr


@app.get("/flipkart/{search}")
async def root_Flipkart(search: str):
    nospaces = search.replace(" ", "+")
    link = "https://www.flipkart.com/search?q=" + nospaces
    page = requests.get(link)
    soup = BeautifulSoup(page.content, "lxml")
    # it gives us the visual representation of data
    # name = soup.find('div', class_="_4rR01T")
    # print(name)
    # rating = soup.find('div', class_="_3LWZlK")
    # print(rating)
    # specification = soup.find('div', class_="fMghEO")
    # print(specification)
    # price = soup.find('div', class_='_30jeq3 _1_WHN1')
    # print(price)

    products = []  # List to store the name of the product
    prices = []  # List to store price of the product
    ratings = []  # List to store rating of the product
    apps = []  # List to store supported apps
    os = []  # List to store operating system
    hd = []  # List to store resolution
    sound = []

    for data in soup.findAll('div', class_='_3pLy-c row'):
        names = data.find('div', attrs={'class': '_4rR01T'})
        price = data.find('div', attrs={'class': '_30jeq3 _1_WHN1'})
        # rating = data.find('div', attrs={'class': '_3LWZlK'})
        # specification = data.find('div', attrs={'class': 'fMghEO'})
        products.append(names.text)  # Add product name to list
        prices.append(price.text)  # Add price to list
        # apps.append(app)  # Add supported apps specifications to list
        # ratings.append(rating.text)  # Add rating specifications to list

    print(products)
    # print(len(ratings))
    print(prices)


@app.get("/flipkart/v2/{search}")
async def root_Flipkart(search: str):
    global rating_count
    products = []
    nospaces = search.replace(" ", "+")
    link = "https://www.flipkart.com/search?q=" + nospaces
    page = requests.get(link)
    soup = BeautifulSoup(page.content, "lxml")
    links_list = []
    for data in soup.findAll('div', class_='_2kHMtA'):
        links = data.findAll('a')
        for link in links:
            links_list.append(link.get("href"))

    for links in links_list:
        link_page = "https://www.flipkart.com" + links
        page_content = requests.get(link_page)
        content = BeautifulSoup(page_content.content, "lxml")

        all_contents = content.find('div', attrs={'class': '_1YokD2 _2GoDe3'})
        if all_contents is not None:
            name = all_contents.find('span', attrs={'class': 'B_NuCI'})
            if name is not None:
                name = name.text
            else:
                name = ""

            # Get the description of the product
            description = []
            description_div = all_contents.find('div', attrs={'class': '_2418kt'})
            if description_div is not None:
                description_tags = description_div.find_all('li')
                for tag in description_tags:
                    description.append(tag.text.strip())

            # Get the rating of the product
            rating_star = ""
            rating_div = all_contents.find('div', attrs={'class': '_3LWZlK'})
            if rating_div is not None:
                if rating_star is not None:
                    rating_star = rating_div.text
                else:
                    rating_star = ""

                rating_count_span = all_contents.find('span', attrs={'class': '_2_R_DZ'})
                if rating_count_span is not None:
                    rating_count_all_span = rating_count_span.findAll('span')
                    if rating_count_all_span is not None:
                        for rating_val in rating_count_all_span:
                            if "Ratings" in rating_val.text:
                                rating_count = rating_val.text
                else:
                    rating_count = ""

            # Get the price of the product
            price_div = all_contents.find('div', attrs={'class': '_30jeq3 _16Jk6d'})
            if price_div is not None:
                price = price_div.text.replace('₹', '').replace(',', '').strip()
                price = float(price)
            else:
                price = 0.0

            # Get the exchange offer of the product
            exchange = ""
            exchange_div = all_contents.findAll('div', attrs={'class': '_17Rl6L'})
            if exchange_div is not None:
                for exchange_val in exchange_div:
                    # print(exchange_val.text)
                    if "up" in exchange_val.text:
                        exchange = exchange_val.text.strip()
            else:
                exchange = ""

            # Get the image of the product
            image = []
            image_div = content.find('div', attrs={'class': '_2mLllQ'})
            if image_div is not None:
                image_tags = image_div.find_all('img')
                for tag in image_tags:
                    image.append(tag.get('src'))

            product = Product(name=name, description=description, ratingStar=rating_star, ratingCount=rating_count,
                              price=price, exchange=exchange, image=image, link=link_page)
            products.append(product)

    product_list = ProductList(status=200, products=products, served_through_cache=False)
    return product_list


@app.get("/reliance/{search}")
async def root_Reliance(search: str):
    nospaces = search.replace(" ", "+")
    # The webpage URL
    URL = "https://www.reliancedigital.in/search?q=" + nospaces + ":relevance"

    # HTTP Request
    webpage = requests.get(URL)

    # Soup Object containing all data
    soup = BeautifulSoup(webpage.content, 'html.parser')

    s = soup.findAll('div', class_='sp grid')
    a = len(s)
    for i in range(a):
        for link in s[i].findAll('a'):
            ab = link.get('href')
            print(ab)
            new_webpage = requests.get("https://www.reliancedigital.in" + ab)
            new_soup = BeautifulSoup(new_webpage.content, "lxml")
            s1 = new_soup.find('span', class_='pdp__offerPrice')
            print(s1.text)


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


@app.get("/")
async def read_root():
    return "Welcome to PriceWalla"
