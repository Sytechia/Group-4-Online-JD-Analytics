# parse_data.py
import re
import sqlite3

import bleach
import openai
from bs4 import BeautifulSoup
import requests
import time
from secret_key import openai_api_key


def parse_job(response, cursor, conn):
    soup = BeautifulSoup(response.body, 'html.parser')
    jobs = soup.find_all("div", class_="base-card")
    print(f"Found {len(jobs)} jobs")

    for job in jobs:
        job_item = {
            'job_id': None,
            'original_job_title': None,
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
                #Check if any updates are needed
                update_existing_job(cursor, conn, job_item)
                continue

            job_title_tag = job.find("h3", class_="base-search-card__title")
            if job_title_tag:
                original_title = job_title_tag.get_text(strip=True)
                print(f"Original job title: {original_title}")
                if isinstance(original_title, str):
                    job_item['original_job_title'] = original_title
                    job_item['job_title'] = extract_job_position(original_title)
                    print(f"Cleaned job title: {job_item['job_title']}")
                else:
                    print(f"Invalid job title: {original_title}")
                    continue

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

            job_item['job_position_level'] = get_job_position_level(job_position_level_soup,job_item['job_description'])


            insert_job_into_db(cursor, conn, job_item)

            yield job_item


def insert_job_into_db(cursor, conn, job_item):
    try:
        cursor.execute('''
            INSERT INTO jobdesc (job_id, original_job_title,job_title, job_detail_url, job_listed, job_description, company_name, company_link, company_location, job_position_level)
            VALUES (?, ?, ?, ?, ?, ?, ?,?,?,?)
        ''', (
            job_item['job_id'], job_item['original_job_title'], job_item['job_title'], job_item['job_detail_url'], job_item['job_listed'], job_item['job_description'],
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

def update_existing_job(cursor, conn, job_item):
    cursor.execute('SELECT * FROM jobdesc WHERE job_id = ?', (job_item['job_id'],))
    existing_job = cursor.fetchone()

    if not existing_job:
        print(f"Job ID {job_item['job_id']} not found in the database.")
        return

    updates = []
    update_values = []

    for key, value in job_item.items():
        if value and value != existing_job[key]:
            updates.append(f"{key} = ?")
            update_values.append(value)

    if not updates:
        print(f"No updates required for Job ID {job_item['job_id']}.")
        return

    if updates:
        update_values.append(job_item['job_id'])
        update_query = f"UPDATE jobdesc SET {', '.join(updates)} WHERE job_id = ?"
        cursor.execute(update_query, update_values)
        conn.commit()
        print(f"Updated job: {job_item['job_detail_url']}")

def get_job_description(job_description_soup):
    if job_description_soup is None:
        return "Could not retrieve Job Description due to rate limiting"

    if job_description_soup:
        #unwrap elements
        for element in job_description_soup.find_all(['span']):
            element.unwrap()

        # Remove unwanted strings
        unwanted_strings = ['Show less', 'Show more']
        for unwanted in unwanted_strings:
            for elem in job_description_soup(text=lambda text: text and unwanted in text):
                elem.extract()

        print(f"Job Description: {job_description_soup}")
        print(f"Job Description Prettified!!!!!!!!!: {job_description_soup.prettify()}")

        # # Get the cleaned HTML content
        html_content = str(job_description_soup.prettify())

        print(f"html_content: {html_content}")

        # Sanitize the HTML to prevent XSS attacks
        allowed_tags = [
            'p', 'ul', 'ol', 'li', 'strong', 'br', 'em', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
            'blockquote', 'code', 'pre', 'hr', 'table', 'thead', 'tbody', 'tr', 'th', 'td',
            'a', 'b', 'i', 'u', 'span', 'div'
        ]
        allowed_attributes = {
            'a': ['href', 'title'],
            'img': ['src', 'alt', 'title'],
            '*': ['style']  # Allow style attribute if needed
        }

        clean_html = bleach.clean(
            html_content,
            tags=allowed_tags,
            attributes=allowed_attributes,
            strip=True
        )
        soup = BeautifulSoup(clean_html, 'html.parser')
        clean_html = soup.prettify()

        print(f"clean_html: {clean_html}")

        return clean_html

    else:
        return "Could not find Job Description"

def get_job_position_level(job_position_level_soup,job_description):
    if job_position_level_soup is None:
        return "Could not retrieve Job Description due to rate limiting"

    for item in job_position_level_soup:
        header = item.find('h3', class_='description__job-criteria-subheader')
        if header and header.get_text(strip=True) == 'Seniority level':
            job_position_level = item.find('span', class_='description__job-criteria-text').get_text(strip=True)
            if job_position_level != 'Not Applicable':
                return job_position_level
            else:
                prompt = (f"Based on the {job_description} job description, what is the seniority level of the job? You have to choose from the following options: "
                          f"Internship, Entry level, Associate, Mid-Senior level, Director, Executive."
                          f"Please choose the most appropriate option and only return the selected option.")

                openai.api_key = openai_api_key
                # Make a request to OpenAI's GPT model
                response = openai.chat.completions.create(
                    model="gpt-4o-mini",  # Ensure this is a valid model name
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=20
                )

                # Extract the text response
                job_position_level = response.choices[0].message.content.strip()
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
""""""""

def fetch_job_details(job_detail_url):
    response = make_request_with_retries(job_detail_url)
    if response is None:
        return None, None  # Return None if the request fails due to rate limiting

    soup = BeautifulSoup(response.content, 'html.parser')

    job_description = soup.find('div', class_='description__text description__text--rich')
    job_position_level = soup.find_all('li', class_='description__job-criteria-item')
    return job_description, job_position_level


def extract_job_position(job_title):
    prompt = (f"Extract the main job position from the following title, keeping relevant keywords like "
              f"coding languages, experience levels (e.g., Senior, Graduate, Trainee), "
              f"but remove location, dates, and other extra details: "
              f"\"{job_title}\". Return only the job title and ensure no quotes are included.")


    openai.api_key = openai_api_key
    # Make a request to OpenAI's GPT model
    response = openai.chat.completions.create(
        model="gpt-4o-mini",  # Ensure this is a valid model name
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=20
    )

    # Extract the text response
    job_position = response.choices[0].message.content.strip()
    return job_position











