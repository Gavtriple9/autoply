import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random


def scrape_indeed_jobs(query, location, num_pages=1):
    base_url = "https://www.indeed.com/jobs"
    job_data = []

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    for page in range(num_pages):
        start = page * 10  # Indeed shows 10 jobs per page by default
        params = {"q": query, "l": location, "start": start}

        print(f"Scraping page {page + 1} for '{query}' in '{location}'...")
        try:
            response = requests.get(base_url, params=params, headers=headers)
            response.raise_for_status()  # Raise an exception for HTTP errors

            soup = BeautifulSoup(response.text, "html.parser")

            # Find all job cards (Inspect HTML to find the correct tags/classes)
            # This class name might change over time, so always verify!
            job_cards = soup.find_all("div", class_="job_seen_beacon")

            if not job_cards:
                print("No more job cards found on this page. Exiting.")
                break

            for card in job_cards:
                title_tag = card.find("h2", class_="jobTitle")
                title = title_tag.get_text(strip=True) if title_tag else "N/A"

                company_tag = card.find("span", class_="companyName")
                company = company_tag.get_text(strip=True) if company_tag else "N/A"

                location_tag = card.find("div", class_="companyLocation")
                location_text = (
                    location_tag.get_text(strip=True) if location_tag else "N/A"
                )

                # The link is often within the 'a' tag inside the jobTitle h2
                link_tag = title_tag.find("a") if title_tag else None
                job_link = (
                    "https://www.indeed.com" + link_tag.get("href")
                    if link_tag and link_tag.get("href")
                    else "N/A"
                )

                job_data.append(
                    {
                        "Title": title,
                        "Company": company,
                        "Location": location_text,
                        "Link": job_link,
                    }
                )

            # Be polite: Add a random delay between requests
            time.sleep(random.uniform(2, 5))

        except requests.exceptions.RequestException as e:
            print(f"Error fetching page: {e}")
            break
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            break

    return pd.DataFrame(job_data)
