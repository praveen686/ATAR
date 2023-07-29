



"""Unofficial SEC EDGAR API wrapper."""
import sys
from pathlib import Path
from typing import Optional, Union

from _BaseClient import BaseClient
from _constants import (
    BASE_URL_SUBMISSIONS, BASE_URL_XBRL_COMPANY_CONCEPTS, BASE_URL_XBRL_COMPANY_FACTS, BASE_URL_XBRL_FRAMES,
    SUPPORTED_FORMS, DEFAULT_AFTER_DATE, DEFAULT_BEFORE_DATE
)
from _orchestrator import fetch_and_save_filings, get_ticker_to_cik_mapping
from _types import DownloadMetadata, DownloadPath, JSONType
from _utils import merge_submission_dicts, validate_cik, validate_and_convert_ticker_or_cik, validate_and_parse_date


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
            self.download_folder = Path.cwd()
        elif isinstance(download_folder, Path):
            self.download_folder = download_folder
        else:
            self.download_folder = Path(download_folder).expanduser().resolve()

        self.ticker_to_cik_mapping = get_ticker_to_cik_mapping(self.user_agent)

        super().__init__(self.user_agent)

    def get_submissions(self, cik: str, *, handle_pagination: bool = True) -> JSONType:
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
        cik = validate_cik(cik)
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
            cik: str,
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
        cik = validate_cik(cik)
        api_endpoint = (
            f"{BASE_URL_XBRL_COMPANY_CONCEPTS}/CIK{cik}/{taxonomy}/{tag}.json"
        )
        return self._rate_limited_get(api_endpoint)

    def get_company_facts(self, cik: str) -> JSONType:
        """Get all company concepts for a specified CIK. Requests data from the
        data.sec.gov/api/xbrl/companyfacts/ API endpoint. Full API documentation:
        https://www.sec.gov/edgar/sec-api-documentation.

        :param cik: CIK to obtain company concepts for.
        :return: JSON response from the data.sec.gov/api/xbrl/companyfacts/
            API endpoint for the specified CIK.
        """
        cik = validate_cik(cik)
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

    def get(
            self,
            form: str,
            ticker_or_cik: str,
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
            form (str): The form type to download.
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
        cik = validate_and_convert_ticker_or_cik(
            ticker_or_cik, self.ticker_to_cik_mapping
        )

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

        if form not in SUPPORTED_FORMS:
            form_options = ", ".join(self.supported_forms)
            raise ValueError(
                f"{form!r} forms are not supported. "
                f"Please choose from the following: {form_options}."
            )

        num_downloaded = fetch_and_save_filings(
            DownloadMetadata(
                self.download_folder,
                form,
                cik,
                limit,
                after_date,
                before_date,
                include_amends,
                download_details,
            ),
            self.user_agent,
        )

        return num_downloaded


if __name__ == "__main__":
    edgar_client = EdgarClient(company_name="Carbonyl", email_address="ruben@carbonyl.org", download_folder=None)
    #
    # print(edgar_client.get_company_facts("0000320193"))
    print(edgar_client.get("10-Q", "AAPL", limit=None, after="2018-01-01", before="2024-01-01"))



