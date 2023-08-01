"""Unofficial SEC EDGAR API wrapper."""
import json
import os
import sys
import time
from pathlib import Path
from typing import Optional, Union, List

import feedparser
import requests

from Modules.EDGAR.client._DownloadFormManager import DownloadFormManager
from _BaseClient import BaseClient
from _constants import (
    BASE_URL_SUBMISSIONS, BASE_URL_XBRL_COMPANY_CONCEPTS, BASE_URL_XBRL_COMPANY_FACTS, BASE_URL_XBRL_FRAMES,
    SUPPORTED_FORMS, DEFAULT_AFTER_DATE, DEFAULT_BEFORE_DATE, ROOT_FACTS_SAVE_FOLDER_NAME, ROOT_FORMS_SAVE_FOLDER_NAME,
    HOST_WWW_SEC, STANDARD_HEADERS
)
from _types import FormsDownloadMetadata, DownloadPath, JSONType
from _utils import merge_submission_dicts, validate_and_return_cik, validate_and_parse_date
from logger import setup_logger

logger = setup_logger(name="EdgarClient")


class EdgarClient(BaseClient, DownloadFormManager):
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
        super().__init__(self.user_agent)

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
            self.get_ticker_cik_name_mapping()



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
        submissions = self._rate_limited_get(api_endpoint).json()

        filings = submissions["filings"]
        paginated_submissions = filings["files"]

        # Handle pagination for a large number of requests
        if handle_pagination and paginated_submissions:
            to_merge = [filings["recent"]]
            for submission in paginated_submissions:
                filename = submission["name"]
                api_endpoint = f"{BASE_URL_SUBMISSIONS}/{filename}"
                resp = self._rate_limited_get(api_endpoint).json()
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
        return self._rate_limited_get(BASE_URL_XBRL_COMPANY_CONCEPTS.format(
            cik=validate_and_return_cik(ticker_or_cik, self.ticker_to_cik_mapping),
            taxonomy=taxonomy,
            tag=tag,
        ))

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
        return self._rate_limited_get(api_endpoint).json()

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
        return self._rate_limited_get(api_endpoint).json()

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

        num_downloaded = self.fetch_and_save_filings(
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
            ) )

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
                logger.error(f"Skipping {ticker_or_cik} because of error: {e}")
                ticker_facts_skipped.append(ticker_or_cik)
                continue
            if skip_if_exists and os.path.exists(save_json_path):
                logger.info(f"Skipping {ticker_name} because it already exists")
                continue
            try:
                values = self.get_company_facts(ticker_name)
            except Exception as e:
                logger.error(f"Skipping {ticker_name}  while downloading facts because of error: {e}")
                ticker_facts_skipped.append(ticker_name)
                continue
            try:
                with open(save_json_path, 'w') as outfile:
                    json.dump(values, outfile)
                logger.info(f"Saved {ticker_name} facts")
                ticker_facts_saved.append(ticker_name)
            except Exception as e:
                logger.error(f"Skipping {ticker_name}  while saving facts because of error: {e}")
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

                logger.info(f"Downloading forms for {ticker_name}")
            except Exception as e:
                logger.error(f"Skipping {ticker_or_cik} because it is not in the ticker to cik mapping: {e}")
                continue

            for filing_type in form_types:
                if filing_type not in self.supported_forms:
                    logger.info(f"Skipping form {filing_type} for equity {ticker_name} because it is not supported")
                    continue
                try:
                    # todo check if already exists for given equity, form, and dates
                    n_saved_filings = self.download_form(ticker_name, filing_type,
                                                         after=after, before=before,
                                                         limit=limit_per_form, include_amends=include_amends,
                                                         download_details=download_details
                                                         )
                    logger.info(f"Saved {n_saved_filings} filings for {ticker_name}-{filing_type}")
                    forms_saved.append(f'{ticker_name}-{filing_type}')
                except Exception as e:
                    logger.error(
                        f"Skipping form {filing_type} for ticker {ticker_name} during download because of error: {e}")
                    forms_skipped.append(f'{ticker_name}-{filing_type}')
                    continue

    def subscribe_to_rss_feed(self, url, interval, callback_func=None):
        # todo if only_pass_entries_by_id is true the starting default value per id should also look back in the saved for the same id
        # todo allow to subscribe to specific form types or companies
        if callback_func is None:
            def _default_process_entry(entry):
                # Do something with the entry
                logger.info("Processing new entry:")
                for field, value in entry.items():
                    logger.info(f"{field}: {value}")
                logger.info("-------------")

            callback_func = _default_process_entry
        last_entry = None
        while True:
            try:

                # fixme this is essensially the same as in baseclient except the host
                response = requests.get(url, headers={
                    "User-Agent": self.user_agent,
                    "Host": HOST_WWW_SEC,
                    **STANDARD_HEADERS,
                })
                feed = feedparser.parse(response.content)
                # fixme ^^^^

                if not feed.entries:
                    logger.warning("No entries found in the RSS feed.")
                    time.sleep(interval)
                    continue
                new_entries = []
                for entry in feed.entries:
                    if last_entry is not None and entry.id == last_entry.id: break
                    new_entries.append(entry)
                if new_entries:
                    last_entry = new_entries[0]
                    for entry in new_entries:
                        callback_func(entry)
            except Exception as e:
                logger.error("Error:", e)
            finally:
                time.sleep(interval)


