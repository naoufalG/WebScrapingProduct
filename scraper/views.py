import requests
from bs4 import BeautifulSoup
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from scraper.models import Product


# Create your views here.


def home(request):
    if request.method == 'POST':
        if request.POST['selectorSite'] == 'ebay':
            item_title = []
            item_price = []
            item_link = []
            item_shipping = []
            item_shipping_calc = []
            item_condition = []
            total_price = []

            cher = request.POST['cher']
            if request.POST['selector'] == 'low':
                refresh = True
                url = 'https://www.ebay.com/sch/' + cher + '?_sop=15'
            elif request.POST['selector'] == 'high':
                refresh = True
                url = 'https://www.ebay.com/sch/' + cher + '?_sop=16'
            else:
                refresh = True
                url = 'https://www.ebay.com/sch/' + cher
            page = requests.get(url)
            soup = BeautifulSoup(page.content, 'html.parser')

            listings_title = soup.find_all('h3', class_='s-item__title')
            listings_link = soup.find_all('a', class_='s-item__link')
            listings_price = soup.find_all('span', class_='s-item__price')
            listings_shipping = soup.find_all('span', class_='s-item__shipping s-item__logisticsCost')
            listings_condition = soup.find_all('span', class_='SECONDARY_INFO')

            for listing in listings_title:
                text_only = listing.text
                no_newListing = text_only.replace('New Listing', '').replace('Ã—', '×')
                item_title.append(no_newListing)

            for listing in listings_price:
                text_only = listing.text
                no_dash = text_only.replace(' to ', '-')
                item_price.append(no_dash)

            for listing in listings_link:
                item_link.append(listing['href'])

            for listing in listings_shipping:
                text_only = listing.text
                no_plus = text_only.replace('+', '').replace('Shipping', '').replace('shipping', '')
                no_symbols = text_only.replace('+', '').replace('Shipping', '').replace('shipping', ''). \
                    replace('Free', '0').replace('International', '').replace(' ', '')
                item_shipping.append(no_plus)
                item_shipping_calc.append(no_symbols)

            for listing in listings_condition:
                text_only = listing.text
                item_condition.append(text_only)

            for i1, i2 in zip(item_price, item_shipping_calc):
                i1, i2 = i1.replace('$', ' '), i2.replace('$', ' ')
                i1 = i1.replace(',', '')
                items = i1.split('-')
                added_items = [str(round(float(item), 2)) for item in items]
                total_price.append('-'.join(added_items))

            total_price = ['$' + s for s in total_price]

            master_list = zip(item_title, item_condition, item_price, item_shipping, total_price, item_link)
            a:[]
            super_list = [a for a in master_list]

            context = {
                'items': super_list,
                'ref': refresh
            }
            return render(request, 'home.html', context)

        if request.POST['selectorSite'] == 'ali':
            refe = 'ali'
            PATH = "E:\chromedriver.exe"
            options = Options()
            options.add_argument("--headless")
            driver = webdriver.Chrome(PATH, options=options)
            driver.get("https://www.aliexpress.com/")
            search = driver.find_element_by_name("SearchText")
            s = request.POST['cher']
            search.send_keys(s)
            search.send_keys(Keys.RETURN)
            try:
                main = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "right-menu"))
                )

                articles = main.find_elements_by_class_name("list-item")

                list = []
                for article in articles:
                    prix = article.find_elements_by_class_name("price-current")
                    for p in prix:
                        p1 = (p.text).replace('US $', '')
                    nom = article.find_elements_by_class_name("item-title")
                    for n in nom:
                        n1 = n.text
                    l = []
                    for a in driver.find_elements_by_class_name('item-title'):
                        link = a.get_attribute('href')
                        l.append(link)
                    list.append(Product(n1, float(p1), l))
                list = sorted(list, key=lambda Product: Product.prix)


            finally:
                driver.quit()
            return render(request, "home.html", locals())

    return render(request, 'home.html')


