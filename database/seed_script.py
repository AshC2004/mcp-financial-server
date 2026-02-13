"""
Seed script for MCP Financial Server.

Generates and inserts dummy financial data into Supabase:
- 20 companies (real tickers with realistic metadata)
- 240 financial reports (4 quarters x 3 years x 20 companies)
- ~1,260 stock prices (90 calendar days x 20 companies, weekdays only)
- 60 analyst ratings (3 per company)

Usage:
    pip install supabase faker python-dotenv
    python database/seed_script.py

Requires .env with SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY.
"""

import os
import random
import json
import sys
from datetime import date, timedelta
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("ERROR: Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY in .env")
    sys.exit(1)

from supabase import create_client

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ---------------------------------------------------------------------------
# Company definitions (real companies with realistic metadata)
# ---------------------------------------------------------------------------

COMPANIES = [
    {
        "ticker": "AAPL", "name": "Apple Inc.", "sector": "Technology",
        "industry": "Consumer Electronics", "ceo": "Tim Cook",
        "employees": 164000, "founded_year": 1976,
        "market_cap": 3200000000000, "country": "US",
        "description": "Apple designs, manufactures, and markets smartphones, personal computers, tablets, wearables, and accessories worldwide.",
        "_base_price": 185.0, "_base_revenue": 95000,
    },
    {
        "ticker": "MSFT", "name": "Microsoft Corporation", "sector": "Technology",
        "industry": "Software—Infrastructure", "ceo": "Satya Nadella",
        "employees": 228000, "founded_year": 1975,
        "market_cap": 3100000000000, "country": "US",
        "description": "Microsoft develops and supports software, services, devices, and solutions worldwide.",
        "_base_price": 420.0, "_base_revenue": 62000,
    },
    {
        "ticker": "GOOGL", "name": "Alphabet Inc.", "sector": "Technology",
        "industry": "Internet Content & Information", "ceo": "Sundar Pichai",
        "employees": 182000, "founded_year": 1998,
        "market_cap": 2100000000000, "country": "US",
        "description": "Alphabet provides online advertising services through Google and various other technology products and platforms.",
        "_base_price": 175.0, "_base_revenue": 85000,
    },
    {
        "ticker": "AMZN", "name": "Amazon.com Inc.", "sector": "Consumer Cyclical",
        "industry": "Internet Retail", "ceo": "Andy Jassy",
        "employees": 1540000, "founded_year": 1994,
        "market_cap": 1900000000000, "country": "US",
        "description": "Amazon engages in the retail sale of consumer products, advertising, and subscription services through online and physical stores.",
        "_base_price": 185.0, "_base_revenue": 150000,
    },
    {
        "ticker": "NVDA", "name": "NVIDIA Corporation", "sector": "Technology",
        "industry": "Semiconductors", "ceo": "Jensen Huang",
        "employees": 29600, "founded_year": 1993,
        "market_cap": 3400000000000, "country": "US",
        "description": "NVIDIA provides graphics and compute & networking solutions in the United States, Taiwan, China, Hong Kong, and internationally.",
        "_base_price": 135.0, "_base_revenue": 30000,
    },
    {
        "ticker": "META", "name": "Meta Platforms Inc.", "sector": "Technology",
        "industry": "Internet Content & Information", "ceo": "Mark Zuckerberg",
        "employees": 67317, "founded_year": 2004,
        "market_cap": 1500000000000, "country": "US",
        "description": "Meta builds technologies that help people connect, find communities, and grow businesses through its family of apps and metaverse products.",
        "_base_price": 500.0, "_base_revenue": 40000,
    },
    {
        "ticker": "TSLA", "name": "Tesla Inc.", "sector": "Consumer Cyclical",
        "industry": "Auto Manufacturers", "ceo": "Elon Musk",
        "employees": 140473, "founded_year": 2003,
        "market_cap": 800000000000, "country": "US",
        "description": "Tesla designs, develops, manufactures, leases, and sells electric vehicles and energy generation and storage systems.",
        "_base_price": 250.0, "_base_revenue": 25000,
    },
    {
        "ticker": "JPM", "name": "JPMorgan Chase & Co.", "sector": "Financial Services",
        "industry": "Banks—Diversified", "ceo": "Jamie Dimon",
        "employees": 309926, "founded_year": 1799,
        "market_cap": 570000000000, "country": "US",
        "description": "JPMorgan Chase is a global financial services firm and one of the largest banking institutions in the United States.",
        "_base_price": 195.0, "_base_revenue": 40000,
    },
    {
        "ticker": "JNJ", "name": "Johnson & Johnson", "sector": "Healthcare",
        "industry": "Drug Manufacturers—General", "ceo": "Joaquin Duato",
        "employees": 131900, "founded_year": 1886,
        "market_cap": 390000000000, "country": "US",
        "description": "Johnson & Johnson researches, develops, manufactures, and sells various products in the healthcare field worldwide.",
        "_base_price": 155.0, "_base_revenue": 22000,
    },
    {
        "ticker": "V", "name": "Visa Inc.", "sector": "Financial Services",
        "industry": "Credit Services", "ceo": "Ryan McInerney",
        "employees": 30300, "founded_year": 1958,
        "market_cap": 580000000000, "country": "US",
        "description": "Visa operates as a payments technology company worldwide, facilitating digital payments among consumers, merchants, and financial institutions.",
        "_base_price": 280.0, "_base_revenue": 9000,
    },
    {
        "ticker": "PG", "name": "Procter & Gamble Co.", "sector": "Consumer Defensive",
        "industry": "Household & Personal Products", "ceo": "Jon Moeller",
        "employees": 107000, "founded_year": 1837,
        "market_cap": 370000000000, "country": "US",
        "description": "Procter & Gamble provides branded consumer packaged goods worldwide across beauty, grooming, health care, fabric and home care segments.",
        "_base_price": 160.0, "_base_revenue": 21000,
    },
    {
        "ticker": "UNH", "name": "UnitedHealth Group Inc.", "sector": "Healthcare",
        "industry": "Healthcare Plans", "ceo": "Andrew Witty",
        "employees": 400000, "founded_year": 1977,
        "market_cap": 480000000000, "country": "US",
        "description": "UnitedHealth Group operates as a diversified health care company in the United States through its Optum and UnitedHealthcare segments.",
        "_base_price": 520.0, "_base_revenue": 95000,
    },
    {
        "ticker": "HD", "name": "The Home Depot Inc.", "sector": "Consumer Cyclical",
        "industry": "Home Improvement Retail", "ceo": "Ted Decker",
        "employees": 471600, "founded_year": 1978,
        "market_cap": 370000000000, "country": "US",
        "description": "The Home Depot operates as a home improvement retailer selling building materials, home improvement products, and lawn and garden products.",
        "_base_price": 370.0, "_base_revenue": 40000,
    },
    {
        "ticker": "MA", "name": "Mastercard Incorporated", "sector": "Financial Services",
        "industry": "Credit Services", "ceo": "Michael Miebach",
        "employees": 33400, "founded_year": 1966,
        "market_cap": 430000000000, "country": "US",
        "description": "Mastercard is a global technology company in the payments industry connecting consumers, financial institutions, merchants, and governments.",
        "_base_price": 460.0, "_base_revenue": 6500,
    },
    {
        "ticker": "DIS", "name": "The Walt Disney Company", "sector": "Communication Services",
        "industry": "Entertainment", "ceo": "Bob Iger",
        "employees": 225000, "founded_year": 1923,
        "market_cap": 200000000000, "country": "US",
        "description": "The Walt Disney Company operates as an entertainment company worldwide through Disney Entertainment, ESPN, and Disney Experiences segments.",
        "_base_price": 110.0, "_base_revenue": 22000,
    },
    {
        "ticker": "NFLX", "name": "Netflix Inc.", "sector": "Communication Services",
        "industry": "Entertainment", "ceo": "Ted Sarandos",
        "employees": 13000, "founded_year": 1997,
        "market_cap": 310000000000, "country": "US",
        "description": "Netflix provides entertainment services and is one of the world's leading streaming entertainment services with paid memberships in over 190 countries.",
        "_base_price": 700.0, "_base_revenue": 9000,
    },
    {
        "ticker": "ADBE", "name": "Adobe Inc.", "sector": "Technology",
        "industry": "Software—Infrastructure", "ceo": "Shantanu Narayen",
        "employees": 29945, "founded_year": 1982,
        "market_cap": 240000000000, "country": "US",
        "description": "Adobe operates as a diversified software company worldwide, offering products and services for content creation, marketing, and document management.",
        "_base_price": 530.0, "_base_revenue": 5000,
    },
    {
        "ticker": "CRM", "name": "Salesforce Inc.", "sector": "Technology",
        "industry": "Software—Application", "ceo": "Marc Benioff",
        "employees": 79390, "founded_year": 1999,
        "market_cap": 280000000000, "country": "US",
        "description": "Salesforce provides customer relationship management technology that brings companies and customers together worldwide.",
        "_base_price": 290.0, "_base_revenue": 9000,
    },
    {
        "ticker": "INTC", "name": "Intel Corporation", "sector": "Technology",
        "industry": "Semiconductors", "ceo": "Pat Gelsinger",
        "employees": 124800, "founded_year": 1968,
        "market_cap": 120000000000, "country": "US",
        "description": "Intel designs, manufactures, and sells computer products and technologies worldwide, including processors, chipsets, and other semiconductor products.",
        "_base_price": 30.0, "_base_revenue": 14000,
    },
    {
        "ticker": "AMD", "name": "Advanced Micro Devices Inc.", "sector": "Technology",
        "industry": "Semiconductors", "ceo": "Lisa Su",
        "employees": 26000, "founded_year": 1969,
        "market_cap": 230000000000, "country": "US",
        "description": "AMD operates as a semiconductor company worldwide, offering x86 microprocessors, GPUs, and adaptive SoC products for data center, client, gaming, and embedded segments.",
        "_base_price": 145.0, "_base_revenue": 6500,
    },
]

