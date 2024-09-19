# Main file that runs the application
from scrapy.crawler import CrawlerProcess
from blueprints import app
import os
from controllers.crawler import JobSpider


if __name__ == "__main__":
    app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')
    app.run(debug=True, threaded=True)
    