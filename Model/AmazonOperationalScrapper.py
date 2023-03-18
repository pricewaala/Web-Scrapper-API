import requests
from bs4 import BeautifulSoup

from Model.ProductDetails import ProductList, Product


async def getAmazonProductRatingStar(product_section):
    rating_star = product_section.find("span", class_="a-icon-alt")
    if rating_star is None:
        rating_star = "None"
    else:
        rating_star = rating_star.text
    return rating_star


async def getAmazonProductDescription(product_section):
    description = []
    description_ul_list = product_section.find("ul", class_="a-unordered-list a-vertical a-spacing-mini")
    if description_ul_list is not None:
        for li in description_ul_list.find_all("li"):
            description.append(li.text)
    return description


async def getAmazonProductExchangeAmount(right_product_section):
    exchange_amount = right_product_section.find("div", class_="a-section a-spacing-none a-padding-none show")
    if exchange_amount is None:
        exchange_amount = ""
    else:
        exchange_amount_span = exchange_amount.find("span", class_="a-color-price")
        if exchange_amount_span is not None:
            exchange_amount = exchange_amount_span.text.strip()
    return exchange_amount


async def getAmazonProductRatingCount(product_section):
    rating_count = product_section.find("span", id="acrCustomerReviewText")
    if rating_count is None:
        rating_count = ""
    else:
        rating_count = rating_count.text
    return rating_count


async def getAmazonProductTitleName(product_section):
    name = product_section.find("span", class_="a-size-large product-title-word-break")
    if name is None:
        name = None
    else:
        name = name.text.strip()
    return name


async def getAmazonProductPrice(product_section):
    price = product_section.find("span", class_="a-price-whole")
    if price is None:
        price = 0.0
    else:
        price = float(price.text.replace(",", ""))
    return price


class AmazonOperationalScrapper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}

    async def getAmazonContentForPage(self, links_list, page_number, search):
        links_list = await self.getAmazonListOfLinks(links_list, page_number, search)
        products = []
        await self.getProductDetailAmazon(links_list, products)
        return products

    async def getProductDetailAmazon(self, links_list, products):
        for link in links_list:
            url = f"https://www.amazon.in{link}"
            page = self.session.get(url)
            soup = BeautifulSoup(page.content, "lxml")
            all_product_section = soup.find("div", id="dp-container")
            while not all_product_section:
                page = self.session.get(url)
                soup = BeautifulSoup(page.content, "lxml")
                all_product_section = soup.find("div", id="dp-container")
            center_product_section = all_product_section.find("div", class_="centerColAlign")
            right_product_section = all_product_section.find("div", id="rightCol")
            left_product_section = all_product_section.find("div", id="leftCol")
            description = []
            images = []
            name = await getAmazonProductTitleName(center_product_section)
            price = await getAmazonProductPrice(center_product_section)
            rating_star = await getAmazonProductRatingStar(center_product_section)
            rating_count = await getAmazonProductRatingCount(center_product_section)
            description = await getAmazonProductDescription(center_product_section)
            exchange_offer = await getAmazonProductExchangeAmount(right_product_section)
            image = left_product_section.find("ul",
                                              class_="a-unordered-list a-nostyle a-button-list a-vertical a-spacing-top-extra-large regularAltImageViewLayout")
            if image is not None:
                for li in image.findAll("span", class_="a-button-inner"):
                    for n in li.find_all('img'):
                        if n.get('src') is not None:
                            images.append(n.get('src'))

            product = Product(name=name, description=description, ratingStar=rating_star, ratingCount=rating_count,
                              price=price, exchange=exchange_offer, image=images, link=link)
            products.append(product)

    async def getAmazonListOfLinks(self, links_list, page_number, search):
        while not links_list:
            search_query = search.replace(" ", "+")
            url = f"https://www.amazon.in/s?k={search_query}&page={page_number}"
            page = self.session.get(url)
            soup = BeautifulSoup(page.content, "lxml")
            links = soup.find_all("a", class_="a-link-normal s-no-outline")
            links_list = [link.get("href") for link in links]
        return links_list
