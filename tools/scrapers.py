from __future__ import absolute_import
from .deals import FlashSale, FlashSaleMultiItem

import requests
import datetime
from requests_html import HTMLSession
import re
from bs4 import BeautifulSoup

class Scraper:
    def scrap(self):
        raise NotImplementedError

    def _parse_end_time_from_html(self, html):
        raise NotImplementedError

    def _parse_prices_from_html(self, html):
        raise NotImplementedError

    def _parse_quantities_from_html(self, html):
        raise NotImplementedError

class MoreleScraper(Scraper):

    def scrap(self):
        url = "https://www.morele.net/"
        try:
            response = requests.get(url)
            response.raise_for_status()
            content = BeautifulSoup(response.content, "html5lib")
            sale = content.find("div", attrs={"class": "home-sections-promotion"})
            if sale is not None:
                sale_name = sale.find("h4", attrs={"class": "prom-box-title"}).text.replace('\n','')
                item_name = sale.find("div", attrs={"class": "promo-box-name"}).text.replace('\n','')
                old_price, new_price = self._parse_prices_from_html(sale)
                sold, remaining = self._parse_quantities_from_html(sale)
                if remaining == "0":
                    sold, remaining = "ALL", "OUT OF STOCK"
                remaining_time = self._parse_end_time_from_html(sale)
                sale = FlashSale(url[8:22], sale_name, item_name, old_price, new_price, sold, remaining, remaining_time)
                print(sale)
            else:
                print("No flash sale found on {}".format(url))
        except requests.exceptions.RequestException as e:
            print(e)


    def _parse_end_time_from_html(self, html):
        current_time = datetime.datetime.now().replace(microsecond=0)
        end_time = html.find("div", attrs={"class": "promo-box-countdown"})["data-date-to"].replace('\n','')
        end_time = datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
        return end_time - current_time

    def _parse_prices_from_html(self, html):
        old = html.find("div", attrs={"class": "promo-box-old-price"}).text.replace('\n','')
        new = html.find("div", attrs={"class": "promo-box-new-price"}).text.replace('\n','')
        old, new = [o for o in old.split() if o.isdigit()], [n for n in new.split() if n.isdigit()]
        old, new = " ".join(old), " ".join(new)
        return old, new

    def _parse_quantities_from_html(self, html):
        sold = html.find("div", attrs={"class": "status-box-expired"}).text.replace('\n','')
        remaining = html.find("div", attrs={"class": "status-box-was"}).text.replace('\n','')
        sold, remaining = sold.split()[1], remaining.split()[1]
        if remaining == "0":
            sold, remaining = "ALL", "OUT OF STOCK"
        return sold, remaining

class XKomScraper(Scraper):

    def scrap(self):
        url = "https://www.x-kom.pl/"
        try:
            response = requests.get(url)
            response.raise_for_status()
            content = BeautifulSoup(response.content, "html5lib")
            sale = content.find("div", attrs={"class": "col-md-4 col-sm-12"})
            if sale is not None:
                sale_name = sale.find("header", attrs={"class": "text-left col-xs-12 col-md-12 col-lg-7"}).text.replace('\n','').split()
                sale_name = " ".join(word for word in sale_name)
                item_name = sale.find("p", attrs={"class": "product-name"}).text.replace('\n','')
                old_price, new_price = self._parse_prices_from_html(sale)
                sold, remaining = self._parse_quantities_from_html(sale)
                remaining_time = self._parse_end_time_from_html(sale)
                sale = FlashSale(url[8:20], sale_name, item_name, old_price, new_price, sold, remaining, remaining_time)
                print(sale)
            else:
                print("No flash sale found on {}".format(url))
        except requests.exceptions.RequestException as e:
            print(e)

    def _parse_end_time_from_html(self, html):
        script = html.findAll("script")[0]
        end_time = self._select_time_object_from_script_body(script)
        current_time = datetime.datetime.now().replace(microsecond=0)
        end_time = end_time - current_time
        return end_time

    def _parse_prices_from_html(self, html):
        old = html.find("div", attrs={"class": "old-price"}).text.replace('\n','')
        new = html.find("div", attrs={"class": "new-price"}).text.replace('\n','')
        old, new = old.split()[0], new.split()[0]
        return old, new

    def _parse_quantities_from_html(self, html):
        try:
            sold = html.find("div", attrs={"class": "pull-right"}).text.replace('\n','')
            remaining = html.find("div", attrs={"class": "pull-left"}).text.replace('\n','')
            sold, remaining = sold.split()[1], remaining.split()[1]
        except AttributeError as e:
            sold, remaining = "ALL", "OUT OF STOCK"
        return sold, remaining

    def _select_time_object_from_script_body(self, script):
        time = re.findall(r"\bDate\(.+?\)", script.text)[0]
        time = time[5:len(time) - 1]
        time = [number for number in time.split(',') if number.isdigit()]
        # In js Date implementation months' indices start from 0, so we have to add 1 to obtain actual month number.
        time[1] = str(int(time[1]) + 1)
        time = "{}-{}-{} {}:{}:{}".format(*time)
        time = datetime.datetime.strptime(time, "%Y-%m-%d %H:%M:%S")
        return time

class EuroScraper(Scraper):
 
    def scrap(self):
        url = "https://www.euro.com.pl/"
        try:
            session = HTMLSession()
            response = session.get(url)
            response.html.render()
            content = BeautifulSoup(response.html.html, "html5lib")
            sale = content.find("div", attrs={"class": "promo-products hotDeals"})
            if sale is not None:
                sale_name = sale.find("div", attrs={"class": "category-name"}).text.split()[0]
                tmp_products = sale.findAll("div", attrs={"product-info"})
                products = []
                parsed_products = set()
                for p in tmp_products:
                    item_name = p.find("h3", attrs={"class": "product-name"}).text
                    if item_name not in parsed_products:
                        product = {}
                        product["item_name"] = p.find("h3", attrs={"class": "product-name"}).text
                        product["old_price"], product["new_price"] = self._parse_prices_from_html(p)
                        product["sold"], product["remaining"] = self._parse_quantities_from_html(p)
                        parsed_products.add(item_name)
                        products.append(product)
                remaining_time = self._parse_end_time_from_html(sale)
                sale = FlashSaleMultiItem(url[8:23], sale_name, products, remaining_time)
                print(sale)
        except requests.exceptions.RequestException as e:
            print(e)
 
    def _parse_end_time_from_html(self, html):
        time = html.find("div", attrs={"id": "time-counter"}).text.replace(" ", "").split(":")
        time = datetime.timedelta(hours=int(time[0]), minutes=int(time[1]), seconds=int(time[2]))
        return time
 
    def _parse_prices_from_html(self, html):
        new = html.find("strong", attrs={"class": "product-price"})
        old = html.find("span", attrs={"class": "product-old-price"})
        if new is not None:
            new = new.text
            new = [n for n in new.split() if not "zł" in n]
            new = " ".join(new)
        else:
            new = "N/A"
        if old is not None:
            old = old.text
            old = [o for o in old.split() if not "zł" in o]
            old = " ".join(old)
        else:
            old = "N/A"
        return old, new
 
    def _parse_quantities_from_html(self, html):
        # euro does not provide quantity of items
        sold, remaining = "N/A", "N/A"
        return sold, remaining
 
    def _parse_item_name_from_html(self, html):
        name = html.find("h3", attrs={"class": "product-name"}).text
        return name