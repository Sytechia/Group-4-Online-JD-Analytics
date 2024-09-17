# Main file that runs the application
from scrapy.crawler import CrawlerProcess
from blueprints import app
import os
from controllers.crawler import JobSpider
from controllers.skill_diagram import soft_skill, hard_skills

if __name__ == "__main__":
    process = CrawlerProcess()
    process.crawl(JobSpider)
    process.start()
    soft_skill()
    hard_skills()
    app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')
    app.run(debug=True, threaded=True)
    