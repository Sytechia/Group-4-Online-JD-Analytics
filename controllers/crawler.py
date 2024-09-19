import scrapy

import sqlite3
from scrapy.crawler import CrawlerProcess


from blueprints import setup_database
from controllers.parse_data import parse_job

import time
import requests

class JobSpider(scrapy.Spider):
    name = "job_spider"
    start_urls = [
        "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=Python&location=Singapore&geoId=102454443&trk=public_jobs_jobs-search-bar_search-submit&start=0"
    ]

    def __init__(self):
        print("Initializing JobSpider and getting db connection!")
        self.conn = sqlite3.connect('database.db')  # Establish a connection to the database
        self.cursor = self.conn.cursor()  # Initialize the cursor
        self.parsed_jobs = []

    def parse(self, response):
        yield scrapy.Request(url=self.start_urls[0], callback=self.parse_data)

    #calls the data cleaning function
    def parse_data(self, response):
        # yield from parse_job(response, self.cursor, self.conn)
        for job_item in parse_job(response, self.cursor, self.conn):
            self.parsed_jobs.append(job_item)


if __name__ == "__main__":
    conn, cursor = setup_database()
    process = CrawlerProcess()
    process.crawl(JobSpider)
    process.start()