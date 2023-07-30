"""Unofficial SEC EDGAR API wrapper."""
import json
import os
import sys
from pathlib import Path
from typing import Optional, Union, List

from _BaseClient import BaseClient
from _constants import (
    BASE_URL_SUBMISSIONS, BASE_URL_XBRL_COMPANY_CONCEPTS, BASE_URL_XBRL_COMPANY_FACTS, BASE_URL_XBRL_FRAMES,
    SUPPORTED_FORMS, DEFAULT_AFTER_DATE, DEFAULT_BEFORE_DATE, ROOT_FACTS_SAVE_FOLDER_NAME, ROOT_FORMS_SAVE_FOLDER_NAME
)
from _orchestrator import fetch_and_save_filings, get_ticker_cik_name_mapping
from _types import FormsDownloadMetadata, DownloadPath, JSONType
from _utils import merge_submission_dicts, validate_and_return_cik, validate_and_parse_date


class EdgarClient(BaseClient):
    """An :class:`EdgarClient` object."""

    def __init__(
            self,
            company_name: str,
            email_address: str,
            download_folder: Optional[DownloadPath] = None,
    ):
        """
        Constructs an Edgar-Client object with user-agent and download folder.

        Args:
            company_name (str): The company name to use in the user-agent string.
            email_address (str): The email address to use in the user-agent string.
            download_folder (Optional[DownloadPath], default=None): The folder to download files to. If not specified, the current directory is used.
        """
        # TODO: add validation for email
        self.user_agent = f"{company_name} {email_address}"
        if not self.user_agent:  # todo - check company, email etc... are valid
            raise ValueError(
                "Please enter a valid user-agent string of the form "
                "'<Sample Company Name> <Sample Company Email>'. "
                "This is required by the SEC to identify your requests "
                "for rate-limiting purposes."
            )
        if download_folder is None:
            self.parent_download_folder = Path.cwd()
        elif isinstance(download_folder, Path):
            self.parent_download_folder = download_folder
        else:
            self.parent_download_folder = Path(download_folder).expanduser().resolve()

        self.supported_forms = SUPPORTED_FORMS
        self.facts_save_folder = self.parent_download_folder / ROOT_FACTS_SAVE_FOLDER_NAME
        self.forms_save_folder = self.parent_download_folder / ROOT_FORMS_SAVE_FOLDER_NAME
        self.ticker_to_cik_mapping, self.cik_to_ticker_mapping, self.cik_to_name = \
            get_ticker_cik_name_mapping(self.user_agent)

        super().__init__(self.user_agent)

    def get_submissions(self, ticker_or_cik: str, *, handle_pagination: bool = True) -> JSONType:
        """Get submissions for a specified CIK. Requests data from the
        data.sec.gov/submissions API endpoint. Full API documentation:
        https://www.sec.gov/edgar/sec-api-documentation.

        :param cik: CIK to obtain submissions for.
        :param handle_pagination: whether to automatically handle API pagination,
            defaults to True. By default, 1000 submissions are included and the
            response specified the next set of filenames to request to get the next
            batch of submissions (each page contains 1000 submissions). If this is
            set to True, requests to the paginated resources will be completed
            automatically and the results will be concatenated to the recent filings key.
            If a raw response is preferred for manual pagination handling, set this
            value to false.
        :return: JSON response from the data.sec.gov/submissions/ API endpoint
            for the specified CIK.
        """
        cik = validate_and_return_cik(ticker_or_cik, self.ticker_to_cik_mapping)
        api_endpoint = f"{BASE_URL_SUBMISSIONS}/CIK{cik}.json"
        submissions = self._rate_limited_get(api_endpoint)

        filings = submissions["filings"]
        paginated_submissions = filings["files"]

        # Handle pagination for a large number of requests
        if handle_pagination and paginated_submissions:
            to_merge = [filings["recent"]]
            for submission in paginated_submissions:
                filename = submission["name"]
                api_endpoint = f"{BASE_URL_SUBMISSIONS}/{filename}"
                resp = self._rate_limited_get(api_endpoint)
                to_merge.append(resp)

            # Merge all paginated submissions from files key into recent
            # and clear files list.
            filings["recent"] = merge_submission_dicts(to_merge)
            filings["files"] = []

        return submissions

    def get_company_concept(
            self,
            ticker_or_cik: str,
            taxonomy: str,
            tag: str,
    ) -> JSONType:
        """Get company concepts for a specified CIK. Requests data from the
        data.sec.gov/api/xbrl/companyconcept/ API endpoint. Returns all
        the XBRL disclosures for a single company (CIK) and concept (taxonomy and
        tag), with a separate array of facts for each unit of measure that the
        company has chosen to disclose (e.g. net profits reported in U.S. dollars
        and in Canadian dollars). Full API documentation:
        https://www.sec.gov/edgar/sec-api-documentation.

        :param cik: CIK to obtain company concepts for.
        :param taxonomy: reporting taxonomy (e.g. us-gaap, ifrs-full, dei, srt).
            More info: https://www.sec.gov/info/edgar/edgartaxonomies.shtml.
        :param tag: reporting tag (e.g. AccountsPayableCurrent).
        :return: JSON response from the data.sec.gov/api/xbrl/companyconcept/
            API endpoint for the specified CIK.
        """
        cik = validate_and_return_cik(ticker_or_cik, self.ticker_to_cik_mapping)

        api_endpoint = (
            f"{BASE_URL_XBRL_COMPANY_CONCEPTS}/CIK{cik}/{taxonomy}/{tag}.json"
        )
        return self._rate_limited_get(api_endpoint)

    def get_company_facts(self, ticker_or_cik: str) -> JSONType:
        """Get all company concepts for a specified CIK. Requests data from the
        data.sec.gov/api/xbrl/companyfacts/ API endpoint. Full API documentation:
        https://www.sec.gov/edgar/sec-api-documentation.

        :param cik: CIK to obtain company concepts for.
        :return: JSON response from the data.sec.gov/api/xbrl/companyfacts/
            API endpoint for the specified CIK.
        """
        cik = validate_and_return_cik(ticker_or_cik, self.ticker_to_cik_mapping)
        api_endpoint = f"{BASE_URL_XBRL_COMPANY_FACTS}/CIK{cik}.json"
        return self._rate_limited_get(api_endpoint)

    def get_frames(
            self,
            taxonomy: str,
            tag: str,
            unit: str,
            year: str,
            quarter: Union[int, str, None] = None,
            instantaneous: bool = True,
    ) -> JSONType:
        """Get all aggregated company facts for a specified taxonomy and tag in the specified
        calendar period. Requests data from the data.sec.gov/api/xbrl/frames/ API endpoint.
        Supports for annual, quarterly and instantaneous data. Example:
        us-gaap / AccountsPayableCurrent / USD / CY2019Q1I.
        Full API documentation: https://www.sec.gov/edgar/sec-api-documentation.

        :param taxonomy: reporting taxonomy (e.g. us-gaap, ifrs-full, dei, srt).
            More info: https://www.sec.gov/info/edgar/edgartaxonomies.shtml.
        :param tag: reporting tag (e.g. AccountsPayableCurrent).
        :param unit: unit of measure specified in the XBRL (e.g. USD).
        :param year: calendar period year.
        :param quarter: calendar period quarter, optional. Defaults to whole year.
        :param instantaneous: whether to request instantaneous data, defaults to True.
        :return: JSON response from the data.sec.gov/api/xbrl/frames/ API endpoint.
        """
        _quarter = (
            f"Q{quarter}" if quarter is not None and 1 <= int(quarter) <= 4 else ""
        )
        _instantaneous = "I" if instantaneous else ""
        period = f"CY{year}{_quarter}{_instantaneous}"
        api_endpoint = f"{BASE_URL_XBRL_FRAMES}/{taxonomy}/{tag}/{unit}/{period}.json"
        return self._rate_limited_get(api_endpoint)

    def download_form(
            self,
            ticker_or_cik: str,
            form_type: str,
            *,
            limit: Optional[int] = None,
            after: Optional[str] = None,
            before: Optional[str] = None,
            include_amends: bool = False,
            download_details: bool = True,
    ) -> int:
        """
        Fetches and saves SEC filings.

        Args:
            form_type (str): The form type to download.
            ticker_or_cik (str): The ticker or CIK to download filings for.
            limit (Optional[int], default=None): The maximum number of filings to download. If not specified, all available filings are downloaded.
            after (Optional[str], default=None): The earliest date for filings. If not specified, downloads filings available since 1994.
            before (Optional[str], default=None): The latest date for filings. If not specified, downloads filings up to today's date.
            include_amends (bool, default=False): Whether to include amended filings.
            download_details (bool, default=True): Whether to download filing details.

        Returns:
            int: The number of downloaded filings.

        Raises:
            ValueError: If the form is not supported, the limit is less than 1, or the after date is later than the before date.
        """
        # TODO: add validation and defaulting
        # TODO: can we rely on class default values rather than manually checking None?
        cik = validate_and_return_cik(ticker_or_cik, self.ticker_to_cik_mapping)

        if limit is None:
            # If amount is not specified, obtain all available filings.
            # We simply need a large number to denote this and the loop
            # responsible for fetching the URLs will break appropriately.
            limit = sys.maxsize
        else:
            limit = int(limit)
            if limit < 1:
                raise ValueError(
                    "Invalid amount. Please enter a number greater than 1."
                )

        # SEC allows for filing searches from 1994 onwards
        if after is None:
            after_date = DEFAULT_AFTER_DATE
        else:
            after_date = validate_and_parse_date(after)

            if after_date < DEFAULT_AFTER_DATE:
                after_date = DEFAULT_AFTER_DATE

        if before is None:
            before_date = DEFAULT_BEFORE_DATE
        else:
            before_date = validate_and_parse_date(before)

        if after_date > before_date:
            raise ValueError("After date cannot be greater than the before date.")

        if form_type not in SUPPORTED_FORMS:
            form_options = ", ".join(self.supported_forms)
            raise ValueError(
                f"{form_type!r} forms are not supported. "
                f"Please choose from the following: {form_options}."
            )

        ticker = self.cik_to_ticker_mapping.get(cik, None)

        num_downloaded = fetch_and_save_filings(
            FormsDownloadMetadata(
                self.parent_download_folder,
                form_type,
                cik,
                ticker,
                limit,
                after_date,
                before_date,
                include_amends,
                download_details,
            ),
            self.user_agent,
        )

        return num_downloaded

    def download_facts_for_companies(self, tickers_or_ciks: List[str], skip_if_exists=True):
        ticker_facts_saved = []
        ticker_facts_skipped = []

        root_facts_directory = Path(self.parent_download_folder, ROOT_FACTS_SAVE_FOLDER_NAME)
        root_facts_directory.mkdir(parents=True, exist_ok=True)

        for ticker_or_cik in tickers_or_ciks:
            try:
                cik = validate_and_return_cik(ticker_or_cik, self.ticker_to_cik_mapping)
                ticker_name = self.cik_to_ticker_mapping.get(cik)
                save_json_path = f'{root_facts_directory}/{ticker_name}-facts.json'
            except Exception as e:
                print(e)
                print(f"Skipping {ticker_or_cik} because it is not in the ticker to cik mapping")
                ticker_facts_skipped.append(ticker_or_cik)
                continue
            if skip_if_exists and os.path.exists(save_json_path):
                print(f"Skipping {ticker_name} because it already exists")
                continue
            try:
                values = self.get_company_facts(ticker_name)
            except Exception as e:
                print(f"Skipping {ticker_name}  while downloading facts because of error: {e}")
                ticker_facts_skipped.append(ticker_name)
                continue
            try:
                with open(save_json_path, 'w') as outfile:
                    json.dump(values, outfile)
                print(f"Saved {ticker_name} facts")
                ticker_facts_saved.append(ticker_name)
            except Exception as e:
                print(f"Skipping {ticker_name}  while saving facts because of error: {e}")
                ticker_facts_skipped.append(ticker_name)
                continue
        return ticker_facts_saved, ticker_facts_skipped

    def download_forms_for_companies(self,
                                     tickers_or_ciks: List[str], form_types: List[str],
                                     *,
                                     limit_per_form: Optional[int] = None,
                                     after: Optional[str] = None,
                                     before: Optional[str] = None,
                                     include_amends: bool = False,
                                     download_details: bool = True,
                                     ):

        forms_saved = []
        forms_skipped = []
        for ticker_or_cik in tickers_or_ciks:
            try:
                ticker_name = self.cik_to_ticker_mapping.get(
                    validate_and_return_cik(ticker_or_cik, self.ticker_to_cik_mapping))

                print(f"Downloading forms for {ticker_name}")
            except Exception as e:
                print(f"Skipping {ticker_or_cik} because it is not in the ticker to cik mapping: {e}")
                continue

            for filing_type in form_types:
                if filing_type not in self.supported_forms:
                    print(f"Skipping form {filing_type} for equity {ticker_name} because it is not supported")
                    continue
                try:
                    # todo check if already exists for given equity, form, and dates
                    n_saved_filings = self.download_form(ticker_name, filing_type,
                                                         after=after, before=before,
                                                         limit=limit_per_form, include_amends=include_amends,
                                                         download_details=download_details
                                                         )
                    print(f"Saved {n_saved_filings} filings for {ticker_name}-{filing_type}")
                    forms_saved.append(f'{ticker_name}-{filing_type}')
                except Exception as e:
                    print(f"Skipping form {filing_type} for ticker {ticker_name} during download because of error: {e}")
                    forms_skipped.append(f'{ticker_name}-{filing_type}')
                    continue


