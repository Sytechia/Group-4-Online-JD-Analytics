import scrapy
import sqlite3
import schedule, time
from urllib.parse import quote_plus  # To encode job titles for URLs
from scrapy.crawler import CrawlerProcess
from scrapy.spidermiddlewares.httperror import HttpError
from controllers.parse_data import parse_job, update_existing_job
from controllers.db_connections import get_db_connection
from twisted.internet.error import DNSLookupError, TimeoutError, TCPTimedOutError
from multiprocessing import Process


class JobSpider(scrapy.Spider):
    name = "job_spider"

    # List of job titles to search for
    job_titles = [
        "Software Engineer",
        "Systems Administrator", "Network Engineer",
        "Database Administrator", "IT Support Specialist", "DevOps Engineer",
        "Security Analyst", "Web Developer", "Data Scientist", "Cloud Architect",
        "Project Manager", "Business Analyst", "Quality Assurance Engineer",
        "Mobile Developer", "Technical Support Engineer", "Product Manager",
        "UI/UX Designer", "IT Manager", "Solutions Architect", "Full Stack Developer"
    ]

    start_urls = [
        f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={quote_plus(job_title)}&location=Singapore&geoId=102454443&trk=public_jobs_jobs-search-bar_search-submit&start={i*25}"
        for job_title in job_titles for i in range(2)
    ]

    handle_httpstatus_list = [301, 302]

    def __init__(self):
        self.conn = get_db_connection()  # Establish a connection to the database
        self.cursor = self.conn.cursor()  # Initialize the cursor

    def start_requests(self):
        for url in self.start_urls:
            print(f"Scrapping: {url}")
            yield scrapy.Request(url, callback=self.parse, errback=self.errback, dont_filter=True, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'})
            time.sleep(1)


    def parse(self, response):
        yield from parse_job(response, self.cursor, self.conn)

    #calls the data cleaning function
    def parse_data(self, response):
        yield from parse_job(response, self.cursor, self.conn)

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
            
    @classmethod
    def get_job_titles(cls):
        return cls.job_titles

# if __name__ == "__main__":
#     process = CrawlerProcess()
#     process.crawl(JobSpider)
#
#     @defer.inlineCallbacks
#     def crawl():
#         yield process.crawl(JobSpider)
#
#     # def run_crawler():
#     #     task.LoopingCall(crawl).start(5.0)
#
#     # process.start(run_crawler())
#
#     process.start()