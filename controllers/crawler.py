import scrapy

import sqlite3
from scrapy.crawler import CrawlerProcess

from controllers.parse_data import parse_job

import time
import requests

from db_connections import get_db_connection

class JobSpider(scrapy.Spider):
    name = "job_spider"
    def __init__(self, keyword=None, start=0, *args, **kwargs):
        super(JobSpider, self).__init__(*args, **kwargs)
        self.keyword = keyword
        self.start = int(start)
        self.start_urls = [
            f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={self.keyword}&location=Singapore&geoId=102454443&trk=public_jobs_jobs-search-bar_search-submit&start={self.start}"
        ]
        print("Initializing JobSpider and getting db connection!")
        try:
            self.conn = get_db_connection()  # Establish a connection to the database
            self.cursor = self.conn.cursor()  # Initialize the cursor
            self.parsed_jobs = []

        except sqlite3.Error as e:
            self.logger.error(f"Error connecting to database: {e}")

    def parse(self, response):
        yield scrapy.Request(url=self.start_urls[0], callback=self.parse_data)

    #calls the data cleaning function
    def parse_data(self, response):
        try:
            jobs = parse_job(response, self.cursor, self.conn)
            for job_item in jobs:
                self.parsed_jobs.append(job_item)
            if len(jobs) == 25: 
                self.start += 25
                next_page = f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={self.keyword}&location=Singapore&geoId=102454443&trk=public_jobs_jobs-search-bar_search-submit&start={self.start}"
                yield scrapy.Request(url=next_page, callback=self.parse_data)

        except Exception as e:
            self.logger.error(f"Error parsing data: {e}")

    # close the database session
    def close(self, reason):
        if self.conn:
            self.conn.close()
            self.logger.info("Database connection closed.")

if __name__ == "__main__":
    conn, cursor = setup_database()
    process = CrawlerProcess()
    process.crawl(JobSpider)
    process.start()