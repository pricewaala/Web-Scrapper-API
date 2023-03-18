from typing import List

import requests
from bs4 import BeautifulSoup

from Model.ProductDetails import ProductList, Product


async def getFlipkartProductName(all_contents):
    name = all_contents.find('span', attrs={'class': 'B_NuCI'})
    if name is not None:
        name = name.text
    else:
        name = ""
    return name


async def getFlipkartProductDescription(all_contents):
    description = []
    description_div = all_contents.find('div', attrs={'class': '_2418kt'})
    if description_div is not None:
        description_tags = description_div.find_all('li')
        for tag in description_tags:
            description.append(tag.text.strip())
    return description


async def getFlipkartProductRating(all_contents):
    rating_star = ""
    rating_count = ""
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
    return rating_count, rating_star


async def getFlipkartProductPrice(all_contents):
    price_div = all_contents.find('div', attrs={'class': '_30jeq3 _16Jk6d'})
    if price_div is not None:
        price = price_div.text.replace('₹', '').replace(',', '').strip()
        price = float(price)
    else:
        price = 0.0
    return price


async def getFlipkartProductExchangeOffer(all_contents):
    exchange = ""
    exchange_div = all_contents.findAll('div', attrs={'class': '_17Rl6L'})
    if exchange_div is not None:
        for exchange_val in exchange_div:
            # print(exchange_val.text)
            if "up" in exchange_val.text:
                exchange = exchange_val.text.strip()
    else:
        exchange = ""
    return exchange


async def getFlipkartProductImages(all_contents):
    image = []
    image_div = all_contents.find('div', attrs={'class': '_2mLllQ'})
    if image_div is not None:
        image_tags = image_div.find_all('img')
        for tag in image_tags:
            image.append(tag.get('src'))
    return image


class FlipkartOperationalScrapper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}

    async def getFlipkartContentForPage(self, search: str) -> List[Product]:
        products = []
        links_list = await self.getFlipkartLinksOfList(search)

        products = await self.getProductDetailFlipkart(links_list, products)

        return products

    async def getProductDetailFlipkart(self, links_list, products):
        for links in links_list:
            link_page = "https://www.flipkart.com" + links
            page_content = requests.get(link_page)
            content = BeautifulSoup(page_content.content, "lxml")

            all_contents = content.find('div', attrs={'class': '_1YokD2 _2GoDe3'})
            if all_contents is not None:
                name = await getFlipkartProductName(all_contents)

                # Get the description of the product
                description = await getFlipkartProductDescription(all_contents)

                # Get the rating of the product
                rating_count, rating_star = await getFlipkartProductRating(all_contents)

                # Get the price of the product
                price = await getFlipkartProductPrice(all_contents)

                # Get the exchange offer of the product
                exchange = await getFlipkartProductExchangeOffer(all_contents)

                # Get the image of the product
                image = await getFlipkartProductImages(all_contents)

                product = Product(name=name, description=description, ratingStar=rating_star, ratingCount=rating_count,
                                  price=price, exchange=exchange, image=image, link=link_page)
                products.append(product)
        return products

    async def getFlipkartLinksOfList(self, search):
        nospaces = search.replace(" ", "+")
        link = "https://www.flipkart.com/search?q=" + nospaces
        page = requests.get(link)
        soup = BeautifulSoup(page.content, "lxml")
        links_list = []
        for data in soup.findAll('div', class_='_2kHMtA'):
            links = data.findAll('a')
            for link in links:
                links_list.append(link.get("href"))
        return links_list
