import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Union

from ._constants import DEFAULT_AFTER_DATE, DEFAULT_BEFORE_DATE


from typing import Any, Dict, List



@dataclass
class DownloadMetadata:
    """Class for representing internal download metadata."""

    download_folder: Path
    form: str
    cik: str
    limit: int = sys.maxsize
    after: date = DEFAULT_AFTER_DATE
    before: date = DEFAULT_BEFORE_DATE
    include_amends: bool = False
    download_details: bool = False


@dataclass
class ToDownload:
    raw_filing_uri: str
    primary_doc_uri: str
    accession_number: str
    details_doc_suffix: str


JSONType = Dict[str, Any]

SubmissionsType = Dict[str, List[str]]
DownloadPath = Union[str, Path]
