"""Parameterized database query functions."""

from __future__ import annotations

from typing import Any

from src.db.client import get_supabase_client
from src.utils.errors import DatabaseError, NotFoundError
from src.validators.input_validator import SearchCompaniesInput, ScreenStocksInput


async def _resolve_ticker(ticker: str) -> dict[str, Any]:
    """Resolve a ticker symbol to a company record. Raises NotFoundError."""
    client = get_supabase_client()
    try:
        result = (
            client.table("companies").select("*").eq("ticker", ticker.upper()).execute()
        )
    except Exception as e:
        raise DatabaseError(f"Failed to look up ticker: {e}")

    if not result.data:
        raise NotFoundError(f"Company with ticker '{ticker.upper()}' not found")
    return result.data[0]


async def get_company_by_ticker_or_name(identifier: str) -> dict[str, Any]:
    """Look up a company by exact ticker match or partial name search."""
    client = get_supabase_client()
    try:
        # Try exact ticker match first
        result = (
            client.table("companies")
            .select("*")
            .eq("ticker", identifier.upper())
            .execute()
        )
        if result.data:
            return result.data[0]

        # Fall back to case-insensitive name search
        result = (
            client.table("companies")
            .select("*")
            .ilike("name", f"%{identifier}%")
            .execute()
        )
        if result.data:
            return result.data[0] if len(result.data) == 1 else result.data
    except Exception as e:
        raise DatabaseError(f"Company lookup failed: {e}")

    raise NotFoundError(f"No company found matching '{identifier}'")


async def search_companies(filters: SearchCompaniesInput) -> dict[str, Any]:
    """Search companies with dynamic filters and pagination."""
    client = get_supabase_client()
    try:
        query = client.table("companies").select("*", count="exact")

        if filters.sector:
            query = query.ilike("sector", f"%{filters.sector}%")
        if filters.industry:
            query = query.ilike("industry", f"%{filters.industry}%")
        if filters.min_market_cap is not None:
            query = query.gte("market_cap", filters.min_market_cap)
        if filters.max_market_cap is not None:
            query = query.lte("market_cap", filters.max_market_cap)
        if filters.country:
            query = query.ilike("country", f"%{filters.country}%")

        result = query.execute()
        return {"companies": result.data, "count": len(result.data)}
    except Exception as e:
        raise DatabaseError(f"Company search failed: {e}")


async def get_financial_reports(
    ticker: str,
    fiscal_year: int | None = None,
    fiscal_quarter: str | None = None,
) -> list[dict[str, Any]]:
    """Get financial reports for a company, optionally filtered by year/quarter."""
    company = await _resolve_ticker(ticker)
    client = get_supabase_client()
    try:
        query = (
            client.table("financial_reports")
            .select("*")
            .eq("company_id", company["id"])
            .order("fiscal_year", desc=True)
            .order("fiscal_quarter", desc=True)
        )

        if fiscal_year is not None:
            query = query.eq("fiscal_year", fiscal_year)
        if fiscal_quarter is not None:
            query = query.eq("fiscal_quarter", fiscal_quarter)

        result = query.execute()
        return result.data
    except NotFoundError:
        raise
    except Exception as e:
        raise DatabaseError(f"Failed to fetch financial reports: {e}")


async def get_financial_reports_for_companies(
    tickers: list[str],
    metrics: list[str],
) -> dict[str, Any]:
    """Fetch latest financial report for each ticker for side-by-side comparison."""
    comparisons: list[dict[str, Any]] = []

    for ticker in tickers:
        company = await _resolve_ticker(ticker)
        client = get_supabase_client()
        try:
            result = (
                client.table("financial_reports")
                .select("*")
                .eq("company_id", company["id"])
                .order("fiscal_year", desc=True)
                .order("fiscal_quarter", desc=True)
                .limit(1)
                .execute()
            )

            report = result.data[0] if result.data else {}
            entry: dict[str, Any] = {
                "ticker": ticker.upper(),
                "company_name": company["name"],
            }
            for metric in metrics:
                entry[metric] = report.get(metric)
            comparisons.append(entry)
        except NotFoundError:
            raise
        except Exception as e:
            raise DatabaseError(f"Failed to fetch data for {ticker}: {e}")

    return {"comparisons": comparisons, "metrics": metrics}


async def get_stock_prices(
    ticker: str,
    start_date: str | None = None,
    end_date: str | None = None,
    limit: int = 30,
) -> list[dict[str, Any]]:
    """Get stock price history for a company."""
    company = await _resolve_ticker(ticker)
    client = get_supabase_client()
    try:
        query = (
            client.table("stock_prices")
            .select("*")
            .eq("company_id", company["id"])
            .order("date", desc=True)
            .limit(limit)
        )

        if start_date:
            query = query.gte("date", start_date)
        if end_date:
            query = query.lte("date", end_date)

        result = query.execute()
        return result.data
    except NotFoundError:
        raise
    except Exception as e:
        raise DatabaseError(f"Failed to fetch stock prices: {e}")


