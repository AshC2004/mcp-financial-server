"""Input validation schemas for all 8 MCP tools."""

from pydantic import BaseModel, Field, field_validator


class GetCompanyProfileInput(BaseModel):
    """Input for get_company_profile tool."""

    identifier: str = Field(
        ..., description="Company ticker symbol or name to look up"
    )

    @field_validator("identifier")
    @classmethod
    def identifier_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("identifier must not be empty")
        return v.strip()


class SearchCompaniesInput(BaseModel):
    """Input for search_companies tool."""

    sector: str | None = Field(None, description="Filter by sector")
    industry: str | None = Field(None, description="Filter by industry")
    min_market_cap: int | None = Field(None, ge=0, description="Minimum market cap")
    max_market_cap: int | None = Field(None, ge=0, description="Maximum market cap")
    country: str | None = Field(None, description="Filter by country")

    @field_validator("sector", "industry", "country", mode="before")
    @classmethod
    def strip_strings(cls, v: str | None) -> str | None:
        return v.strip() if isinstance(v, str) else v

    def has_any_filter(self) -> bool:
        return any(
            v is not None
            for v in [
                self.sector,
                self.industry,
                self.min_market_cap,
                self.max_market_cap,
                self.country,
            ]
        )


class GetFinancialReportInput(BaseModel):
    """Input for get_financial_report tool."""

    ticker: str = Field(..., description="Company ticker symbol")
    fiscal_year: int | None = Field(None, ge=2000, le=2030, description="Fiscal year")
    fiscal_quarter: str | None = Field(
        None, pattern=r"^Q[1-4]$", description="Fiscal quarter (Q1-Q4)"
    )


class CompareCompaniesInput(BaseModel):
    """Input for compare_companies tool."""

    tickers: list[str] = Field(
        ..., min_length=2, max_length=5, description="2-5 ticker symbols to compare"
    )
    metrics: list[str] | None = Field(
        None,
        description="Metrics to compare (defaults to revenue, net_income, eps, gross_margin)",
    )


class GetStockPriceHistoryInput(BaseModel):
    """Input for get_stock_price_history tool."""

    ticker: str = Field(..., description="Company ticker symbol")
    start_date: str | None = Field(
        None, pattern=r"^\d{4}-\d{2}-\d{2}$", description="Start date (YYYY-MM-DD)"
    )
    end_date: str | None = Field(
        None, pattern=r"^\d{4}-\d{2}-\d{2}$", description="End date (YYYY-MM-DD)"
    )
    limit: int = Field(30, ge=1, le=365, description="Max number of records")


class GetAnalystRatingsInput(BaseModel):
    """Input for get_analyst_ratings tool."""

    ticker: str = Field(..., description="Company ticker symbol")
    firm: str | None = Field(None, description="Filter by analyst firm name")


class ScreenStocksInput(BaseModel):
    """Input for screen_stocks tool."""

    min_revenue: float | None = Field(None, ge=0, description="Minimum revenue")
    min_eps: float | None = Field(None, description="Minimum EPS")
    min_gross_margin: float | None = Field(
        None, ge=0, le=100, description="Minimum gross margin (%)"
    )
    max_debt_to_equity: float | None = Field(
        None, ge=0, description="Maximum debt-to-equity ratio"
    )
    sector: str | None = Field(None, description="Filter by sector")


class GetSectorOverviewInput(BaseModel):
    """Input for get_sector_overview tool."""

    sector: str = Field(..., description="Sector name to get overview for")

    @field_validator("sector")
    @classmethod
    def sector_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("sector must not be empty")
        return v.strip()
