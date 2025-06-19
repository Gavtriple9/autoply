#!/usr/bin/env python3
from autoply import scrape_with_selenium
from autoply import scrape_indeed_jobs


def main():
    print("Starting autoply...")
    indeed_url = (
        "https://www.indeed.com/jobs?q=entry+level+computer+engineer&l=San+Diego%2C+CA"
    )
    scrape_with_selenium(indeed_url)


if __name__ == "__main__":
    main()