ANALYST_FIRMS = [
    "Goldman Sachs", "Morgan Stanley", "JPMorgan", "Bank of America",
    "Citigroup", "Wells Fargo", "Barclays", "Deutsche Bank",
    "UBS", "Credit Suisse", "Jefferies", "Raymond James",
]

RATINGS = ["Strong Buy", "Buy", "Overweight", "Hold", "Underweight", "Sell"]
RATING_WEIGHTS = [15, 30, 20, 25, 7, 3]  # Weighted toward positive


def generate_financial_reports(company, company_id):
    """Generate 12 quarterly reports (2022-2024) for a company."""
    reports = []
    base_revenue = company["_base_revenue"]
    quarter_dates = {"Q1": "03-31", "Q2": "06-30", "Q3": "09-30", "Q4": "12-31"}

    for year in [2022, 2023, 2024]:
        # Year-over-year growth factor
        yoy_growth = 1.0 + random.uniform(-0.05, 0.15)
        yearly_revenue = base_revenue * yoy_growth

        for q in ["Q1", "Q2", "Q3", "Q4"]:
            # Quarterly variation
            q_factor = random.uniform(0.9, 1.1)
            revenue = round(yearly_revenue * q_factor / 4, 2)
            margin = random.uniform(0.08, 0.35)

            reports.append({
                "company_id": company_id,
                "fiscal_year": year,
                "fiscal_quarter": q,
                "revenue": revenue,
                "net_income": round(revenue * margin, 2),
                "eps": round(random.uniform(0.5, 8.0), 4),
                "gross_margin": round(random.uniform(30.0, 75.0), 2),
                "operating_margin": round(random.uniform(10.0, 45.0), 2),
                "debt_to_equity": round(random.uniform(0.1, 2.5), 3),
                "free_cash_flow": round(revenue * random.uniform(0.05, 0.25), 2),
                "report_date": f"{year}-{quarter_dates[q]}",
            })

        base_revenue = yearly_revenue  # compound growth

    return reports


