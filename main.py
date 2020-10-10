import argparse
import re

from prettytable import PrettyTable
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def get_tesco_searches():
    search_online_shop(
        shop_name='TESCO',
        url=f'https://www.tesco.com/groceries/en-GB/search?query={SEARCH_TERM}',
        not_found_css_selector='.empty-section',
        items_list_selector='.product-list > li',
        price_css_selector='.price-control-wrapper',
        title_css_selector='a[data-auto="product-tile--title"]'
    )


def get_morrisons_searches():
    search_online_shop(
        shop_name='MORRISONS',
        url=f'https://groceries.morrisons.com/search?entry={SEARCH_TERM}',
        not_found_css_selector='p[class$=noResultsFoundMessage], div[class$=resourceNotFound]',
        items_list_selector='.fops-shelf > li',
        price_css_selector='.fop-price',
        title_css_selector='.fop-description'
    )


def get_waitrose_searches():
    search_online_shop(
        shop_name='WAITROSE',
        url=f'https://www.waitrose.com/ecom/shop/search?&searchTerm={SEARCH_TERM}',
        not_found_css_selector='[class^=alternativeSearch]',
        items_list_selector='.container-fluid > .row > article',
        price_css_selector='span[data-test=product-pod-price]',
        title_css_selector='header',
        accept_cookies_css_selector='button[data-test=accept-all]'
    )


def get_aldi_searches():
    search_online_shop(
        shop_name='ALDI',
        url=f'https://www.aldi.co.uk/search?text={SEARCH_TERM}',
        not_found_css_selector='p[class$=no-results]',
        items_list_selector='#products-tab .hover-item',
        price_css_selector='.category-item__price',
        price_split=True,
        title_css_selector='.category-item__title'
    )


def get_sainsburys_searches():
    search_online_shop(
        shop_name='SAINSBURYS',
        url=f'https://www.sainsburys.co.uk/gol-ui/SearchDisplayView?filters[keyword]={SEARCH_TERM}',
        not_found_css_selector='div[class$=no-results]',
        items_list_selector='.ln-o-section:not(.header-fixed-subheading) li.pt-grid-item',
        price_css_selector='[data-test-id=pt-retail-price]',
        title_css_selector='[data-test-id=product-tile-description]',
        wait_condition=EC.presence_of_element_located((By.CSS_SELECTOR, "[data-test-id=search-results-title]"))
    )


def get_asda_searches():
    search_online_shop(
        shop_name='ASDA',
        url=f'https://groceries.asda.com/search/{SEARCH_TERM}',
        not_found_css_selector='.no-result',
        items_list_selector='#main-content > main > div.search-page-content > div:nth-child(4) > div > div.co-product-list > ul li.co-item',
        price_css_selector='.co-product__price',
        name_css_selector='[data-auto-id=linkProductTitle]',
        weight_css_selector='.co-product__volume',
        wait_condition=EC.text_to_be_present_in_element((By.CSS_SELECTOR, "[class^=search-content-header]"),
                                                        'search results')
    )


def search_online_shop(shop_name: str, url: str, not_found_css_selector: str, items_list_selector: str,
                       price_css_selector: str, price_split: bool = False, name_css_selector: str = None,
                       weight_css_selector: str = None, title_css_selector: str = None, wait_condition: any = None,
                       accept_cookies_css_selector: str = None):
    print(f'\n{shop_name}')

    try:
        driver.get(url)
        # Some shops fetch results after the page has loaded - wait for a certain condition to pass, otherwise timeout and move on.
        if wait_condition is not None:
            WebDriverWait(driver, 10).until(wait_condition)

        # Some shops ask you to accept cookies before continuing
        if accept_cookies_css_selector is not None:
            try:
                driver.find_element_by_css_selector(accept_cookies_css_selector).click()
            except NoSuchElementException:
                pass

        # Look for something on the page that indicates that no results are found.
        # If len(condition) is 0, the "no results found" text is not present and you can assume there are results on the page.
        if len(driver.find_elements_by_css_selector(not_found_css_selector)) == 0:
            # Create a PrettyTable
            t = PrettyTable(['Item', 'Price'])
            # Iterate over items
            for i, elem in enumerate(driver.find_elements_by_css_selector(items_list_selector)):
                # In case lots of items are returned, you probably only need the first few
                if i == MAX_LENGTH:
                    break

                title = ''
                # Title should be in the format `Name Quantity`
                # Some shops combine them together (use title_css_selector), others have them separate (use name_css_selector and weight_css_selector)
                if title_css_selector is not None:
                    title = elem.find_element_by_css_selector(title_css_selector).text.replace('\n', ' ').strip()
                if name_css_selector is not None and weight_css_selector is not None:
                    name = elem.find_element_by_css_selector(name_css_selector).text.replace('\n', ' ').strip()
                    weight = elem.find_element_by_css_selector(weight_css_selector).text.replace('\n', ' ').strip()
                    title = f'{name} {weight}'
                price = elem.find_element_by_css_selector(price_css_selector).text.replace('\n', ' ').strip()

                # In case the price isn't the only text in the element returned by the price_css_selector
                if price_split:
                    price = price.split(' ')[0]
                t.add_row([title, price])
            print(t.get_string(sortby='Price', sort_key=lambda row: format_price(row[0])))
        else:
            print(f'No results found for {SEARCH_TERM}')
    except (NoSuchElementException, TimeoutException):
        print(f'Error finding product: {SEARCH_TERM}')
    except WebDriverException as e:
        print(e)


def format_price(price: str) -> float:
    pound_pattern = '[0-9]+(\\.[0-9]{2}|$)'  # matches pounds, e.g. £2 or £2.99
    penny_pattern = '[0-9]+'  # matches pennies, e.g. 65 (to be turned into 0.65 later)
    pound_match = re.search(pound_pattern, price)
    penny_match = re.search(penny_pattern, price)
    if pound_match is not None:
        span = pound_match.span()
        return float(price[span[0]:span[1]])
    if penny_match is not None:
        span = penny_match.span()
        return float(f'0.{price[span[0]:span[1]]}')
    return 0  # Default - if the price doesn't match either regex, return the price unordered


if __name__ == '__main__':
    # Set up query arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('item', help='The name of the item to search for', type=str)
    parser.add_argument('--number-of-items', '-n', help='The maximum number of items to return', type=int, default=10)
    args = parser.parse_args()

    SEARCH_TERM = args.item
    MAX_LENGTH = args.number_of_items

    # Set up headless browser/driver (and set user-agent to pretend to not be headless)
    options = Options()
    options.add_argument('--headless')
    options.add_argument(
        'user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36')
    driver = webdriver.Chrome(options=options)

    # Search shops
    get_tesco_searches()
    get_morrisons_searches()
    get_waitrose_searches()
    get_aldi_searches()
    get_sainsburys_searches()
    get_asda_searches()

    # Close driver
    driver.close()
