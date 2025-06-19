import os

THIS_FILE = os.path.abspath(__file__)
ROOT_DIR = os.path.dirname(os.path.dirname(THIS_FILE))
ROOT_LOGGER_NAME = __name__.lower()

from autoply.scrapers.example import scrape_with_selenium
from autoply.scrapers.indeed import scrape_indeed_jobs
from autoply.logger import get_root_logger
from autoply.parser import get_parser
