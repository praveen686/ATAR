import pytest

from Modules.EDGAR import EdgarClient, EdgarAPIError


def test_api_error(edgar_client: EdgarClient):
    # Invalid CIK, so GET request will return a 404
    with pytest.raises(EdgarAPIError) as exc_info:
        edgar_client.get_submissions_by_company("0")

    assert "404 Client Error" in str(exc_info.value)


def test_cik_validation_error(edgar_client: EdgarClient):
    with pytest.raises(ValueError):
        # Too many digits
        edgar_client.get_submissions_by_company("0" * 11)

    with pytest.raises(ValueError):
        # Tickers are not supported
        edgar_client.get_submissions_by_company("AAPL")


def test_user_agent_validation_error(edgar_client: EdgarClient):
    with pytest.raises(ValueError):
        EdgarClient(user_agent=None)  # type: ignore

    with pytest.raises(ValueError):
        EdgarClient(user_agent="")
