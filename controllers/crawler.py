import scrapy
import re
import sqlite3

class JobSpider(scrapy.Spider):
    name = "job_spider"
    start_urls = [
        "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=Python&location=Singapore&geoId=102454443&trk=public_jobs_jobs-search-bar_search-submit&start=0"
    ]

    def __init__(self):
        print("Initializing JobSpider and getting db connection!")
        self.conn = sqlite3.connect('database.db')  # Establish a connection to the database
        self.cursor = self.conn.cursor()  # Initialize the cursor

    def parse(self, response):
        yield scrapy.Request(url=self.start_urls[0], callback=self.parse_job)

    def parse_job(self, response):
        print("parse_job function called")
        job_item = {}
        jobs = response.css("li")

        num_jobs_returned = len(jobs)
        print("******* Num Jobs Returned *******")
        print(num_jobs_returned)
        print('*****')

        for job in jobs:
            job_item['job_title'] = job.css("h3::text").get(default='not-found').strip()
            job_item['job_detail_url'] = job.css(".base-card__full-link::attr(href)").get(default='not-found').strip()
            job_item['job_listed'] = job.css('time::text').get(default='not-found').strip()

            job_item['company_name'] = job.css('h4 a::text').get(default='not-found').strip()
            job_item['company_link'] = job.css('h4 a::attr(href)').get(default='not-found')
            job_item['company_location'] = job.css('.job-search-card__location::text').get(default='not-found').strip()

            # Extract job ID from job_detail_url
            job_id_match = re.search(r'view/[^/]+-(\d+)', job_item['job_detail_url'])
            if job_id_match:
                job_item['job_id'] = job_id_match.group(1)
                print(f"Extracted Job ID: {job_item['job_id']}")
            else:
                print("No job ID found in the URL")
                job_item['job_id'] = 'not-found'

            # Check if job ID already exists in the database
            self.cursor.execute('SELECT 1 FROM jobdesc WHERE job_id = ?', (job_item['job_id'],))
            if self.cursor.fetchone():
                print(f"Job ID {job_item['job_id']} already exists: {job_item['job_detail_url']}")
                continue

            try:
                self.cursor.execute('''
                    INSERT INTO jobdesc (job_id, job_title, job_detail_url, job_listed, company_name, company_link, company_location)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    job_item['job_id'], job_item['job_title'], job_item['job_detail_url'], job_item['job_listed'],
                    job_item['company_name'], job_item['company_link'], job_item['company_location']
                ))
                self.conn.commit()
                print(f"Inserted job: {job_item['job_detail_url']}")
            except sqlite3.IntegrityError as e:
                print(f"IntegrityError: {e}")
                print(f"Job listing already exists: {job_item['job_detail_url']}")
            except Exception as e:
                print(f"Exception: {e}")

            yield job_item