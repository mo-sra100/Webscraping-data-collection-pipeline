import unittest
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from logging import exception
from selenium.common.exceptions import NoSuchElementException
import time
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy import inspect
import boto3
from file4 import Scraper
from selenium.webdriver.chrome.service import Service

class ScraperTestCase(unittest.TestCase):
    def setUp(self):
        self.bot_scraper = Scraper()
        self.directory1 = f'raw_data/{time.strftime("%d_%m_%Y_%H_%M")}'
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
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

    def test_correct_url(self):
        """Unit test to ensure the webscraper is scraping the correct website."""
        actual_value = self.bot_scraper.get_url()
        expected_value = 'https://www.ebay.co.uk/sch/i.html?_from=R40&_trksid=p2047675.m570.l1313&_nkw=Shark+Anti+Hair+Wrap+Cordless+Pet+Vacuum+Cleaner&_sacat=0'
        self.assertEqual(actual_value, expected_value)

    def test_accept_cookies(self):
        """Unit test to ensure the webscraper has accepted the cookies. It will attempt
        to accept cookies twice - the second attempt will result in 'NoSuchElementException'
        being raised as the cookies element will no longer exist if the first attempt
        successfully accepted the cookies."""
        self.bot_scraper.get_url()
        self.bot_scraper.accept_ebay_cookies()
        with self.assertRaises(NoSuchElementException):
            self.bot_scraper.repeat_accept_ebay_cookies()
        self.assertTrue(NoSuchElementException)

    def test_dictionary_not_empty(self):
        """Unit test to ensure the dictionary containing the information obtained
        from the webscraper is not empty. The dictionary produced by the webscraper
        will be compared to an empty dictionary."""
        self.bot_scraper.get_url()
        self.bot_scraper.accept_ebay_cookies()
        self.bot_scraper.scrape_data()
        self.bot_scraper.json_dump()
        empty_dict = {'UID':[], 'UUID':[], 'Product name':[], 'Price':[], 'Product URL':[], 'Image URL(s)':[]}
        self.assertNotEqual(empty_dict, self.bot_scraper.product_dictionary)

    def test_for_duplicates_in_database(self):
        """Unit test to ensure the same product has not been scraped more than once.
        The counter will increase by 1 every time a specific UID is found to have a
        duplicate. The final value of the counter will be compared to a value of 0,
        and both variables should be equal"""
        cur = self.engine.execute(f''' SELECT (product_dictionary."UID")::text, COUNT("UID") FROM product_dictionary GROUP BY product_dictionary."UID" HAVING count("UID") > 0 ''')
        df = pd.DataFrame.from_dict(cur, orient='columns')
        expected_product_duplicate_count = 0
        print("The count per UID currently in the database is:")
        print(df)
        col_one_arr = df['count'].to_numpy()
        for x in col_one_arr:
            if x > 1:
                self.product_duplicate_count += 1
                print("UID count > 1")
        self.assertEqual(expected_product_duplicate_count, self.product_duplicate_count)

    def tearDown(self):
        self.bot_scraper.driver.close()

if __name__ == '__main__':
    unittest.main(verbosity = 2, exit = False)