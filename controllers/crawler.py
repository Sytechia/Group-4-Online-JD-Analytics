import scrapy
import nltk
import sqlite3
from scrapy.crawler import CrawlerProcess
from scrapy.spidermiddlewares.httperror import HttpError
from parse_data import parse_job
from db_connections import get_db_connection
from twisted.internet import reactor, defer, task
from twisted.internet.error import DNSLookupError, TimeoutError, TCPTimedOutError

import time
import requests

class JobSpider(scrapy.Spider):
    name = "job_spider"
    start_urls = [
        "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=Python&location=Singapore&geoId=102454443&trk=public_jobs_jobs-search-bar_search-submit&start=0"
    ]
    handle_httpstatus_list = [301, 302]

    def __init__(self):
        print("Initializing JobSpider and getting db connection!")
        self.conn = get_db_connection()  # Establish a connection to the database
        self.cursor = self.conn.cursor()  # Initialize the cursor
        self.parsed_jobs = []

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.parse, errback=self.errback, dont_filter=True, headers={'User-Agent': 'Mozilla/5.0'})

    def parse(self, response):
        yield scrapy.Request(url=self.start_urls[0], callback=self.parse_data)

    #calls the data cleaning function
    def parse_data(self, response):
        # yield from parse_job(response, self.cursor, self.conn)
        for job_item in parse_job(response, self.cursor, self.conn):
            self.parsed_jobs.append(job_item)

    def errback(self, failure):
        self.logger.error(repr(failure))
        if failure.check(HttpError):
            response = failure.value.response
            self.logger.error('HttpError on %s', response.url)
        elif failure.check(DNSLookupError):
            request = failure.request
            self.logger.error('DNSLookupError on %s', request.url)
        elif failure.check(TimeoutError, TCPTimedOutError):
            request = failure.request
            self.logger.error('TimeoutError on %s', request.url)


if __name__ == "__main__":
    nltk.download('punkt')
    nltk.download('averaged_perceptron_tagger_eng')
    nltk.download('stopwords')
    process = CrawlerProcess()
    process.crawl(JobSpider)
    # process.start()

    @defer.inlineCallbacks
    def crawl():
        yield process.crawl(JobSpider)

    def run_crawler():
        task.LoopingCall(crawl).start(5.0)

    process.start(run_crawler())