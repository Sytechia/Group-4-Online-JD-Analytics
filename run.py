# Main file that runs the application

from blueprints import app
import os
import threading
from controllers.crawler import JobSpider
from scrapy.crawler import CrawlerProcess
from twisted.internet import defer, task

def start_crawler():
    process = CrawlerProcess()
    process.crawl(JobSpider)

    @defer.inlineCallbacks
    def crawl():
        yield process.crawl(JobSpider)

    def run_crawler():
        task.LoopingCall(crawl).start(1800.0)   # 30-minute interval

    process.start(run_crawler())

if __name__ == "__main__":
    app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')
    crawler_thread = threading.Thread(target=start_crawler)
    crawler_thread.start()
    app.run(debug=True, threaded=True)