import requests
from bs4 import BeautifulSoup


# Function to extract Product Title
def get_title(soup):
    try:
        # Outer Tag Object
        title = soup.find("span", attrs={"id": 'productTitle'})

        # Inner NavigatableString Object
        title_value = title.string

        # Title as a string value
        title_string = title_value.strip()

    # # Printing types of values for efficient understanding
    # print(type(title))
    # print(type(title_value))
    # print(type(title_string))
    # print()

    except AttributeError:
        title_string = ""

    return title_string


# Function to extract Product Price
def get_price_FlipKart(soup):
    try:
        price = soup.find("div", attrs={
            'class': '30jeq3 _1_WHN1'}).string.strip()

    except AttributeError:

        try:
            # If there is some deal price
            price = soup.find("div", attrs={
                'class': '30jeq3 _1_WHN1'}).string.strip()

        except:
            price = ""

    return price

def get_price_Amazon(soup):
    try:
        price = soup.find("span", attrs={
            'class': 'a-offscreen'}).string.strip()

    except AttributeError:

        try:
            # If there is some deal price
            price = soup.find("span", attrs={
                'class': 'a-offscreen'}).string.strip()

        except:
            price = ""

    return price


# Function to extract Product Rating
def get_rating(soup):
    try:
        rating = soup.find("i", attrs={'class': 'a-icon a-icon-star a-star-4-5'}).string.strip()

    except AttributeError:

        try:
            rating = soup.find("span", attrs={'class': 'a-icon-alt'}).string.strip()
        except:
            rating = ""

    return rating


# Function to extract Number of User Reviews
def get_review_count(soup):
    try:
        review_count = soup.find("span", attrs={'id': 'acrCustomerReviewText'}).string.strip()

    except AttributeError:
        review_count = ""

    return review_count


# Function to extract Availability Status
def get_availability(soup):
    try:
        available = soup.find("div", attrs={'id': 'availability'})
        available = available.find("span").string.strip()

    except AttributeError:
        available = "Not Available"

    return available


# if __name__ == '__main__':

    # Headers for request
    # HEADERS = ({'User-Agent':
    #                 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
    #             'Accept-Language': 'en-US'})
    #
    # # The webpage URL
    # URL = "https://www.amazon.in/s?k=oneplus+11+pro"
    #
    # # HTTP Request
    # webpage = requests.get(URL, headers=HEADERS)
    #
    # # Soup Object containing all data
    # soup = BeautifulSoup(webpage.content, "lxml")
    #
    # # Fetch links as List of Tag Objects
    # links = soup.find_all("a", attrs={'class': 'a-link-normal s-no-outline'})
    #
    # # Store the links
    # links_list = []
    #
    # # Loop for extracting links from Tag Objects
    # for link in links:
    #     links_list.append(link.get('href'))
    #
    # # Loop for extracting product details from each link
    # for link in links_list:
    #     new_webpage = requests.get("https://www.amazon.in" + link, headers=HEADERS)
    #
    #     new_soup = BeautifulSoup(new_webpage.content, "lxml")
    #
    #     # Function calls to display all necessary product information
    #     print("Product Title =", get_title(new_soup))
    #     print("Product Price =", get_price(new_soup))
    #     print("Product Rating =", get_rating(new_soup))
    #     print("Number of Product Reviews =", get_review_count(new_soup))
    #     print("Availability =", get_availability(new_soup))
    #     print(link)
    #     print()


#---------Amazon-Base-Logic---------//


# async def getAmazonContentForPage(links_list, page_number, search):
#     # Collect all product links on Amazon search results page for page 1
#     links_list = await getAmazonListOfLinks(links_list, page_number, search)
#     # Extract product details from each link
#     products = []
#     await getProductDetailAmazon(links_list, products)
#     return products
#
#
# async def getProductDetailAmazon(links_list, products):
#     for link in links_list:
#         url = f"https://www.amazon.in{link}"
#         page = requests.get(url)
#         soup = BeautifulSoup(page.content, "lxml")
#         all_product_section = soup.find("div", id="dp-container")
#         while not all_product_section:
#             page = requests.get(url)
#             soup = BeautifulSoup(page.content, "lxml")
#             all_product_section = soup.find("div", id="dp-container")
#         center_product_section = all_product_section.find("div", class_="centerColAlign")
#         right_product_section = all_product_section.find("div", id="rightCol")
#         left_product_section = all_product_section.find("div", id="leftCol")
#         description = []
#         images = []
#         name = await getAmazonProductTitleName(center_product_section)
#         price = await getAmazonProductPrice(center_product_section)
#         rating_star = await getAmazonProductRatingStar(center_product_section)
#         rating_count = await getAmazonProductRatingCount(center_product_section)
#         description = await getAmazonProductDescription(description, center_product_section)
#         exchange_offer = await getAmazonProductExchangeAmount(right_product_section)
#         image = left_product_section.find("ul",
#                                           class_="a-unordered-list a-nostyle a-button-list a-vertical a-spacing-top-extra-large regularAltImageViewLayout")
#         if image is not None:
#             for li in image.findAll("span", class_="a-button-inner"):
#                 for n in li.find_all('img'):
#                     if n.get('src') is not None:
#                         images.append(n.get('src'))
#                         print(n.get('src'))
#
#         # print(image)
#         product = Product(name=name, description=description, ratingStar=rating_star, ratingCount=rating_count,
#                           price=price, exchange=exchange_offer, image=images, link=link)
#         products.append(product)
#
#
# async def getAmazonListOfLinks(links_list, page_number, search):
#     while not links_list:
#         search_query = search.replace(" ", "+")
#         url = f"https://www.amazon.in/s?k={search_query}&page={page_number}"
#         page = requests.get(url)
#         soup = BeautifulSoup(page.content, "lxml")
#         links = soup.find_all("a", class_="a-link-normal s-no-outline")
#         links_list = [link.get("href") for link in links]
#         print(len(links_list))
#     return links_list
#
#
# async def getAmazonProductExchangeAmount(right_product_section):
#     exchange_amount = right_product_section.find("div", class_="a-section a-spacing-none a-padding-none show")
#     if exchange_amount is None:
#         exchange_amount = ""
#     else:
#         exchange_amount_span = exchange_amount.find("span", class_="a-color-price")
#         if exchange_amount_span is not None:
#             exchange_amount = exchange_amount_span.text.strip()
#     return exchange_amount
#
#
# async def getAmazonProductRatingCount(product_section):
#     rating_count = product_section.find("span", id="acrCustomerReviewText")
#     if rating_count is None:
#         rating_count = ""
#     else:
#         rating_count = rating_count.text
#     return rating_count
#
#
# async def getAmazonProductTitleName(product_section):
#     name = product_section.find("span", class_="a-size-large product-title-word-break")
#     if name is None:
#         name = None
#     else:
#         name = name.text.strip()
#     return name
#
#
# async def getAmazonProductPrice(product_section):
#     price = product_section.find("span", class_="a-price-whole")
#     if price is None:
#         price = 0.0
#     else:
#         price = float(price.text.replace(",", ""))
#     return price
#
#
# async def getAmazonProductRatingStar(product_section):
#     rating_star = product_section.find("span", class_="a-icon-alt")
#     if rating_star is None:
#         rating_star = None
#     else:
#         rating_star = rating_star.text
#     return rating_star
#
#
# async def getAmazonProductDescription(description, product_section):
#     description_ul_list = product_section.find("ul", class_="a-unordered-list a-vertical a-spacing-mini")
#     if description_ul_list is None:
#         description = []
#     else:
#         for li in description_ul_list.find_all("li"):
#             description.append(li.text)
#     return description
