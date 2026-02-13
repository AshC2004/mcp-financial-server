"""Tool handler tests with mocked Supabase responses."""

import json
from unittest.mock import MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
SAMPLE_COMPANY = {
    "id": "abc-123",
    "ticker": "AAPL",
    "name": "Apple Inc.",
    "sector": "Technology",
    "industry": "Consumer Electronics",
    "market_cap": 3200000000000,
    "country": "US",
    "founded_year": 1976,
    "ceo": "Tim Cook",
    "employees": 164000,
    "description": "Apple designs smartphones and computers.",
    "created_at": "2026-01-01T00:00:00Z",
}

SAMPLE_REPORT = {
    "id": "rpt-1",
    "company_id": "abc-123",
    "fiscal_year": 2024,
    "fiscal_quarter": "Q4",
    "revenue": "119000000000.00",
    "net_income": "33000000000.00",
    "eps": "2.18",
    "gross_margin": "46.20",
    "operating_margin": "33.50",
    "debt_to_equity": "1.500",
    "free_cash_flow": "28000000000.00",
    "report_date": "2024-10-31",
    "created_at": "2026-01-01T00:00:00Z",
}

SAMPLE_PRICE = {
    "id": "px-1",
    "company_id": "abc-123",
    "date": "2024-12-20",
    "open": "248.50",
    "high": "252.30",
    "low": "247.10",
    "close": "251.80",
    "volume": 45000000,
    "created_at": "2026-01-01T00:00:00Z",
}

SAMPLE_RATING = {
    "id": "rat-1",
    "company_id": "abc-123",
    "analyst_firm": "Goldman Sachs",
    "rating": "Buy",
    "target_price": "280.00",
    "previous_rating": "Hold",
    "rating_date": "2024-12-15",
    "created_at": "2026-01-01T00:00:00Z",
}


def make_mock_result(data):
    """Create a mock Supabase query result."""
    mock = MagicMock()
    mock.data = data
    mock.count = len(data) if data else 0
    return mock


def make_chainable_query(final_result):
    """Create a chainable mock that returns final_result on .execute()."""
    query = MagicMock()
    query.select.return_value = query
    query.eq.return_value = query
    query.ilike.return_value = query
    query.gte.return_value = query
    query.lte.return_value = query
    query.order.return_value = query
    query.limit.return_value = query
    query.execute.return_value = final_result
    return query


# ---------------------------------------------------------------------------
# Input validation tests
# ---------------------------------------------------------------------------
class TestInputValidation:
    """Test Pydantic input validation schemas."""

    def test_get_company_profile_empty_identifier(self):
        from src.validators.input_validator import GetCompanyProfileInput

        with pytest.raises(Exception):
            GetCompanyProfileInput(identifier="   ")

    def test_get_company_profile_valid(self):
        from src.validators.input_validator import GetCompanyProfileInput

        p = GetCompanyProfileInput(identifier="AAPL")
        assert p.identifier == "AAPL"

    def test_search_companies_no_filters(self):
        from src.validators.input_validator import SearchCompaniesInput

        p = SearchCompaniesInput()
        assert not p.has_any_filter()

    def test_search_companies_with_filter(self):
        from src.validators.input_validator import SearchCompaniesInput

        p = SearchCompaniesInput(sector="Technology")
        assert p.has_any_filter()

    def test_compare_companies_too_few(self):
        from src.validators.input_validator import CompareCompaniesInput

        with pytest.raises(Exception):
            CompareCompaniesInput(tickers=["AAPL"])

    def test_compare_companies_too_many(self):
        from src.validators.input_validator import CompareCompaniesInput

        with pytest.raises(Exception):
            CompareCompaniesInput(tickers=["A", "B", "C", "D", "E", "F"])

    def test_compare_companies_valid(self):
        from src.validators.input_validator import CompareCompaniesInput

        p = CompareCompaniesInput(tickers=["AAPL", "MSFT"])
        assert len(p.tickers) == 2

    def test_financial_report_invalid_quarter(self):
        from src.validators.input_validator import GetFinancialReportInput

        with pytest.raises(Exception):
            GetFinancialReportInput(ticker="AAPL", fiscal_quarter="Q5")

    def test_financial_report_valid_quarter(self):
        from src.validators.input_validator import GetFinancialReportInput

        p = GetFinancialReportInput(ticker="AAPL", fiscal_quarter="Q3")
        assert p.fiscal_quarter == "Q3"

    def test_stock_price_invalid_date(self):
        from src.validators.input_validator import GetStockPriceHistoryInput

        with pytest.raises(Exception):
            GetStockPriceHistoryInput(ticker="AAPL", start_date="not-a-date")

    def test_stock_price_valid(self):
        from src.validators.input_validator import GetStockPriceHistoryInput

        p = GetStockPriceHistoryInput(ticker="AAPL", start_date="2024-01-01", limit=10)
        assert p.limit == 10

    def test_screen_stocks_negative_margin(self):
        from src.validators.input_validator import ScreenStocksInput

        with pytest.raises(Exception):
            ScreenStocksInput(min_gross_margin=-5.0)

    def test_sector_overview_empty(self):
        from src.validators.input_validator import GetSectorOverviewInput

        with pytest.raises(Exception):
            GetSectorOverviewInput(sector="   ")


