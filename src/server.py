"""MCP Financial Server — Entry point."""

from __future__ import annotations

import sys
from typing import Any

from mcp.server.fastmcp import FastMCP

from src.utils.errors import ToolError, ValidationError
from src.utils.formatters import format_error_result

mcp = FastMCP(
    "Financial Data Server",
    instructions="MCP server providing financial data tools — company profiles, financial reports, stock prices, analyst ratings, screening, and sector overviews.",
)


# ---------------------------------------------------------------------------
# Tool: get_company_profile
# ---------------------------------------------------------------------------
@mcp.tool(
    name="get_company_profile",
    description="Look up a company by ticker symbol or name. Returns full company profile including sector, market cap, CEO, and more.",
)
async def get_company_profile(identifier: str) -> str:
    """Look up a company by ticker or name."""
    from src.validators.input_validator import GetCompanyProfileInput

    try:
        params = GetCompanyProfileInput(identifier=identifier)
    except Exception as e:
        return format_error_result(ValidationError(str(e)))

    try:
        from src.db.queries import get_company_by_ticker_or_name

        result = await get_company_by_ticker_or_name(params.identifier)
        from src.utils.formatters import format_tool_result

        return format_tool_result(result, "get_company_profile")
    except ToolError as e:
        return format_error_result(e)


# ---------------------------------------------------------------------------
# Tool: search_companies
# ---------------------------------------------------------------------------
@mcp.tool(
    name="search_companies",
    description="Search companies by sector, industry, market cap range, or country. At least one filter required.",
)
async def search_companies(
    sector: str | None = None,
    industry: str | None = None,
    min_market_cap: int | None = None,
    max_market_cap: int | None = None,
    country: str | None = None,
) -> str:
    """Search companies with filters."""
    from src.validators.input_validator import SearchCompaniesInput

    try:
        params = SearchCompaniesInput(
            sector=sector,
            industry=industry,
            min_market_cap=min_market_cap,
            max_market_cap=max_market_cap,
            country=country,
        )
        if not params.has_any_filter():
            return format_error_result(
                ValidationError("At least one search filter is required")
            )
    except Exception as e:
        return format_error_result(ValidationError(str(e)))

    try:
        from src.db.queries import search_companies as db_search

        result = await db_search(params)
        from src.utils.formatters import format_tool_result

        return format_tool_result(result, "search_companies")
    except ToolError as e:
        return format_error_result(e)


# ---------------------------------------------------------------------------
# Tool: get_financial_report
# ---------------------------------------------------------------------------
@mcp.tool(
    name="get_financial_report",
    description="Get financial reports for a company by ticker. Optionally filter by fiscal year and/or quarter.",
)
async def get_financial_report(
    ticker: str,
    fiscal_year: int | None = None,
    fiscal_quarter: str | None = None,
) -> str:
    """Get financial reports for a company."""
    from src.validators.input_validator import GetFinancialReportInput

    try:
        params = GetFinancialReportInput(
            ticker=ticker, fiscal_year=fiscal_year, fiscal_quarter=fiscal_quarter
        )
    except Exception as e:
        return format_error_result(ValidationError(str(e)))

    try:
        from src.db.queries import get_financial_reports

        result = await get_financial_reports(params.ticker, params.fiscal_year, params.fiscal_quarter)
        from src.utils.formatters import format_tool_result

        return format_tool_result(result, "get_financial_report")
    except ToolError as e:
        return format_error_result(e)


# ---------------------------------------------------------------------------
# Tool: compare_companies
# ---------------------------------------------------------------------------
@mcp.tool(
    name="compare_companies",
    description="Compare 2-5 companies side by side on financial metrics. Default metrics: revenue, net_income, eps, gross_margin.",
)
async def compare_companies(
    tickers: list[str],
    metrics: list[str] | None = None,
) -> str:
    """Compare multiple companies on financial metrics."""
    from src.validators.input_validator import CompareCompaniesInput

    try:
        params = CompareCompaniesInput(tickers=tickers, metrics=metrics)
    except Exception as e:
        return format_error_result(ValidationError(str(e)))

    try:
        from src.db.queries import get_financial_reports_for_companies

        result = await get_financial_reports_for_companies(
            params.tickers,
            params.metrics or ["revenue", "net_income", "eps", "gross_margin"],
        )
        from src.utils.formatters import format_tool_result

        return format_tool_result(result, "compare_companies")
    except ToolError as e:
        return format_error_result(e)


# ---------------------------------------------------------------------------
# Tool: get_stock_price_history
# ---------------------------------------------------------------------------
@mcp.tool(
    name="get_stock_price_history",
    description="Get historical stock prices for a company. Returns daily OHLCV data, most recent first.",
)
async def get_stock_price_history(
    ticker: str,
    start_date: str | None = None,
    end_date: str | None = None,
    limit: int = 30,
) -> str:
    """Get stock price history."""
    from src.validators.input_validator import GetStockPriceHistoryInput

    try:
        params = GetStockPriceHistoryInput(
            ticker=ticker, start_date=start_date, end_date=end_date, limit=limit
        )
    except Exception as e:
        return format_error_result(ValidationError(str(e)))

    try:
        from src.db.queries import get_stock_prices

        result = await get_stock_prices(
            params.ticker, params.start_date, params.end_date, params.limit
        )
        from src.utils.formatters import format_tool_result

        return format_tool_result(result, "get_stock_price_history")
    except ToolError as e:
        return format_error_result(e)


