from tools import scrapers

def main():
    scraper = scrapers.MoreleScraper()
    scraper.scrap()
    scraper = scrapers.XKomScraper()
    scraper.scrap()
    scraper = scrapers.EuroScraper()
    scraper.scrap()

if __name__ == "__main__":
    main()
