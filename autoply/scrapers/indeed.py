from typing import List
from logging import Logger
import undetected_chromedriver as uc
from selenium import webdriver
from selenium_stealth import stealth
import time

# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.common.by import By
# import pandas as pd
# from bs4 import BeautifulSoup


def scrape_indeed(job: str, location: str, logger: Logger) -> List[dict]:
    """
    Scrape job listings from Indeed based on the provided job title and location.

    Args:
        job (str): The job title to search for.
        location (str): The location to search in.
        logger (Logger): A logger instance for logging.

    Returns:
        list[dict]: A list of dictionaries containing job details.
    """
    # cService = webdriver.ChromeService(
    #     executable_path="/Users/groberts/Developer/gitrepos/personal/autoply/chromedriver"
    # )
    # driver = uc.Chrome(headless=False, use_subprocess=False)
    #
    # driver.get(f"https://secure.indeed.com/auth")
    # players = driver.find_elements(By.XPATH, '//td[@class="name"]')

    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')

    # Set up WebDriver
    driver = uc.Chrome(options=options)
    stealth(
        driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
    )

    # Open a webpage
    driver.set_window_size(1620, 1280)
    driver.get(f"https://secure.indeed.com/auth")

    # driver.get(f"https://indeed.com/jobs")
    print(driver.title)

    time.sleep(100)  # Wait for the page to load
    driver.quit()
