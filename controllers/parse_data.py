# parse_data.py
import re
import sqlite3
from bs4 import BeautifulSoup
import requests
import time

def parse_job(response, cursor, conn):
    soup = BeautifulSoup(response.body, 'html.parser')
    jobs = soup.find_all("div", class_="base-card")
    print(f"Found {len(jobs)} jobs")
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
            'job_description': None,
            'job_position_level': None
        }

        job_detail_url_tag = job.find("a", class_="base-card__full-link")
        if job_detail_url_tag:
            job_item['job_detail_url'] = job_detail_url_tag.get('href').strip()

            # Check if job ID already exists in the database
            # Extract job ID from job_detail_url
            job_id_match = re.search(r'view/[^/]+-(\d+)', job_item['job_detail_url'])
            if job_id_match:
                job_item['job_id'] = job_id_match.group(1)
                job_item['job_detail_url'] = f"https://www.linkedin.com/jobs/view/{job_item['job_id']}/"
                print(f"Extracted Job ID: {job_item['job_id']}")
            else:
                print("No job ID found in the URL")
                continue

            if job_id_exists(cursor, job_item['job_id']):
                print(f"Job ID {job_item['job_id']} already exists: {job_item['job_detail_url']}")
                continue


            job_title_tag = job.find("h3", class_="base-search-card__title")
            if job_title_tag:
                job_item['job_title'] = job_title_tag.get_text(strip=True)

            job_listed_tag = job.find("time", class_=["job-search-card__listdate", "job-search-card__listdate--new"])
            if job_listed_tag:
                datetime_value = job_listed_tag.get('datetime')
                if datetime_value:
                    job_item['job_listed'] = datetime_value  # Use 'datetime' attribute if available
                else:
                    job_item['job_listed'] = job_listed_tag.text.strip()  # Fallback to text content if datetime is not available
            else:
                job_item['job_listed'] = "Not specified"

            company_name_tag = job.find("h4", class_="base-search-card__subtitle").find("a")
            if company_name_tag:
                job_item['company_name'] = company_name_tag.get_text(strip=True)
                job_item['company_link'] = company_name_tag.get('href')
            else:
                continue

            company_location_tag = job.find("span", class_="job-search-card__location")
            if company_location_tag:
                job_item['company_location'] = company_location_tag.get_text(strip=True)

            get_job_description_soup, job_position_level_soup = fetch_job_details(job_item['job_detail_url'])

            job_item['job_description'] = get_job_description(get_job_description_soup)
            job_item['job_position_level'] = get_job_position_level(job_position_level_soup)

            insert_job_into_db(cursor, conn, job_item)

            yield job_item


def insert_job_into_db(cursor, conn, job_item):
    try:
        cursor.execute('''
            INSERT INTO jobdesc (job_id, job_title, job_detail_url, job_listed, job_description, company_name, company_link, company_location, job_position_level)
            VALUES (?, ?, ?, ?, ?, ?, ?,?,?)
        ''', (
            job_item['job_id'], job_item['job_title'], job_item['job_detail_url'], job_item['job_listed'], job_item['job_description'],
            job_item['company_name'], job_item['company_link'], job_item['company_location'], job_item['job_position_level']
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

def get_job_description(job_description_soup):
    if job_description_soup is None:
        return "Could not retrieve Job Description due to rate limiting"

    if job_description_soup:
        # Remove unwanted elements
        for element in job_description_soup.find_all(['span', 'a']):
            element.decompose()

        # Replace bullet points
        for ul in job_description_soup.find_all('ul'):
            for li in ul.find_all('li'):
                li.insert(0, '-')

        text = job_description_soup.get_text(separator='\n').strip()
        text = text.replace('\n\n', '')
        text = text.replace('::marker', '-')
        text = text.replace('-\n', '- ')
        text = text.replace('Show less', '').replace('Show more', '')
        return text
    else:
        return "Could not find Job Description"

def get_job_position_level(job_position_level_soup):
    if job_position_level_soup is None:
        return "Could not retrieve Job Description due to rate limiting"

    for item in job_position_level_soup:
        header = item.find('h3', class_='description__job-criteria-subheader')
        if header and header.get_text(strip=True) == 'Seniority level':
            job_position_level = item.find('span', class_='description__job-criteria-text').get_text(strip=True)
            return job_position_level


"Ray make this function as a portion of your code as well"
def make_request_with_retries(url, retries=5, backoff_factor=1):
    for i in range(retries):
        response = requests.get(url)
        if response.status_code == 429:
            wait_time = backoff_factor * (2 ** i)
            print(f"Rate limited. Retrying in {wait_time} seconds...")
            time.sleep(wait_time)
        else:
            return response
    return None

def fetch_job_details(job_detail_url):
    response = make_request_with_retries(job_detail_url)
    if response is None:
        return None, None  # Return None if the request fails due to rate limiting

    soup = BeautifulSoup(response.content, 'html.parser')

    job_description = soup.find('div', class_='description__text description__text--rich')
    job_position_level = soup.find_all('li', class_='description__job-criteria-item')
    return job_description, job_position_level










