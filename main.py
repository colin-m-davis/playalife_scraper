from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from webdriver_manager.chrome import ChromeDriverManager

from bs4 import BeautifulSoup

import re

import pandas as pd


class PlayaLifeScraper:
    def __init__(self, url='https://www.playalifeiv.com/vacancies'):
        self.url = url

    def scrape(self):
        print('attempting to scrape ' + self.url)

        options = Options()
        options.headless = True
        options.add_argument('--window-size=1920,1080')

        driver = webdriver.Chrome(
            options=options,
            service=Service(ChromeDriverManager().install())
        )
        driver.get(self.url)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'listing-section'))
        )

        total_html = BeautifulSoup(driver.find_element(By.ID, 'total').get_attribute('innerHTML'), 'html.parser')
        total = int(total_html.find('strong').text)

        listings = []
        attempts = 0
        while (len(listings) < (total - 1)) and (attempts < (total + 1)):  # 2nd condition--is there a better way?
            listings = driver.find_elements(By.CLASS_NAME, 'listing-item')
            driver.execute_script('arguments[0].scrollIntoView();', listings[-1])
            attempts += 1

        print('# listings gathered: ' + str(len(listings)))

        rows = []
        for listing in listings:
            soup = BeautifulSoup(listing.get_attribute('innerHTML'), 'html.parser')

            address = str(soup.find('a', {'class': 'slider-link'})['aria-label'])
            raw_link = str(soup.find('a', {'class': 'slider-link'})['href'])
            link = 'https://www.playalifeiv.com' + raw_link
            raw_rent = soup.find('h3', {'class': 'rent'}).text if soup.find('h3', {'class': 'rent'}) else ''
            rent = float(''.join(c for c in raw_rent if c.isdigit())) if raw_rent else -1
            raw_bed = soup.find('div', {'class': 'feature beds'}).text
            bed = float(re.findall('\d*\.?\d+', raw_bed)[0])
            raw_bath = soup.find('div', {'class': 'feature baths'}).text
            bath = float(re.findall('\d*\.?\d+', raw_bath)[0])

            row = [address, link, rent, bed, bath]
            rows.append(row)

        df = pd.DataFrame(rows, columns=['Address', 'Link', 'Rent', 'Bed', 'Bath'])
        df.to_csv(r'playalifeiv.csv')

        driver.quit()


class ApartmentsComScraper:
    def __init__(self, url='https://www.zillow.com/isla-vista-ca/rentals/'):
        self.url = url

    def scrape(self):
        print('attempting to scrape ' + self.url)

        options = Options()
        options.headless = True
        options.add_argument('--window-size=1920,1080')

        driver = webdriver.Chrome(
            options=options,
            service=Service(ChromeDriverManager().install())
        )
        driver.get(self.url)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'search-page-react-content'))
        )

        listings = driver.find_elements(By.CLASS_NAME, 'list-card-info')

        driver.quit()

        return listings

        # find number of pages of results

        # while i+1-th page exists, go to i+1-th page and scrape results

        # organize all results in dataframe and save as csv file


print(PlayaLifeScraper().scrape())
