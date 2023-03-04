from time import time

import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from Service.WebScrapperService import get_title, get_price_Amazon, get_price_FlipKart

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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


@app.get("/amazon/v2/{search}")
async def root_AmazonV2(search: str):
    products = []  # List to store the name of the product
    prices = []  # List to store price of the product
    ratings = []  # List to store rating of the product
    apps = []  # List to store supported apps
    os = []  # List to store operating system
    hd = []  # List to store resolution
    sound = []
    links_list = []

    while len(links_list) == 0:
        nospaces = search.replace(" ", "+")
        link = "https://www.amazon.in/s?k=" + nospaces
        page = requests.get(link)
        soup = BeautifulSoup(page.content, "lxml")
        s = soup.findAll('a', {'class': 'a-link-normal s-no-outline'})
        # Loop for extracting links from Tag Objects
        for link in s:
            links_list.append(link.get('href'))

        print(len(links_list))

    for i1 in links_list:
        new_webpage = requests.get("https://www.amazon.in" + i1)
        new_soup = BeautifulSoup(new_webpage.content, "lxml")
        s1 = new_soup.find('span', class_='a-price-whole')
        while s1 is None:
            new_webpage = requests.get("https://www.amazon.in" + i1)
            new_soup = BeautifulSoup(new_webpage.content, "lxml")
            s1 = new_soup.find('span', class_='a-price-whole')
            print(i1, s1)
        print(s1.text)
    return links_list


# a = len(s)
# print(a)
# for i in range(a):
#     # print(s[i])
#     ab = s[i].get('href')
#     print(ab)
# new_webpage = requests.get("https://www.reliancedigital.in" + ab)
# new_soup = BeautifulSoup(new_webpage.content, "lxml")
# s1 = new_soup.find('span', class_='pdp__offerPrice')
# print(s1.text)

# print(products)
# print(len(ratings))
# print(prices)


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
