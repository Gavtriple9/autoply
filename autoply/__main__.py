#!/usr/bin/env python3

from autoply import ROOT_LOGGER_NAME, JobScraper, Site, get_root_logger, get_parser

JOB_TITLE = "Entry Level Software Engineer"
LOCATION = "San Diego, CA"

import asyncio
import time
import random
from asynciolimiter import Limiter
from rnet import Impersonate, Client, Proxy, Response, HeaderMap
from os import getenv
from selectolax.parser import HTMLParser
from fake_useragent import UserAgent


def create_client() -> Client:
    """Create a new RNET client with impersonation and realistic headers."""
    # custom_proxy = getenv("CUSTOM_PROXY", None)
    # if custom_proxy:
    #     raise Exception("No proxy found")
    # proxies = [Proxy.http(custom_proxy), Proxy.https(custom_proxy)]
    proxies = None

    # Create client with Firefox impersonation
    ua = UserAgent()
    client = Client(
        impersonate=Impersonate.Firefox136, proxies=proxies, user_agent=ua.random
    )

    # Set realistic headers to avoid bot detection
    headers = HeaderMap(
        {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "DNT": "1",  # Do Not Track
            "Cache-Control": "max-age=0",
            "Pragma": "no-cache",
        }
    )

    # Add realistic headers
    client.update(headers=headers)

    return client


async def fetch_urls(
    client: Client, urls: list[str], limiter: Limiter
) -> list[Response]:
    """Fetch multiple URLs using the provided client and limiter with human-like delays."""
    responses = []

    for i, url in enumerate(urls):
        print(f"Fetching URL {i+1}/{len(urls)}: {url}")

        # Use the limiter to control rate
        await limiter.wait()

        try:
            response = await client.get(url)
            responses.append(response)
            print(f"Response status: {response.status_code}")

        except Exception as e:
            print(f"Error fetching {url}: {e}")
            continue

        # Add human-like delay between requests
        if i < len(urls) - 1:  # Don't delay after the last request
            delay = random.uniform(5, 12)  # Longer delays
            print(f"Waiting {delay:.1f} seconds before next request...")
            await asyncio.sleep(delay)

    return responses


async def async_main() -> None:
    """Main async function with improved bot detection avoidance."""
    # Much more conservative rate limiting: 1 request per 10 seconds
    limiter = Limiter(100 / 10)

    # Use a simpler URL without the specific job ID that might trigger detection
    urls = [
        "https://www.indeed.com/jobs?q=computer+science&l=San+Diego%2C+CA&from=searchOnHP%2Cwhatautocomplete%2CwhatautocompleteSourceStandard&vjk=2fd2849254466111"
        "https://www.glassdoor.com/Job/san-diego-ca-us-entry-level-software-engineer-jobs",
    ]

    client = create_client()

    try:
        # Fetch the job URLs
        responses = await fetch_urls(client, urls, limiter)

        for i, res in enumerate(responses):
            print(f"\n--- Response {i+1} ---")
            print(f"Status: {res.status_code}")

            if res.status_code == 200:
                response_text = await res.text()
                print(f"Response length: {len(response_text)} characters")
                print("✅ Successfully fetched page!")

            elif res.status_code == 403:
                print("❌ 403 Forbidden - Still being detected as bot")
                print(
                    "Try using residential proxies, VPN, or accessing from different IP"
                )
            else:
                print(f"❌ Unexpected status code: {res.status_code}")
                response_text = await res.text()
                print(f"Response preview: {response_text[:300]}...")

    except Exception as e:
        print(f"Error occurred: {e}")
        import traceback

        traceback.print_exc()


def main():
    """Entry point for the CLI script."""
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