# ---------------------------------------------------------------------------
# Tool handler tests (mocked DB)
# ---------------------------------------------------------------------------
class TestGetCompanyProfile:
    """Test get_company_profile tool."""

    @pytest.mark.asyncio
    async def test_found_by_ticker(self):
        query = make_chainable_query(make_mock_result([SAMPLE_COMPANY]))
        mock_client = MagicMock()
        mock_client.table.return_value = query

        with patch("src.db.queries.get_supabase_client", return_value=mock_client):
            from src.server import get_company_profile

            result = await get_company_profile("AAPL")
            data = json.loads(result)
            assert data["status"] == "success"
            assert data["data"]["ticker"] == "AAPL"

    @pytest.mark.asyncio
    async def test_not_found(self):
        empty_query = make_chainable_query(make_mock_result([]))
        mock_client = MagicMock()
        mock_client.table.return_value = empty_query

        with patch("src.db.queries.get_supabase_client", return_value=mock_client):
            from src.server import get_company_profile

            result = await get_company_profile("ZZZZ")
            data = json.loads(result)
            assert data["status"] == "error"
            assert data["error"]["code"] == "NOT_FOUND"

    @pytest.mark.asyncio
    async def test_empty_identifier(self):
        from src.server import get_company_profile

        result = await get_company_profile("   ")
        data = json.loads(result)
        assert data["status"] == "error"
        assert data["error"]["code"] == "VALIDATION_ERROR"


class TestSearchCompanies:
    """Test search_companies tool."""

    @pytest.mark.asyncio
    async def test_no_filters(self):
        from src.server import search_companies

        result = await search_companies()
        data = json.loads(result)
        assert data["status"] == "error"
        assert "filter" in data["error"]["message"].lower()

    @pytest.mark.asyncio
    async def test_by_sector(self):
        query = make_chainable_query(make_mock_result([SAMPLE_COMPANY]))
        mock_client = MagicMock()
        mock_client.table.return_value = query

        with patch("src.db.queries.get_supabase_client", return_value=mock_client):
            from src.server import search_companies

            result = await search_companies(sector="Technology")
            data = json.loads(result)
            assert data["status"] == "success"
            assert data["data"]["count"] == 1


class TestGetFinancialReport:
    """Test get_financial_report tool."""

    @pytest.mark.asyncio
    async def test_valid_report(self):
        company_query = make_chainable_query(make_mock_result([SAMPLE_COMPANY]))
        report_query = make_chainable_query(make_mock_result([SAMPLE_REPORT]))
        mock_client = MagicMock()
        mock_client.table.side_effect = lambda t: (
            company_query if t == "companies" else report_query
        )

        with patch("src.db.queries.get_supabase_client", return_value=mock_client):
            from src.server import get_financial_report

            result = await get_financial_report("AAPL", fiscal_year=2024)
            data = json.loads(result)
            assert data["status"] == "success"
            assert len(data["data"]) == 1
            assert data["data"][0]["fiscal_year"] == 2024

    @pytest.mark.asyncio
    async def test_invalid_quarter(self):
        from src.server import get_financial_report

        result = await get_financial_report("AAPL", fiscal_quarter="Q9")
        data = json.loads(result)
        assert data["status"] == "error"
        assert data["error"]["code"] == "VALIDATION_ERROR"


class TestCompareCompanies:
    """Test compare_companies tool."""

    @pytest.mark.asyncio
    async def test_valid_comparison(self):
        company_query = make_chainable_query(make_mock_result([SAMPLE_COMPANY]))
        report_query = make_chainable_query(make_mock_result([SAMPLE_REPORT]))
        mock_client = MagicMock()
        mock_client.table.side_effect = lambda t: (
            company_query if t == "companies" else report_query
        )

        with patch("src.db.queries.get_supabase_client", return_value=mock_client):
            from src.server import compare_companies

            result = await compare_companies(["AAPL", "MSFT"])
            data = json.loads(result)
            assert data["status"] == "success"
            assert len(data["data"]["comparisons"]) == 2

    @pytest.mark.asyncio
    async def test_too_few_tickers(self):
        from src.server import compare_companies

        result = await compare_companies(["AAPL"])
        data = json.loads(result)
        assert data["status"] == "error"
        assert data["error"]["code"] == "VALIDATION_ERROR"