# ---------------------------------------------------------------------------
# Tool: get_analyst_ratings
# ---------------------------------------------------------------------------
@mcp.tool(
    name="get_analyst_ratings",
    description="Get analyst ratings and price targets for a company. Optionally filter by analyst firm. Includes consensus summary.",
)
async def get_analyst_ratings(
    ticker: str,
    firm: str | None = None,
) -> str:
    """Get analyst ratings for a company."""
    from src.validators.input_validator import GetAnalystRatingsInput

    try:
        params = GetAnalystRatingsInput(ticker=ticker, firm=firm)
    except Exception as e:
        return format_error_result(ValidationError(str(e)))

    try:
        from src.db.queries import get_analyst_ratings as db_ratings

        result = await db_ratings(params.ticker, params.firm)
        from src.utils.formatters import format_tool_result

        return format_tool_result(result, "get_analyst_ratings")
    except ToolError as e:
        return format_error_result(e)


# ---------------------------------------------------------------------------
# Tool: screen_stocks
# ---------------------------------------------------------------------------
@mcp.tool(
    name="screen_stocks",
    description="Screen stocks by financial criteria: minimum revenue, EPS, gross margin, maximum debt-to-equity, and sector.",
)
async def screen_stocks(
    min_revenue: float | None = None,
    min_eps: float | None = None,
    min_gross_margin: float | None = None,
    max_debt_to_equity: float | None = None,
    sector: str | None = None,
) -> str:
    """Screen stocks by financial criteria."""
    from src.validators.input_validator import ScreenStocksInput

    try:
        params = ScreenStocksInput(
            min_revenue=min_revenue,
            min_eps=min_eps,
            min_gross_margin=min_gross_margin,
            max_debt_to_equity=max_debt_to_equity,
            sector=sector,
        )
    except Exception as e:
        return format_error_result(ValidationError(str(e)))

    try:
        from src.db.queries import screen_stocks as db_screen

        result = await db_screen(params)
        from src.utils.formatters import format_tool_result

        return format_tool_result(result, "screen_stocks")
    except ToolError as e:
        return format_error_result(e)


# ---------------------------------------------------------------------------
# Tool: get_sector_overview
# ---------------------------------------------------------------------------
@mcp.tool(
    name="get_sector_overview",
    description="Get an overview of a market sector including average metrics, company count, and list of tickers.",
)
async def get_sector_overview(sector: str) -> str:
    """Get sector-level aggregated overview."""
    from src.validators.input_validator import GetSectorOverviewInput

    try:
        params = GetSectorOverviewInput(sector=sector)
    except Exception as e:
        return format_error_result(ValidationError(str(e)))

    try:
        from src.db.queries import get_sector_overview as db_sector

        result = await db_sector(params.sector)
        from src.utils.formatters import format_tool_result

        return format_tool_result(result, "get_sector_overview")
    except ToolError as e:
        return format_error_result(e)


# ---------------------------------------------------------------------------
# MCP Resources
# ---------------------------------------------------------------------------
@mcp.resource(
    "financial://companies",
    name="All Companies",
    description="List of all companies in the financial database with basic info.",
    mime_type="application/json",
)
async def list_companies_resource() -> str:
    """Return all companies as a resource."""
    import json

    from src.db.client import get_supabase_client

    client = get_supabase_client()
    result = client.table("companies").select("ticker, name, sector, market_cap").order("ticker").execute()
    return json.dumps(result.data, default=str)


@mcp.resource(
    "financial://company/{ticker}",
    name="Company Detail",
    description="Full profile and latest financials for a specific company by ticker.",
    mime_type="application/json",
)
async def company_detail_resource(ticker: str) -> str:
    """Return detailed company data as a resource."""
    import json

    from src.db.client import get_supabase_client

    client = get_supabase_client()
    company = client.table("companies").select("*").eq("ticker", ticker.upper()).execute()
    if not company.data:
        return json.dumps({"error": f"Company {ticker} not found"})

    report = (
        client.table("financial_reports")
        .select("*")
        .eq("company_id", company.data[0]["id"])
        .order("fiscal_year", desc=True)
        .order("fiscal_quarter", desc=True)
        .limit(1)
        .execute()
    )

    return json.dumps(
        {
            "company": company.data[0],
            "latest_report": report.data[0] if report.data else None,
        },
        default=str,
    )


# ---------------------------------------------------------------------------
# MCP Prompt Templates
# ---------------------------------------------------------------------------
@mcp.prompt(
    name="analyze_company",
    description="Generate a comprehensive analysis prompt for a given company ticker.",
)
async def analyze_company_prompt(ticker: str) -> str:
    """Prompt template: Analyze a company."""
    return (
        f"Please provide a comprehensive analysis of {ticker.upper()} including:\n"
        f"1. Company profile and business overview\n"
        f"2. Recent financial performance (revenue, earnings, margins)\n"
        f"3. Stock price trends\n"
        f"4. Analyst ratings and consensus target price\n"
        f"5. Key strengths and risks\n\n"
        f"Use the available financial data tools to gather the information."
    )


@mcp.prompt(
    name="compare_companies",
    description="Generate a comparison prompt for two companies.",
)
async def compare_companies_prompt(ticker1: str, ticker2: str) -> str:
    """Prompt template: Compare two companies."""
    return (
        f"Please compare {ticker1.upper()} and {ticker2.upper()} on the following dimensions:\n"
        f"1. Company profiles (sector, size, market cap)\n"
        f"2. Financial metrics (revenue, net income, EPS, margins)\n"
        f"3. Recent stock price performance\n"
        f"4. Analyst sentiment and target prices\n"
        f"5. Which company appears to be the stronger investment and why?\n\n"
        f"Use the available financial data tools to gather the information."
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main():
    """Run the MCP server."""
    transport = "stdio"
    if len(sys.argv) > 1 and sys.argv[1] == "--sse":
        transport = "sse"
    mcp.run(transport=transport)


if __name__ == "__main__":
    main()