if __name__ == "__main__":
    DOWNLOAD_FOLDER = "/home/ruben/PycharmProjects/Genie-Trader/Data/raw_data/SEC"

    # Create an EdgarClient instance
    edgar_client = EdgarClient(company_name="Carbonyl LLC", email_address="ruben@carbonyl.org",
                               download_folder=DOWNLOAD_FOLDER)

    # # Download 1 10-K forms for Apple
    # edgar_client.download_form(ticker_or_cik='AAPL', form_type='10-K', limit=1)

    # rss_feed_url = f"https://{HOST_WWW_SEC}/cgi-bin/browse-edgar?action=getcurrent&type=&company=&dateb=&owner=include&start=0&output=atom&count=100"
    # edgar_client.subscribe_to_rss_feed(url=rss_feed_url, interval=5, callback_func=None)
    # exit()
    edgar_client.get_company_facts(ticker_or_cik='AAPL')

    # logger(edgar_client.get_company_concept(
    #     ticker_or_cik='AAPL',
    #     taxonomy='us-gaap',
    #     tag='AccountsPayableCurrent',
    #
    # ))

    exit()
    TICKERS_TO_ANALYZE = ['AAPL']

    # get tickers from directory and filenames {ticker}-facts.json
    tickers = TICKERS_TO_ANALYZE or [f.replace('-facts.json', '') for f in
                                     os.listdir(f'{DOWNLOAD_FOLDER}/sec-edgar-facts') if
                                     f.endswith('-facts.json')]

    # Initialize an empty DataFrame
    multi_df = pd.DataFrame()

    for ticker in tickers:
        with open(f'{DOWNLOAD_FOLDER}/sec-edgar-facts/{ticker}-facts.json') as f:
            company_facts = json.load(f)

        logger(f'Parsing {company_facts["entityName"]} facts')
        taxonomies = company_facts['facts']

        for taxonomy_name in taxonomies.keys():
            logger(f'    Taxonomy {taxonomy_name}')
            for tag_name in taxonomies[taxonomy_name].keys():
                units = taxonomies[taxonomy_name][tag_name]["units"].keys()

                logger(f'      Tag {tag_name}')
                # logger(f'        Label: {taxonomies[taxonomy_name][tag_name]["label"]}')
                # logger(f'        Description: {taxonomies[taxonomy_name][tag_name]["description"]}')
                # logger(f'        Units: {list(units)}')

                for unit in units:
                    # Create a DataFrame from the data list
                    events_df = pd.DataFrame(taxonomies[taxonomy_name][tag_name]["units"][unit])

                    logger(f'            Keys -> {list(events_df.keys())}')

                    # Add multi-index before concatenating to the main DataFrame
                    events_df.columns = pd.MultiIndex.from_product(
                        [[taxonomy_name], [tag_name], [unit], events_df.columns])

                    # Concatenate the data to the main DataFrame
                    multi_df = pd.concat([multi_df, events_df], axis=1)

    logger(multi_df.head())
