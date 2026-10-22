"""Bounded, retrying HTTPS requests for read-only registry scrapers."""
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def fetch_text(url, headers=None):
    retry = Retry(total=3, backoff_factor=1, status_forcelist=(429, 500, 502, 503, 504),
                  allowed_methods={"GET"}, respect_retry_after_header=False)
    with requests.Session() as session:
        session.mount("https://", HTTPAdapter(max_retries=retry))
        response = session.get(url, headers=headers, timeout=(10, 30))
        response.raise_for_status()
        return response.text
