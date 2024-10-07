# Main file that runs the application

from blueprints import app
import os
import threading
import schedule
import time
from controllers.crawler import JobSpider
from scrapy.crawler import CrawlerProcess
from multiprocessing import Process

def start_crawler():
    process = CrawlerProcess()
    process.crawl(JobSpider)
    process.start()

def run_crawler():
    p = Process(target=start_crawler)
    p.start()
    p.join()

def schedule_crawler():
    run_crawler()
    schedule.every(30).minutes.do(run_crawler)      # 30-minute interval
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
if __name__ == "__main__":
    app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')
    crawler_thread = threading.Thread(target=schedule_crawler)
    crawler_thread.start()
    app.run(debug=True, threaded=True)
