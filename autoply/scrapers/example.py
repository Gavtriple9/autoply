from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
from bs4 import BeautifulSoup
import random

# Path to geckodriver executable
GECKO_DRIVER = "/usr/local/bin/geckodriver"


def scrape_with_selenium(url):
    breakpoint()
    service = Service(executable_path=GECKO_DRIVER)
    options = webdriver.FirefoxOptions()
    # options.add_argument('--headless') # Run browser in background (no GUI)
    options.add_argument("--disable-gpu")  # Recommended for headless mode
    # Add other options as needed (e.g., user-agent)

    driver = webdriver.Firefox(service=service, options=options)
    driver.get(url)

    jobs = []

    try:
        # Give the page time to load its JavaScript content
        # Wait for a specific element to be present (e.g., a job listing container)
        # This is highly site-specific and requires inspecting the HTML
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CLASS_NAME, "jobs-search-results__list")
            )  # Example for LinkedIn
        )

        # Scroll down to load more jobs (LinkedIn/Glassdoor often load on scroll)
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.uniform(2, 4))  # Allow time for new content to load
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break  # Reached the bottom or no more content loaded
            last_height = new_height

        # Now parse the page source with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, "html.parser")

        # Example for LinkedIn: Find job listings. THIS IS A SIMPLIFIED EXAMPLE AND LIKELY WON'T WORK ROBUSTLY.
        # LinkedIn's structure is very complex and dynamic.
        job_listings = soup.find_all("li", class_="jobs-search-results__list-item")

        for job in job_listings:
            title_tag = job.find("h3", class_="base-search-card__title")
            company_tag = job.find("h4", class_="base-search-card__subtitle")
            location_tag = job.find("span", class_="job-search-card__location")
            link_tag = job.find("a", class_="base-card__full-link")

            jobs.append(
                {
                    "Title": title_tag.get_text(strip=True) if title_tag else "N/A",
                    "Company": (
                        company_tag.get_text(strip=True) if company_tag else "N/A"
                    ),
                    "Location": (
                        location_tag.get_text(strip=True) if location_tag else "N/A"
                    ),
                    "Link": link_tag.get("href") if link_tag else "N/A",
                }
            )

    except Exception as e:
        print(f"An error occurred during Selenium scraping: {e}")
    finally:
        driver.quit()  # Always close the browser

    return pd.DataFrame(jobs)
