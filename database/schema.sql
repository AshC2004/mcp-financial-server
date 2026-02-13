-- MCP Financial Server — Database Schema
-- Run this in Supabase SQL Editor

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Companies table
CREATE TABLE companies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ticker VARCHAR(10) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    sector VARCHAR(100),
    industry VARCHAR(100),
    market_cap BIGINT,
    country VARCHAR(50),
    founded_year INT,
    ceo VARCHAR(255),
    employees INT,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_companies_ticker ON companies(ticker);
CREATE INDEX idx_companies_sector ON companies(sector);
CREATE INDEX idx_companies_country ON companies(country);

-- Financial reports table
CREATE TABLE financial_reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    fiscal_year INT NOT NULL,
    fiscal_quarter VARCHAR(5) NOT NULL,
    revenue NUMERIC(15,2),
    net_income NUMERIC(15,2),
    eps NUMERIC(8,4),
    gross_margin NUMERIC(5,2),
    operating_margin NUMERIC(5,2),
    debt_to_equity NUMERIC(6,3),
    free_cash_flow NUMERIC(15,2),
    report_date DATE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_reports_company_year ON financial_reports(company_id, fiscal_year);
CREATE INDEX idx_reports_company_quarter ON financial_reports(company_id, fiscal_year, fiscal_quarter);

-- Stock prices table
CREATE TABLE stock_prices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    open NUMERIC(10,2),
    high NUMERIC(10,2),
    low NUMERIC(10,2),
    close NUMERIC(10,2),
    volume BIGINT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_prices_company_date ON stock_prices(company_id, date);
CREATE INDEX idx_prices_date ON stock_prices(date);

-- Analyst ratings table
CREATE TABLE analyst_ratings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    analyst_firm VARCHAR(255) NOT NULL,
    rating VARCHAR(20) NOT NULL,
    target_price NUMERIC(10,2),
    previous_rating VARCHAR(20),
    rating_date DATE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_ratings_company ON analyst_ratings(company_id);
CREATE INDEX idx_ratings_date ON analyst_ratings(rating_date);