async def get_analyst_ratings(
    ticker: str,
    firm: str | None = None,
) -> dict[str, Any]:
    """Get analyst ratings for a company with consensus summary."""
    company = await _resolve_ticker(ticker)
    client = get_supabase_client()
    try:
        query = (
            client.table("analyst_ratings")
            .select("*")
            .eq("company_id", company["id"])
            .order("rating_date", desc=True)
        )

        if firm:
            query = query.ilike("analyst_firm", f"%{firm}%")

        result = query.execute()
        ratings = result.data

        # Build consensus summary
        rating_counts: dict[str, int] = {}
        target_prices: list[float] = []
        for r in ratings:
            rating_val = r.get("rating", "Unknown")
            rating_counts[rating_val] = rating_counts.get(rating_val, 0) + 1
            if r.get("target_price") is not None:
                target_prices.append(float(r["target_price"]))

        consensus = {
            "total_ratings": len(ratings),
            "distribution": rating_counts,
            "avg_target_price": (
                round(sum(target_prices) / len(target_prices), 2)
                if target_prices
                else None
            ),
        }

        return {"ratings": ratings, "consensus": consensus}
    except NotFoundError:
        raise
    except Exception as e:
        raise DatabaseError(f"Failed to fetch analyst ratings: {e}")


async def screen_stocks(criteria: ScreenStocksInput) -> list[dict[str, Any]]:
    """Screen stocks by joining companies with their latest financial reports."""
    client = get_supabase_client()
    try:
        # Fetch all companies (optionally filtered by sector)
        company_query = client.table("companies").select("*")
        if criteria.sector:
            company_query = company_query.ilike("sector", f"%{criteria.sector}%")
        companies_result = company_query.execute()

        results: list[dict[str, Any]] = []
        for company in companies_result.data:
            # Get latest financial report for each company
            report_result = (
                client.table("financial_reports")
                .select("*")
                .eq("company_id", company["id"])
                .order("fiscal_year", desc=True)
                .order("fiscal_quarter", desc=True)
                .limit(1)
                .execute()
            )
            if not report_result.data:
                continue

            report = report_result.data[0]

            # Apply financial criteria filters
            if criteria.min_revenue is not None and (
                report.get("revenue") is None
                or float(report["revenue"]) < criteria.min_revenue
            ):
                continue
            if criteria.min_eps is not None and (
                report.get("eps") is None or float(report["eps"]) < criteria.min_eps
            ):
                continue
            if criteria.min_gross_margin is not None and (
                report.get("gross_margin") is None
                or float(report["gross_margin"]) < criteria.min_gross_margin
            ):
                continue
            if criteria.max_debt_to_equity is not None and (
                report.get("debt_to_equity") is None
                or float(report["debt_to_equity"]) > criteria.max_debt_to_equity
            ):
                continue

            results.append(
                {
                    "ticker": company["ticker"],
                    "name": company["name"],
                    "sector": company["sector"],
                    "market_cap": company["market_cap"],
                    "latest_report": {
                        "fiscal_year": report["fiscal_year"],
                        "fiscal_quarter": report["fiscal_quarter"],
                        "revenue": report.get("revenue"),
                        "net_income": report.get("net_income"),
                        "eps": report.get("eps"),
                        "gross_margin": report.get("gross_margin"),
                        "debt_to_equity": report.get("debt_to_equity"),
                    },
                }
            )

        return results
    except Exception as e:
        raise DatabaseError(f"Stock screening failed: {e}")


async def get_sector_overview(sector: str) -> dict[str, Any]:
    """Get aggregated sector overview with averages and company list."""
    client = get_supabase_client()
    try:
        companies_result = (
            client.table("companies")
            .select("*")
            .ilike("sector", f"%{sector}%")
            .execute()
        )

        if not companies_result.data:
            raise NotFoundError(f"No companies found in sector '{sector}'")

        companies = companies_result.data
        tickers = [c["ticker"] for c in companies]

        # Aggregate market caps
        market_caps = [c["market_cap"] for c in companies if c.get("market_cap")]
        avg_market_cap = (
            round(sum(market_caps) / len(market_caps), 2) if market_caps else None
        )

        # Get latest reports for margin averages
        margins: list[float] = []
        operating_margins: list[float] = []
        for company in companies:
            report_result = (
                client.table("financial_reports")
                .select("gross_margin, operating_margin")
                .eq("company_id", company["id"])
                .order("fiscal_year", desc=True)
                .order("fiscal_quarter", desc=True)
                .limit(1)
                .execute()
            )
            if report_result.data:
                r = report_result.data[0]
                if r.get("gross_margin") is not None:
                    margins.append(float(r["gross_margin"]))
                if r.get("operating_margin") is not None:
                    operating_margins.append(float(r["operating_margin"]))

        return {
            "sector": sector,
            "company_count": len(companies),
            "tickers": tickers,
            "avg_market_cap": avg_market_cap,
            "avg_gross_margin": (
                round(sum(margins) / len(margins), 2) if margins else None
            ),
            "avg_operating_margin": (
                round(sum(operating_margins) / len(operating_margins), 2)
                if operating_margins
                else None
            ),
        }
    except NotFoundError:
        raise
    except Exception as e:
        raise DatabaseError(f"Sector overview failed: {e}")
