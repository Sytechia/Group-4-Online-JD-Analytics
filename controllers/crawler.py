import scrapy
import nltk
import sqlite3

from scrapy.crawler import CrawlerProcess
from controllers.parse_data import parse_job
from controllers.db_connections import get_db_connection


class JobSpider(scrapy.Spider):
    name = "job_spider"
    start_urls = [
        "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=Python&location=Singapore&geoId=102454443&trk=public_jobs_jobs-search-bar_search-submit&start=25"
    ]

    def __init__(self):
        print("Initializing JobSpider and getting db connection!")
        self.conn = get_db_connection()  # Establish a connection to the database
        self.cursor = self.conn.cursor()  # Initialize the cursor

    def parse(self, response):
        yield scrapy.Request(url=self.start_urls[0], callback=self.parse_data)

    #calls the data cleaning function
    def parse_data(self, response):
        yield from parse_job(response, self.cursor, self.conn)


if __name__ == "__main__":
    process = CrawlerProcess()
    process.crawl(JobSpider)
    process.start()