from flask import Flask,request
from blueprints.routes import home_blueprint, login_blueprint, register_user_blueprint, profile_page_blueprint, error_blueprint, error500_blueprint
import sqlite3
import scrapy
import re

app = Flask(__name__)
app.register_blueprint(home_blueprint)
app.register_blueprint(login_blueprint)
app.register_blueprint(register_user_blueprint)
app.register_blueprint(profile_page_blueprint)
app.register_blueprint(error_blueprint)
app.register_blueprint(error500_blueprint)

# Use this as initial function to set up the database
def setup_database():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY,
            job_id TEXT NOT NULL,
            job_title TEXT NOT NULL,
            job_detail_url TEXT NOT NULL,
            job_listed TEXT NOT NULL,
            company_name TEXT NOT NULL,
            company_link TEXT,
            company_location TEXT NOT NULL,
            unique(job_detail_url,company_name,job_listed)
        )
    ''')
    conn.commit()
    return conn, cursor

def AddRecord():
    pass


### Ray you need to edit this portion of the code, putting it here as a reference
def start_requests(api_url):
    first_job_on_page = 0
    first_url = api_url + str(first_job_on_page)
    return scrapy.Request(url=first_url, callback=parse_job, meta={'first_job_on_page': first_job_on_page})

def parse_job(response):
    first_job_on_page = response.meta['first_job_on_page']

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
        job_item['job_id'] = job.css('.job-search-card__location::text').get(default='not-found').strip()

        # Extract job ID from job_detail_url
        job_id_match = re.search(r'view/[^/]+-(\d+)', job_item['job_detail_url'])
        if job_id_match:
            job_item['job_id'] = job_id_match.group(1)
            print(f"Extracted Job ID: {job_item['job_id']}")
        else:
            print("No job ID found in the URL")
            job_item['job_id'] = 'not-found'

        # Check if job ID already exists in the database
        cursor.execute('SELECT 1 FROM jobs WHERE job_id = ?', (job_item['job_id'],))
        if cursor.fetchone():
            print(f"Job ID {job_item['job_id']} already exists: {job_item['job_detail_url']}")
            continue

        try:
            cursor.execute('''
                INSERT INTO jobs (job_id, job_title, job_detail_url, job_listed, company_name, company_link, company_location)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                job_item['job_id'], job_item['job_title'], job_item['job_detail_url'], job_item['job_listed'],
                job_item['company_name'], job_item['company_link'], job_item['company_location']
            ))
            conn.commit()
            print(f"Inserted job: {job_item['job_detail_url']}")
        except sqlite3.IntegrityError:
            print(f"Job listing already exists: {job_item['job_detail_url']}")

        yield job_item

conn, cursor = setup_database()
api_url = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=Python&location=Singapore&geoId=102454443&trk=public_jobs_jobs-search-bar_search-submit&start="
request = start_requests(api_url)

