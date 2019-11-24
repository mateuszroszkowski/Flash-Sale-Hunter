from __future__ import absolute_import
from .deals import FlashSale

import requests
import datetime
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
        old, new = old.split()[0], new.split()[0]
        return old, new

    def _parse_quantities_from_html(self, html):
        sold = html.find("div", attrs={"class": "status-box-expired"}).text.replace('\n','')
        remaining = html.find("div", attrs={"class": "status-box-was"}).text.replace('\n','')
        sold, remaining = sold.split()[1], remaining.split()[1]
        return sold, remaining

    