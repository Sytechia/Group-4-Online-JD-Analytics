import schedule
import time
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from crawler import JobSpider

def run_spider():
    process = CrawlerProcess(get_project_settings())
    process.crawl(JobSpider, keyword='Java')  # Replace 'Java' with the desired keyword or make it dynamic
    process.start()

# Schedule the spider to run every minute
schedule.every(1).minutes.do(run_spider)

while True:
    schedule.run_pending()
    time.sleep(1)