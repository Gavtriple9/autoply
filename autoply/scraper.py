from abc import ABC
from enum import Enum, auto
from logging import Logger
from typing import List

from autoply.scrapers.indeed import scrape_indeed


class DefaultLogger(ABC):
    def __init__(self, logger: Logger = None):
        """
        Initialize the logger.
        :param logger: Optional custom logger
        """
        self._logger = logger

    def _debug(self, text: str):
        """
        Log debug information.
        """
        if self._logger is not None:
            self._logger.debug(text)
        else:
            print("[DEBUG]: ", text)

    def _info(self, text: str):
        """
        Log information.
        """
        if self._logger is not None:
            self._logger.info(text)
        else:
            print("[INFO]: ", text)

    def _warning(self, text: str):
        """
        Log warning information.
        """
        if self._logger is not None:
            self._logger.warning(text)
        else:
            print("[WARNING]: ", text)

    def _error(self, text: str):
        """0
        Log error information.
        """
        if self._logger is not None:
            self._logger.error(text)
        else:
            print("[ERROR]: ", text)

    def _critical(self, text: str):
        """
        Log critical information.
        """
        if self._logger is not None:
            self._logger.critical(text)
        else:
            print("[CRITICAL]: ", text)


class Site(Enum):
    INDEED = auto()
    GLASSDOOR = auto()
    YCOMBINATOR = auto()


class Job:
    def __init__(
        self, title: str, company: str, location: str, link: str, description: str
    ):
        self.title = title
        self.company = company
        self.location = location
        self.link = link
        self.description = description

    def __repr__(self):
        return f"Job(title={self.title}, company={self.company}, location={self.location}, link={self.link})"


class JobScraper(DefaultLogger):
    def __init__(self, logger: Logger):
        self.job: str = None
        self.location: str = None
        super().__init__(logger)

    def set_job(self, job: str):
        self.job = job

    def set_location(self, location: str):
        self.location = location

    def scrape(self, site: Site) -> List[Job]:
        if site is None:
            self._error("site is not set.")
            return []
        if self.job is None:
            self._error("Job is not set.")
            return []
        if self.location is None:
            self._error("Location is not set.")
            return []

        match site:
            case Site.INDEED:
                jobs_data = scrape_indeed(self.job, self.location, self._logger)

            # case Site.YCOMBINATOR:
            #     jobs_data = scrape_ycombinator(self.job, self.location, self._logger)

            case default:
                self._error(f"Unsupported site: {site}")
                return []

        if not jobs_data:
            self._warning(
                f"No jobs found for '{self.job}' in '{self.location}' on '{site.name}'."
            )
            return []

        jobs = [Job(**job) for job in jobs_data]
        return jobs