def generate_stock_prices(company, company_id, days=90):
    """Generate daily stock prices for ~90 calendar days (weekdays only)."""
    prices = []
    base_price = company["_base_price"]
    start_date = date(2024, 10, 1)

    for i in range(days):
        d = start_date + timedelta(days=i)
        if d.weekday() >= 5:  # Skip weekends
            continue

        change = random.uniform(-0.03, 0.03)
        open_p = round(base_price * (1 + change), 2)
        high_p = round(open_p * (1 + random.uniform(0, 0.02)), 2)
        low_p = round(open_p * (1 - random.uniform(0, 0.02)), 2)
        close_p = round(random.uniform(low_p, high_p), 2)
        base_price = close_p

        prices.append({
            "company_id": company_id,
            "date": str(d),
            "open": open_p,
            "high": high_p,
            "low": low_p,
            "close": close_p,
            "volume": random.randint(5000000, 80000000),
        })

    return prices


def generate_analyst_ratings(company, company_id, count=3):
    """Generate analyst ratings from different firms."""
    firms = random.sample(ANALYST_FIRMS, count)
    ratings = []
    base_price = company["_base_price"]

    for firm in firms:
        rating = random.choices(RATINGS, weights=RATING_WEIGHTS, k=1)[0]
        prev_rating = random.choices(RATINGS, weights=RATING_WEIGHTS, k=1)[0]
        target = round(base_price * random.uniform(0.85, 1.35), 2)
        days_ago = random.randint(1, 180)
        rating_date = date(2024, 12, 31) - timedelta(days=days_ago)

        ratings.append({
            "company_id": company_id,
            "analyst_firm": firm,
            "rating": rating,
            "target_price": target,
            "previous_rating": prev_rating,
            "rating_date": str(rating_date),
        })

    return ratings


def insert_batch(table, rows, batch_size=100):
    """Insert rows in batches to avoid payload limits."""
    for i in range(0, len(rows), batch_size):
        batch = rows[i:i + batch_size]
        result = supabase.table(table).insert(batch).execute()
        print(f"  Inserted {len(batch)} rows into {table} (batch {i // batch_size + 1})")