class TestGetStockPriceHistory:
    """Test get_stock_price_history tool."""

    @pytest.mark.asyncio
    async def test_valid_prices(self):
        company_query = make_chainable_query(make_mock_result([SAMPLE_COMPANY]))
        price_query = make_chainable_query(make_mock_result([SAMPLE_PRICE]))
        mock_client = MagicMock()
        mock_client.table.side_effect = lambda t: (
            company_query if t == "companies" else price_query
        )

        with patch("src.db.queries.get_supabase_client", return_value=mock_client):
            from src.server import get_stock_price_history

            result = await get_stock_price_history("AAPL", limit=5)
            data = json.loads(result)
            assert data["status"] == "success"
            assert len(data["data"]) == 1

    @pytest.mark.asyncio
    async def test_invalid_date_format(self):
        from src.server import get_stock_price_history

        result = await get_stock_price_history("AAPL", start_date="12/20/2024")
        data = json.loads(result)
        assert data["status"] == "error"
        assert data["error"]["code"] == "VALIDATION_ERROR"


class TestGetAnalystRatings:
    """Test get_analyst_ratings tool."""

    @pytest.mark.asyncio
    async def test_valid_ratings(self):
        company_query = make_chainable_query(make_mock_result([SAMPLE_COMPANY]))
        rating_query = make_chainable_query(make_mock_result([SAMPLE_RATING]))
        mock_client = MagicMock()
        mock_client.table.side_effect = lambda t: (
            company_query if t == "companies" else rating_query
        )

        with patch("src.db.queries.get_supabase_client", return_value=mock_client):
            from src.server import get_analyst_ratings

            result = await get_analyst_ratings("AAPL")
            data = json.loads(result)
            assert data["status"] == "success"
            assert data["data"]["consensus"]["total_ratings"] == 1
            assert data["data"]["consensus"]["avg_target_price"] == 280.0


class TestScreenStocks:
    """Test screen_stocks tool."""

    @pytest.mark.asyncio
    async def test_valid_screen(self):
        company_query = make_chainable_query(make_mock_result([SAMPLE_COMPANY]))
        report_query = make_chainable_query(make_mock_result([SAMPLE_REPORT]))
        mock_client = MagicMock()
        mock_client.table.side_effect = lambda t: (
            company_query if t == "companies" else report_query
        )

        with patch("src.db.queries.get_supabase_client", return_value=mock_client):
            from src.server import screen_stocks

            result = await screen_stocks(min_eps=1.0)
            data = json.loads(result)
            assert data["status"] == "success"

    @pytest.mark.asyncio
    async def test_negative_margin_validation(self):
        from src.server import screen_stocks

        result = await screen_stocks(min_gross_margin=-5.0)
        data = json.loads(result)
        assert data["status"] == "error"
        assert data["error"]["code"] == "VALIDATION_ERROR"


class TestGetSectorOverview:
    """Test get_sector_overview tool."""

    @pytest.mark.asyncio
    async def test_valid_sector(self):
        company_query = make_chainable_query(make_mock_result([SAMPLE_COMPANY]))
        report_query = make_chainable_query(
            make_mock_result([{"gross_margin": "46.20", "operating_margin": "33.50"}])
        )
        mock_client = MagicMock()
        mock_client.table.side_effect = lambda t: (
            company_query if t == "companies" else report_query
        )

        with patch("src.db.queries.get_supabase_client", return_value=mock_client):
            from src.server import get_sector_overview

            result = await get_sector_overview("Technology")
            data = json.loads(result)
            assert data["status"] == "success"
            assert data["data"]["company_count"] == 1
            assert data["data"]["tickers"] == ["AAPL"]

    @pytest.mark.asyncio
    async def test_empty_sector_name(self):
        from src.server import get_sector_overview

        result = await get_sector_overview("   ")
        data = json.loads(result)
        assert data["status"] == "error"
        assert data["error"]["code"] == "VALIDATION_ERROR"

    @pytest.mark.asyncio
    async def test_sector_not_found(self):
        query = make_chainable_query(make_mock_result([]))
        mock_client = MagicMock()
        mock_client.table.return_value = query

        with patch("src.db.queries.get_supabase_client", return_value=mock_client):
            from src.server import get_sector_overview

            result = await get_sector_overview("NonexistentSector")
            data = json.loads(result)
            assert data["status"] == "error"
            assert data["error"]["code"] == "NOT_FOUND"


# ---------------------------------------------------------------------------
# Formatter tests
# ---------------------------------------------------------------------------
class TestFormatters:
    """Test response formatting utilities."""

    def test_format_tool_result(self):
        from src.utils.formatters import format_tool_result

        result = json.loads(format_tool_result({"key": "value"}, "test_tool"))
        assert result["status"] == "success"
        assert result["data"]["key"] == "value"
        assert result["tool"] == "test_tool"

    def test_format_error_result(self):
        from src.utils.errors import NotFoundError
        from src.utils.formatters import format_error_result

        err = NotFoundError("Not found", {"id": "123"})
        result = json.loads(format_error_result(err))
        assert result["status"] == "error"
        assert result["error"]["code"] == "NOT_FOUND"
        assert result["error"]["details"]["id"] == "123"
