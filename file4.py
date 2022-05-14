from http.client import FOUND
from logging import exception
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd
import urllib
import urllib.request
import uuid
import os
import json
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy import inspect
import boto3
import psycopg2
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem


class Scraper():
    def __init__(self):
        """Upon initialisation, a directory is created for this particular instance of
        running the webscraper - it is named using the date and time at which the instance
        occurs. The connection between this webscraper and the database is also created."""
        self.parent_dir = "/home/mo/Desktop/scratch/AICOREproject3/webscraper/raw_data"
        self.new_dir = f'{time.strftime("%m_%d_%Y_%H_%M")}'
        self.new_path = os.path.join(self.parent_dir, self.new_dir)
        if not os.path.exists(self.new_path):
            os.makedirs(self.new_path)
        
        opts = webdriver.ChromeOptions()
        opts.add_argument('headless')
        software_names = [SoftwareName.CHROME.value]
        operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value]   
        user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=100)
        # Get list of user agents.
        # user_agents = user_agent_rotator.get_user_agents()
        # Get Random User Agent String.
        user_agent = user_agent_rotator.get_random_user_agent()
        opts.add_argument(f'--user-agent={user_agent}')
        opts.add_argument('--no-sandbox')
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)

        self.url_list_index = 0
        self.last_item = 3
        self.product_dictionary = {'UID':[], 'UUID':[], 'Product name':[], 'Price':[], 'Product URL':[], 'Image URL(s)':[]}
        self.url_list = []
        self.product_duplicate_count = 0

        DATABASE_TYPE = 'postgresql'
        DBAPI = 'psycopg2'
        ENDPOINT = 'aicoreproject3db.cqevmilatvad.us-east-1.rds.amazonaws.com'
        USER = 'postgres'
        PASSWORD = 'killua123'
        PORT = 5432
        DATABASE = 'postgres'
        self.engine = create_engine(f"{DATABASE_TYPE}+{DBAPI}://{USER}:{PASSWORD}@{ENDPOINT}:{PORT}/{DATABASE}")
        self.inspector = inspect(self.engine)
        self.inspector.get_table_names()
        self.s3_client = boto3.client('s3')


    def get_url(self):
        """This function opens the provided URL in the webdriver."""
        time.sleep(0.5)
        url = 'https://www.ebay.co.uk/sch/i.html?_from=R40&_trksid=p2047675.m570.l1313&_nkw=Shark+Anti+Hair+Wrap+Cordless+Pet+Vacuum+Cleaner&_sacat=0'
        self.driver.get(url)
        return str(url)


    def accept_ebay_cookies(self):
        """This function selects the "Accept all" cookies option when prompted by the website."""
        time.sleep(1)
        xpath = '//button[@id="gdpr-banner-accept"]'        
        try:
            time.sleep(0.5)
            WebDriverWait(self.driver,10).until(EC.presence_of_element_located((By.XPATH, xpath)))
            self.driver.find_element(By.XPATH, xpath).click()
        except TimeoutException:
            print('accept_ebay_cookies TimeoutException error')
        except NoSuchElementException:
            print('accept_ebay_cookies NoSuchElementException error')
        except WebDriverException:
            print('accept_ebay_cookies WebDriverException')


    def repeat_accept_ebay_cookies(self):
        """This function selects the "Accept all" cookies option when prompted by the website.
        The purpose of this function is purely for a unit test which ensures the cookies
        have been accepted."""
        time.sleep(1)
        xpath = '//button[@id="gdpr-banner-accept"]'        
        time.sleep(0.5)
        self.driver.find_element(By.XPATH, xpath).click()


    def scrape_data(self):
        """This function collects the URLs for every product on the page, then iteratively 
        opens each URL. The UID scraped on each product page will be compared to the database,
        and if this product has already been scraped, it will be skipped. Otherwise the
        webscraper will collect the relevant information and store it within a dictionary.
        The product images are downloaded and stored within the directory created during
        initialisation."""
        time.sleep(1)
        xpath = '//div[@id="srp-river-results"]/ul'
        try:
            time.sleep(0.5)
            WebDriverWait(self.driver,10).until(EC.presence_of_element_located((By.XPATH, xpath)))
            product_container = self.driver.find_element(by = By.XPATH, value = xpath)
        except TimeoutException:
            print('product_container TimeoutException error')
        except NoSuchElementException:
            print('product_container NoSuchElementException error')
        except WebDriverException:
            print('product_container WebDriverException')

        xpath = '//div[@id="srp-river-results"]/ul/li'
        try:
            time.sleep(0.5)
            WebDriverWait(self.driver,10).until(EC.presence_of_element_located((By.XPATH, xpath)))
            individual_product = product_container.find_elements(by = By.XPATH, value = xpath)
        except TimeoutException:
            print('individual_product TimeoutException error')
        except NoSuchElementException:
            print('individual_product NoSuchElementException error')
        except WebDriverException:
            print('individual_product WebDriverException')

        for i in individual_product:
            time.sleep(0.5)
            url_tag = i.find_element(by = By.TAG_NAME, value = 'a')
            url_link = url_tag.get_attribute('href')
            self.url_list.append(url_link)
        # print(f"The length of self.url_list is {len(self.url_list)}")
        self.index_limit = len(self.url_list) - 1
        # print(self.url_list)

        while self.url_list_index < self.last_item:
            time.sleep(0.5)
            if self.url_list_index == self.index_limit:
                print("There are no more products left to scrape. The web scraper will stop.")
                break

            else:
                time.sleep(0.5)
                try:
                    time.sleep(0.5)
                    self.current_link = self.url_list[self.url_list_index]
                    # print(f"The index is currently: {self.url_list_index}")
                    self.driver.get(self.current_link)
                    # print(self.current_link)
                    # self.driver.save_screenshot(f"screenshot after get self.current_link at index {self.url_list_index}.png")
                except TimeoutException:
                    print('get_product TimeoutException error')
                    self.last_item += 1
                    self.url_list_index += 1
                    continue
                except NoSuchElementException:
                    print('get_product NoSuchElementException error')
                    self.last_item += 1
                    self.url_list_index += 1
                    continue
                except WebDriverException:
                    print('get_product WebDriverException error')
                    self.last_item += 1
                    self.url_list_index += 1
                    continue
                
                time.sleep(0.5)

                try:
                    time.sleep(0.5)
                    ebay_item_number = self.driver.find_element(by = By.XPATH, value = '//div[@id="descItemNumber"]').text
                    print(ebay_item_number)
                except TimeoutException:
                    print('ebay_item_number TimeoutException error')
                    self.last_item += 1
                    self.url_list_index += 1
                    continue
                except NoSuchElementException:
                    print('ebay_item_number NoSuchElementException error')
                    self.last_item += 1
                    self.url_list_index += 1
                    continue
                except WebDriverException:
                    print('ebay_item_number WebDriverException')
                    self.last_item += 1
                    self.url_list_index += 1
                    continue

                time.sleep(0.5)

                # the function of the following code is: if ebay_item_number NOT already in database then continue with webscraping and populate dictionary
                cur = self.engine.execute(f''' SELECT * from product_dictionary where "UID" = '{ebay_item_number}' ''')
                if not cur.fetchone():

                    time.sleep(0.5)
                    
                    print("Does not exist in database - this object will be scraped")
                    self.product_dictionary['UID'].append(ebay_item_number)
                    self.product_dictionary['Product URL'].append(self.url_list[self.url_list_index])
                    self.product_dictionary['UUID'].append(str(uuid.uuid4()))

                    try:
                        time.sleep(0.5)
                        name_tag = self.driver.find_element(by = By.XPATH, value = '//h1[@class="x-item-title__mainTitle"]/span').text
                        self.product_dictionary['Product name'].append(name_tag)
                    except TimeoutException:
                        print('Product name TimeoutException error')
                        self.product_dictionary['Product name'].append("N/A")
                    except NoSuchElementException:
                        self.product_dictionary['Product name'].append("N/A")
                        print('Product name NoSuchElementException error')
                    except WebDriverException:
                        print('Product name WebDriverException')
                        self.product_dictionary['Product name'].append("N/A")

                    time.sleep(0.5)

                    try:
                        time.sleep(0.5)
                        price_tag = self.driver.find_element(by = By.XPATH, value = '//span[@class="notranslate"]').text
                        self.product_dictionary['Price'].append(price_tag)
                    except TimeoutException:
                        print('Price TimeoutException error')
                        self.product_dictionary['Price'].append("N/A")
                    except NoSuchElementException:
                        print('Price NoSuchElementException error')
                        self.product_dictionary['Price'].append("N/A")
                    except WebDriverException:
                        print('Price WebDriverException error')
                        self.product_dictionary['Price'].append("N/A")

                    time.sleep(0.5)
                    
                    try:
                        time.sleep(0.5)
                        image_element = self.driver.find_element(by = By.XPATH, value ='//img[@id="icImg"]')
                        image_link = image_element.get_attribute('src')
                        if not os.path.exists(self.new_path):
                            os.makedirs(self.new_path)
                        urllib.request.urlretrieve(image_link, f'{self.new_path}/{ebay_item_number}.jpg')
                        response = self.s3_client.upload_file(f'{self.new_path}/{ebay_item_number}.jpg', 'aicoreproject3bucket', f'{ebay_item_number}.jpg')
                        time.sleep(1)
                        self.product_dictionary['Image URL(s)'].append(image_link)
                    except TimeoutException:
                        print('Image URLS TimeoutException error')
                        self.product_dictionary['Image URL(s)'].append("N/A")
                    except NoSuchElementException:
                        print('Image URLS NoSuchElementException error')
                        self.product_dictionary['Image URL(s)'].append("N/A")
                    except WebDriverException:
                        print('Image URLS WebDriverException error')
                        self.product_dictionary['Image URL(s)'].append("N/A")

                    time.sleep(0.5)

                else:
                    time.sleep(0.5)
                    pass
                    print("Already exists in database - this object will not be scraped")
                    self.last_item += 1
                
                self.url_list_index += 1

        # the following line is not used if running in headless mode (as no driver window will be opened) or if running unit tests (as it will conflict with teardown)
        # self.driver.quit()


    def json_dump(self):
        """This function saves the populated dictionary to the same folder as the
        downloaded product images (i.e. the directory created during initialisation)."""
        time.sleep(0.5)
        base = Path(self.new_path)
        jsonpath = base / ('data.json')
        jsonpath.write_text(json.dumps(self.product_dictionary, indent=4))


    def upload_dictionary_to_cloud(self):
        """This function uploads the data.json file to the RDS database and the
        images to the S3 data lake bucket."""
        response = self.s3_client.upload_file(f'{self.new_path}/data.json', 'aicoreproject3bucket', 'data.json')
        data = self.product_dictionary
        df = pd.DataFrame.from_dict(data, orient='columns')
        print("The following data will be added to the database (if all the products are already in the database it will say 'Empty DataFrame'):")
        print(df)
        df.to_sql('product_dictionary', self.engine, if_exists='replace')
        df = pd.read_sql_table('product_dictionary', self.engine)


if __name__ == '__main__' :
    scrapers = Scraper()
    scrapers.get_url()
    scrapers.accept_ebay_cookies()
    scrapers.scrape_data()
    scrapers.json_dump()
    scrapers.upload_dictionary_to_cloud()