def generate_seed_sql(companies_with_ids, all_reports, all_prices, all_ratings):
    """Generate seed.sql file as a backup."""
    lines = ["-- Auto-generated seed data\n-- Run after schema.sql\n"]

    for c, cid in companies_with_ids:
        cols = "id, ticker, name, sector, industry, market_cap, country, founded_year, ceo, employees, description"
        vals = f"'{cid}', '{c['ticker']}', '{c['name'].replace(chr(39), chr(39)+chr(39))}', '{c['sector']}', '{c['industry']}', {c['market_cap']}, '{c['country']}', {c['founded_year']}, '{c['ceo'].replace(chr(39), chr(39)+chr(39))}', {c['employees']}, '{c['description'].replace(chr(39), chr(39)+chr(39))}'"
        lines.append(f"INSERT INTO companies ({cols}) VALUES ({vals});")

    lines.append("")

    for r in all_reports:
        cols = "company_id, fiscal_year, fiscal_quarter, revenue, net_income, eps, gross_margin, operating_margin, debt_to_equity, free_cash_flow, report_date"
        vals = f"'{r['company_id']}', {r['fiscal_year']}, '{r['fiscal_quarter']}', {r['revenue']}, {r['net_income']}, {r['eps']}, {r['gross_margin']}, {r['operating_margin']}, {r['debt_to_equity']}, {r['free_cash_flow']}, '{r['report_date']}'"
        lines.append(f"INSERT INTO financial_reports ({cols}) VALUES ({vals});")

    lines.append("")

    for p in all_prices:
        cols = "company_id, date, open, high, low, close, volume"
        vals = f"'{p['company_id']}', '{p['date']}', {p['open']}, {p['high']}, {p['low']}, {p['close']}, {p['volume']}"
        lines.append(f"INSERT INTO stock_prices ({cols}) VALUES ({vals});")

    lines.append("")

    for a in all_ratings:
        cols = "company_id, analyst_firm, rating, target_price, previous_rating, rating_date"
        vals = f"'{a['company_id']}', '{a['analyst_firm']}', '{a['rating']}', {a['target_price']}, '{a['previous_rating']}', '{a['rating_date']}'"
        lines.append(f"INSERT INTO analyst_ratings ({cols}) VALUES ({vals});")

    sql_path = os.path.join(os.path.dirname(__file__), "seed.sql")
    with open(sql_path, "w") as f:
        f.write("\n".join(lines))
    print(f"\nGenerated {sql_path} with {len(lines)} statements")


def main():
    print("=== MCP Financial Server — Seed Script ===\n")

    # Step 1: Insert companies
    print("Inserting companies...")
    company_rows = []
    for c in COMPANIES:
        row = {k: v for k, v in c.items() if not k.startswith("_")}
        company_rows.append(row)

    result = supabase.table("companies").insert(company_rows).execute()
    inserted_companies = result.data
    print(f"  Inserted {len(inserted_companies)} companies")

    # Build ticker → id mapping
    ticker_to_id = {c["ticker"]: c["id"] for c in inserted_companies}
    companies_with_ids = []
    for c in COMPANIES:
        cid = ticker_to_id[c["ticker"]]
        companies_with_ids.append((c, cid))

    # Step 2: Generate and insert financial reports
    print("\nGenerating financial reports...")
    all_reports = []
    for c, cid in companies_with_ids:
        all_reports.extend(generate_financial_reports(c, cid))
    print(f"  Generated {len(all_reports)} reports")
    insert_batch("financial_reports", all_reports)

    # Step 3: Generate and insert stock prices
    print("\nGenerating stock prices...")
    all_prices = []
    for c, cid in companies_with_ids:
        all_prices.extend(generate_stock_prices(c, cid))
    print(f"  Generated {len(all_prices)} price records")
    insert_batch("stock_prices", all_prices)

    # Step 4: Generate and insert analyst ratings
    print("\nGenerating analyst ratings...")
    all_ratings = []
    for c, cid in companies_with_ids:
        all_ratings.extend(generate_analyst_ratings(c, cid))
    print(f"  Generated {len(all_ratings)} ratings")
    insert_batch("analyst_ratings", all_ratings)

    # Step 5: Generate seed.sql backup
    print("\nGenerating seed.sql backup...")
    generate_seed_sql(companies_with_ids, all_reports, all_prices, all_ratings)

    print("\n=== Seeding complete! ===")
    print(f"  Companies:         {len(inserted_companies)}")
    print(f"  Financial Reports: {len(all_reports)}")
    print(f"  Stock Prices:      {len(all_prices)}")
    print(f"  Analyst Ratings:   {len(all_ratings)}")


if __name__ == "__main__":
    main()
