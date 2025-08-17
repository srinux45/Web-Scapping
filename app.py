from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
import difflib

app = Flask(__name__)

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
HEADERS = {'User-Agent': USER_AGENT}

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        role = request.form.get('role', '').strip()
        location = request.form.get('location', '').strip()
        experience = request.form.get('experience', '').strip()

        jobs = scrape_jobs(role, location, experience)

        message = "No jobs found." if not jobs else None
        return render_template('index.html', jobs=jobs, message=message)

    return render_template('index.html', jobs=[], message=None)


def is_partial_match(query, text):
    """Check if query partially matches text using sequence matching."""
    match_ratio = difflib.SequenceMatcher(None, query.lower(), text.lower()).ratio()
    return match_ratio > 0.5


def scrape_jobs(role, location, experience):
    """Scrape jobs from TimesJobs and LinkedIn."""
    jobs = []

    def fetch_url(url):
        try:
            response = requests.get(url, headers=HEADERS)
            response.raise_for_status()  # Raise HTTPError for bad responses
            return response
        except requests.exceptions.RequestException as e:
            print(f"Error fetching URL {url}: {e}")
            return None

    # TimesJobs scraping
    timesjobs_url = (
        f"https://www.timesjobs.com/candidate/job-search.html?searchType=personalizedSearch&from=submit"
        f"&txtKeywords={role.replace(' ', '+')}&txtLocation={location.replace(' ', '+')}"
    )
    response = fetch_url(timesjobs_url)
    if response:
        soup = BeautifulSoup(response.text, 'html.parser')
        for li in soup.find_all(name="li", attrs={"class": "clearfix job-bx wht-shd-bx"}):
            title_elem = li.find(name="header", attrs={"class": "clearfix"})
            company_elem = li.find(name="h3", attrs={"class": "joblist-comp-name"})
            location_elem = li.find(name="ul", attrs={"class": "top-jd-dtl clearfix"})
            posted_date = li.find(name="span", attrs={"class": "sim-posted"})
            summary_elem = li.find(name="ul", attrs={"class": "list-job-dtl clearfix"})

            # Extract job details with default values
            title = title_elem.a.text.strip() if title_elem and title_elem.a else "Not specified"
            company = company_elem.text.strip() if company_elem else "Not specified"
            location = location_elem.span.text.strip() if location_elem and location_elem.span else "Not specified"
            summary = summary_elem.li.text.strip() if summary_elem and summary_elem.li else "Not specified"
            job_url = title_elem.a['href'] if title_elem and title_elem.a else "#"
            date_posted = posted_date.text.strip() if posted_date else "N/A"

            if is_partial_match(role, title) or is_partial_match(location, location):
                jobs.append({
                    "title": title,
                    "company": company,
                    "location": location,
                    "summary": summary,
                    "date": date_posted,
                    "url": job_url,
                    "source": "TimesJobs"
                })

    # LinkedIn scraping
    linkedin_url = (
        f"https://www.linkedin.com/jobs/search?keywords={role.replace(' ', '%20')}&location={location.replace(' ', '%20')}"
    )
    response = fetch_url(linkedin_url)
    if response:
        soup = BeautifulSoup(response.text, 'html.parser')
        for job in soup.find_all(name="div", attrs={"class": "base-card"}):
            title_elem = job.find(name="h3", attrs={"class": "base-search-card__title"})
            company_elem = job.find(name="h4", attrs={"class": "base-search-card__subtitle"})
            location_elem = job.find(name="span", attrs={"class": "job-search-card__location"})
            date_posted = job.find(name="time", attrs={"class": "job-search-card__listdate"})

            # Extract LinkedIn job details with default values
            title = title_elem.text.strip() if title_elem else "Not specified"
            company = company_elem.text.strip() if company_elem else "Not specified"
            location = location_elem.text.strip() if location_elem else "Not specified"
            job_url = job.find(name="a", attrs={"class": "base-card__full-link"})['href'] if job.find(name="a", attrs={"class": "base-card__full-link"}) else "#"
            date_posted = date_posted.text.strip() if date_posted else "N/A"

            if is_partial_match(role, title) or is_partial_match(location, location):
                jobs.append({
                    "title": title,
                    "company": company,
                    "location": location,
                    "summary": "",
                    "date": date_posted,
                    "url": job_url,
                    "source": "LinkedIn"
                })

    return jobs


if __name__ == '__main__':
    app.run(debug=True)
