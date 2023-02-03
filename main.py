from time import time

import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI

from Service.WebScrapperService import get_title, get_price, get_rating, get_review_count, get_availability

app = FastAPI()


@app.get("/")
async def root():
    # Headers for request
    HEADERS = ({'User-Agent':
                    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
                'Accept-Language': 'en-US'})

    # The webpage URL
    URL = "https://www.amazon.in/s?k=oneplus+11+pro"

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
        arr.append(get_title(new_soup) + ", " + get_price(new_soup) + " , " + link)
        end = int(time() * 1000)
        print(end-start)

    print(len(arr))
    return arr


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
