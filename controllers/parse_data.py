# parse_data.py
import re
import sqlite3
from bs4 import BeautifulSoup
import requests

def parse_job(response, cursor, conn):
    soup = BeautifulSoup(response.body, 'html.parser')
    jobs = soup.find_all("div", class_="base-card")
    # print(soup.prettify())

    for job in jobs:
        job_item = {
            'job_id': None,
            'job_title': None,
            'job_detail_url': None,
            'job_listed': None,
            'company_name': None,
            'company_link': None,
            'company_location': None,
            'job_description': None
        }

        job_detail_url_tag = job.find("a", class_="base-card__full-link")
        if job_detail_url_tag:
            job_item['job_detail_url'] = job_detail_url_tag.get('href').strip()

            # Extract job ID from job_detail_url
            job_id_match = re.search(r'view/[^/]+-(\d+)', job_item['job_detail_url'])
            if job_id_match:
                job_item['job_id'] = job_id_match.group(1)
                job_item['job_detail_url'] = 'https://www.linkedin.com/jobs/view/' + job_item['job_id'] + '/'
                print(f"Extracted Job ID: {job_item['job_id']}")
            else:
                print("No job ID found in the URL")
                continue


            if job_id_exists(cursor, job_item['job_id']):
                print(f"Job ID {job_item['job_id']} already exists: {job_item['job_detail_url']}")
                continue
            # # Check if job ID already exists in the database

            job_title_tag = job.find("h3", class_="base-search-card__title")
            if job_title_tag:
                job_item['job_title'] = job_title_tag.get_text(strip=True)

            job_listed_tag = job.find("time", class_="job-search-card__listdate--new")
            if job_listed_tag:
                job_item['job_listed'] = job_listed_tag.get_text(strip=True)
            else:
                job_item['job_listed'] = 'Not Listed'

            company_name_tag = job.find("h4", class_="base-search-card__subtitle").find("a")
            if company_name_tag:
                job_item['company_name'] = company_name_tag.get_text(strip=True)
                job_item['company_link'] = company_name_tag.get('href')
            else:
                continue

            job_item['job_description'] = get_job_description(job_item['job_detail_url'])

            company_location_tag = job.find("span", class_="job-search-card__location")
            if company_location_tag:
                job_item['company_location'] = company_location_tag.get_text(strip=True)


            insert_job_into_db(cursor, conn, job_item)

            yield job_item

def insert_job_into_db(cursor, conn, job_item):
    try:
        cursor.execute('''
            INSERT INTO jobdesc (job_id, job_title, job_detail_url, job_listed, job_description, company_name, company_link, company_location)
            VALUES (?, ?, ?, ?, ?, ?, ?,?)
        ''', (
            job_item['job_id'], job_item['job_title'], job_item['job_detail_url'], job_item['job_listed'], job_item['job_description'],
            job_item['company_name'], job_item['company_link'], job_item['company_location']
        ))
        conn.commit()
        print(f"Inserted job: {job_item['job_detail_url']}")
    except sqlite3.IntegrityError as e:
        print(f"IntegrityError: {e}")
        print(f"Job listing already exists: {job_item['job_detail_url']}")
    except Exception as e:
        print(f"Exception: {e}")

def job_id_exists(cursor, job_id):
    cursor.execute('SELECT 1 FROM jobdesc WHERE job_id = ?', (job_id,))
    return cursor.fetchone() is not None

def get_job_description(job_detail_url):
    response = requests.get(job_detail_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    div = soup.find('div', class_='description__text description__text--rich')
    if div:
        # Remove unwanted elements
        for element in div.find_all(['span', 'a']):
            element.decompose()

        # Replace bullet points
        for ul in div.find_all('ul'):
            for li in ul.find_all('li'):
                li.insert(0, '-')

        text = div.get_text(separator='\n').strip()
        text = text.replace('\n\n', '')
        text = text.replace('::marker', '-')
        text = text.replace('-\n', '- ')
        text = text.replace('Show less', '').replace('Show more', '')
        return text
    else:
        return "Could not find Job Description"