import feedparser
import time


def get_rss_feed_updates(feed_url):
    while True:
        # Fetch the RSS feed
        feed = feedparser.parse(feed_url)

        if not feed.entries:
            print("No entries found in the RSS feed.")
        else:
            # Display the latest update from the feed
            latest_entry = feed.entries[0]
            print("Latest update:")
            print("Title:", latest_entry.title)
            print("Published Date:", latest_entry.published)
            print("Summary:", latest_entry.summary)

        # Wait for some time before checking for updates again (e.g., every 5 minutes)
        time.sleep(300)  # 300 seconds = 5 minutes


if __name__ == "__main__":
    # Replace this URL with the RSS feed URL you want to subscribe to
    rss_feed_url = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent"
    get_rss_feed_updates(rss_feed_url)
    exit()

if __name__ == "__main__":
    DOWNLOAD_FOLDER = "/home/ruben/PycharmProjects/Genie-Trader/Data/raw_data/SEC"

    TICKERS_TO_ANALYZE = ['AAPL']

    # # Create an EdgarClient instance
    # edgar_client = EdgarClient(company_name="Carbonyl", email_address="ruben@carbonyl.org",
    #                            download_folder=DOWNLOAD_FOLDER)

    # get tickers from directory and filenames {ticker}-facts.json
    tickers = TICKERS_TO_ANALYZE or [f.replace('-facts.json', '') for f in
                                     os.listdir(f'{DOWNLOAD_FOLDER}/sec-edgar-facts') if
                                     f.endswith('-facts.json')]

    for ticker in tickers:
        # Parse the facts json for a company
        # with open(f'{edgar_client.facts_save_folder}/{ticker}-facts.json') as f:
        with open(f'{DOWNLOAD_FOLDER}/sec-edgar-facts/{ticker}-facts.json') as f:
            company_facts = json.load(f)

        # parse the company facts into a dataframe(s) for analysis
        print(f'Parsing {company_facts["entityName"]} facts')
        taxonomies = company_facts['facts']
        #             taxonomy: str,
        #             tag: str,
        #             unit: str,

        for taxonomy_name in taxonomies.keys():
            print(f'    Taxonomy {taxonomy_name}')
            for tag_name in taxonomies[taxonomy_name].keys():
                units = taxonomies[taxonomy_name][tag_name]["units"].keys()

                print(f'      Tag {tag_name}')
                print(f'        Label: {taxonomies[taxonomy_name][tag_name]["label"]}')
                print(f'        Description: {taxonomies[taxonomy_name][tag_name]["description"]}')
                print(f'        Units: {list(units)}')

                exit()
