"""
Data Fetcher Module - Fetches financial data from multiple sources
Supports: Screener.in (India), Yahoo Finance (Global), Financial Modeling Prep API
Version: 2.1.0 - Universal NSE/BSE ticker acceptance
"""

import os
import re
import json
import time
import sys
import warnings
from abc import ABC, abstractmethod
from contextlib import contextmanager
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

import requests
from bs4 import BeautifulSoup
import pandas as pd

try:
    import yfinance as yf
except ImportError:
    yf = None


@contextmanager
def suppress_output():
    """Suppress stdout and stderr temporarily"""
    import io
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    sys.stdout = io.StringIO()
    sys.stderr = io.StringIO()
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            yield
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr


@dataclass
class FinancialData:
    """Container for company financial data"""
    company_name: str
    ticker: str
    years_analyzed: int
    
    # Balance Sheet Data
    total_assets: Dict[str, float] = field(default_factory=dict)
    total_liabilities: Dict[str, float] = field(default_factory=dict)
    shareholders_equity: Dict[str, float] = field(default_factory=dict)
    total_debt: Dict[str, float] = field(default_factory=dict)
    cash_and_equivalents: Dict[str, float] = field(default_factory=dict)
    
    # Income Statement Data
    revenue: Dict[str, float] = field(default_factory=dict)
    net_income: Dict[str, float] = field(default_factory=dict)
    operating_income: Dict[str, float] = field(default_factory=dict)
    gross_profit: Dict[str, float] = field(default_factory=dict)
    ebitda: Dict[str, float] = field(default_factory=dict)
    
    # Cash Flow Data
    operating_cash_flow: Dict[str, float] = field(default_factory=dict)
    free_cash_flow: Dict[str, float] = field(default_factory=dict)
    capex: Dict[str, float] = field(default_factory=dict)
    
    # Key Ratios
    roe: Dict[str, float] = field(default_factory=dict)  # Return on Equity
    roa: Dict[str, float] = field(default_factory=dict)  # Return on Assets
    roce: Dict[str, float] = field(default_factory=dict)  # Return on Capital Employed
    debt_to_equity: Dict[str, float] = field(default_factory=dict)
    current_ratio: Dict[str, float] = field(default_factory=dict)
    interest_coverage: Dict[str, float] = field(default_factory=dict)
    
    # Quality Metrics
    revenue_growth: Dict[str, float] = field(default_factory=dict)
    profit_growth: Dict[str, float] = field(default_factory=dict)
    operating_margin: Dict[str, float] = field(default_factory=dict)
    net_margin: Dict[str, float] = field(default_factory=dict)
    
    # Additional Info
    sector: str = ""
    industry: str = ""
    market_cap: float = 0.0
    pe_ratio: float = 0.0
    pb_ratio: float = 0.0
    dividend_yield: float = 0.0
    
    # Raw data for AI analysis
    raw_data: Dict[str, Any] = field(default_factory=dict)
    data_source: str = ""
    fetch_timestamp: str = ""
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            'company_name': self.company_name,
            'ticker': self.ticker,
            'years_analyzed': self.years_analyzed,
            'total_assets': self.total_assets,
            'total_liabilities': self.total_liabilities,
            'shareholders_equity': self.shareholders_equity,
            'total_debt': self.total_debt,
            'cash_and_equivalents': self.cash_and_equivalents,
            'revenue': self.revenue,
            'net_income': self.net_income,
            'operating_income': self.operating_income,
            'gross_profit': self.gross_profit,
            'ebitda': self.ebitda,
            'operating_cash_flow': self.operating_cash_flow,
            'free_cash_flow': self.free_cash_flow,
            'capex': self.capex,
            'roe': self.roe,
            'roa': self.roa,
            'roce': self.roce,
            'debt_to_equity': self.debt_to_equity,
            'current_ratio': self.current_ratio,
            'interest_coverage': self.interest_coverage,
            'revenue_growth': self.revenue_growth,
            'profit_growth': self.profit_growth,
            'operating_margin': self.operating_margin,
            'net_margin': self.net_margin,
            'sector': self.sector,
            'industry': self.industry,
            'market_cap': self.market_cap,
            'pe_ratio': self.pe_ratio,
            'pb_ratio': self.pb_ratio,
            'dividend_yield': self.dividend_yield,
            'data_source': self.data_source,
            'fetch_timestamp': self.fetch_timestamp
        }


class BaseDataFetcher(ABC):
    """Abstract base class for data fetchers"""
    
    @abstractmethod
    def fetch_data(self, company_identifier: str, years: int) -> Optional[FinancialData]:
        """Fetch financial data for a company"""
        pass
    
    @abstractmethod
    def search_company(self, query: str) -> List[Dict[str, str]]:
        """Search for a company by name or ticker"""
        pass


class ScreenerInFetcher(BaseDataFetcher):
    """Fetcher for Screener.in (Indian stocks)"""
    
    BASE_URL = "https://www.screener.in"
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)
    
    def search_company(self, query: str) -> List[Dict[str, str]]:
        """Search for companies on Screener.in"""
        try:
            search_url = f"{self.BASE_URL}/api/company/search/?q={query}"
            response = self.session.get(search_url, timeout=10)
            
            if response.status_code == 200:
                results = response.json()
                parsed_results = []
                for item in results[:10]:
                    name = item.get('name', '')
                    url = item.get('url', '')
                    # URL format: /company/TCS/ or /company/TCS/consolidated/
                    # Extract the company identifier (second segment after /company/)
                    parts = [p for p in url.split('/') if p]  # Remove empty strings
                    ticker = ''
                    if len(parts) >= 2 and parts[0] == 'company':
                        ticker = parts[1].upper()  # The company identifier
                    if ticker and ticker not in ['CONSOLIDATED', 'STANDALONE']:
                        parsed_results.append({'name': name, 'ticker': ticker})
                return parsed_results
        except Exception as e:
            pass  # Silent fail
        return []
    
    def fetch_data(self, company_identifier: str, years: int) -> Optional[FinancialData]:
        """Fetch financial data from Screener.in"""
        try:
            # Try to get the company page
            company_url = f"{self.BASE_URL}/company/{company_identifier}/consolidated/"
            response = self.session.get(company_url, timeout=15)
            
            if response.status_code != 200:
                # Try standalone if consolidated fails
                company_url = f"{self.BASE_URL}/company/{company_identifier}/"
                response = self.session.get(company_url, timeout=15)
            
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.content, 'lxml')
            
            # Extract company name
            company_name = ""
            name_elem = soup.find('h1', class_='h2')
            if name_elem:
                company_name = name_elem.text.strip()
            
            # Initialize financial data
            fin_data = FinancialData(
                company_name=company_name,
                ticker=company_identifier.upper(),
                years_analyzed=years,
                data_source="Screener.in",
                fetch_timestamp=datetime.now().isoformat()
            )
            
            # Extract data from tables
            self._extract_profit_loss(soup, fin_data, years)
            self._extract_balance_sheet(soup, fin_data, years)
            self._extract_cash_flow(soup, fin_data, years)
            self._extract_ratios(soup, fin_data, years)
            self._extract_company_info(soup, fin_data)
            
            return fin_data
            
        except Exception as e:
            # Silent fail - multi-source fetcher will try next source
            return None
    
    def _extract_table_data(self, soup: BeautifulSoup, section_id: str, metric_name: str, years: int) -> Dict[str, float]:
        """Extract specific metric from a table section"""
        data = {}
        try:
            section = soup.find('section', id=section_id)
            if not section:
                return data
            
            table = section.find('table')
            if not table:
                return data
            
            # Get years from header
            header = table.find('thead')
            if header:
                year_cells = header.find_all('th')[1:]  # Skip first column
                year_labels = [cell.text.strip() for cell in year_cells][-years:]
            else:
                return data
            
            # Find the row with the metric
            rows = table.find('tbody').find_all('tr')
            for row in rows:
                cells = row.find_all('td')
                if cells:
                    row_label = cells[0].text.strip().lower()
                    if metric_name.lower() in row_label:
                        values = [cells[i].text.strip() for i in range(1, len(cells))][-years:]
                        for i, year in enumerate(year_labels):
                            if i < len(values):
                                try:
                                    # Clean and convert value
                                    val = values[i].replace(',', '').replace('%', '').strip()
                                    if val and val != '-':
                                        data[year] = float(val)
                                except ValueError:
                                    pass
                        break
        except Exception as e:
            pass
        return data
    
    def _extract_profit_loss(self, soup: BeautifulSoup, fin_data: FinancialData, years: int):
        """Extract P&L data"""
        fin_data.revenue = self._extract_table_data(soup, 'profit-loss', 'sales', years)
        if not fin_data.revenue:
            fin_data.revenue = self._extract_table_data(soup, 'profit-loss', 'revenue', years)
        fin_data.operating_income = self._extract_table_data(soup, 'profit-loss', 'operating profit', years)
        fin_data.net_income = self._extract_table_data(soup, 'profit-loss', 'net profit', years)
        fin_data.operating_margin = self._extract_table_data(soup, 'profit-loss', 'opm', years)
    
    def _extract_balance_sheet(self, soup: BeautifulSoup, fin_data: FinancialData, years: int):
        """Extract balance sheet data"""
        fin_data.shareholders_equity = self._extract_table_data(soup, 'balance-sheet', 'equity', years)
        fin_data.total_debt = self._extract_table_data(soup, 'balance-sheet', 'borrowing', years)
        fin_data.total_assets = self._extract_table_data(soup, 'balance-sheet', 'total assets', years)
    
    def _extract_cash_flow(self, soup: BeautifulSoup, fin_data: FinancialData, years: int):
        """Extract cash flow data"""
        fin_data.operating_cash_flow = self._extract_table_data(soup, 'cash-flow', 'operating', years)
        fin_data.free_cash_flow = self._extract_table_data(soup, 'cash-flow', 'free cash flow', years)
    
    def _extract_ratios(self, soup: BeautifulSoup, fin_data: FinancialData, years: int):
        """Extract financial ratios"""
        fin_data.roe = self._extract_table_data(soup, 'ratios', 'roe', years)
        fin_data.roce = self._extract_table_data(soup, 'ratios', 'roce', years)
    
    def _extract_company_info(self, soup: BeautifulSoup, fin_data: FinancialData):
        """Extract company information"""
        try:
            # Extract from top ratios section
            ratios_list = soup.find('ul', id='top-ratios')
            if ratios_list:
                items = ratios_list.find_all('li')
                for item in items:
                    name = item.find('span', class_='name')
                    value = item.find('span', class_='number')
                    if name and value:
                        name_text = name.text.strip().lower()
                        value_text = value.text.strip().replace(',', '')
                        
                        if 'market cap' in name_text:
                            fin_data.market_cap = self._parse_value(value_text)
                        elif 'stock p/e' in name_text or 'p/e' in name_text:
                            fin_data.pe_ratio = self._parse_value(value_text)
                        elif 'book value' in name_text:
                            pass  # Could calculate P/B from this
                        elif 'dividend yield' in name_text:
                            fin_data.dividend_yield = self._parse_value(value_text)
                        elif 'roe' in name_text:
                            fin_data.roe['current'] = self._parse_value(value_text)
                        elif 'roce' in name_text:
                            fin_data.roce['current'] = self._parse_value(value_text)
            
            # Extract sector/industry
            company_info = soup.find('div', class_='company-info')
            if company_info:
                links = company_info.find_all('a')
                for link in links:
                    href = link.get('href', '')
                    if '/screen/raw/' in href:
                        fin_data.sector = link.text.strip()
                        break
                        
        except Exception as e:
            pass
    
    def _parse_value(self, value_str: str) -> float:
        """Parse value string to float"""
        try:
            value_str = value_str.replace(',', '').replace('%', '').strip()
            if 'Cr' in value_str:
                value_str = value_str.replace('Cr', '').strip()
            return float(value_str)
        except ValueError:
            return 0.0


class YahooFinanceFetcher(BaseDataFetcher):
    """Fetcher for Yahoo Finance (Global stocks)"""
    
    # Common Indian stock tickers that need .NS suffix
    INDIAN_TICKERS = {
        'TCS', 'RELIANCE', 'INFY', 'HDFCBANK', 'ICICIBANK', 'HINDUNILVR',
        'SBIN', 'BHARTIARTL', 'ITC', 'KOTAKBANK', 'LT', 'AXISBANK',
        'WIPRO', 'ASIANPAINT', 'MARUTI', 'HCLTECH', 'SUNPHARMA', 'TITAN',
        'ULTRACEMCO', 'BAJFINANCE', 'NESTLEIND', 'TECHM', 'POWERGRID',
        'NTPC', 'TATAMOTORS', 'TATASTEEL', 'JSWSTEEL', 'ONGC', 'COALINDIA',
        'ADANIENT', 'ADANIPORTS', 'BAJAJFINSV', 'DRREDDY', 'CIPLA', 'EICHERMOT',
        'GRASIM', 'DIVISLAB', 'BRITANNIA', 'APOLLOHOSP', 'INDUSINDBK', 'M&M',
        'BPCL', 'HEROMOTOCO', 'HINDALCO', 'TATACONSUM', 'BAJAJ-AUTO', 'UPL'
    }
    
    def __init__(self):
        if yf is None:
            raise ImportError("yfinance is required for Yahoo Finance fetching")
    
    def _resolve_ticker(self, company_identifier: str) -> List[str]:
        """Resolve ticker to possible Yahoo Finance symbols"""
        ticker = company_identifier.upper().strip()
        candidates = []
        
        # If already has exchange suffix, use as-is
        if '.NS' in ticker or '.BO' in ticker or '.' in ticker:
            candidates.append(ticker)
            return candidates
        
        # Check if it's a known Indian stock
        if ticker in self.INDIAN_TICKERS:
            candidates.append(f"{ticker}.NS")  # NSE first
            candidates.append(f"{ticker}.BO")  # BSE as fallback
        
        # Also try the raw ticker (for US stocks)
        candidates.append(ticker)
        
        return candidates
    
    def search_company(self, query: str) -> List[Dict[str, str]]:
        """Search for companies using Yahoo Finance data"""
        ticker = query.upper().strip()
        results = []
        
        # Try to get actual company name from Yahoo Finance
        try:
            candidates = self._resolve_ticker(ticker)
            for ticker_symbol in candidates:
                try:
                    # Try with suppress_output first
                    with suppress_output():
                        yf_ticker = yf.Ticker(ticker_symbol)
                        info = yf_ticker.info
                    
                    # If info is empty or very small, try without suppression
                    if not info or len(info) < 5:
                        yf_ticker = yf.Ticker(ticker_symbol)
                        info = yf_ticker.info
                    
                    if info and len(info) > 5:  # Valid info dict should have many fields
                        # Try multiple name fields in order of preference
                        company_name = None
                        for name_field in ['longName', 'shortName', 'name', 'quoteType']:
                            if name_field in info and info[name_field]:
                                potential_name = str(info[name_field])
                                # Skip if it's just the ticker itself (without exchange suffix)
                                base_ticker = ticker_symbol.replace('.NS', '').replace('.BO', '').replace('.', '')
                                if (potential_name.upper() != base_ticker and 
                                    potential_name.upper() != ticker and
                                    potential_name.upper() not in ['EQUITY', 'MUTUALFUND', 'ETF']):
                                    company_name = potential_name
                                    break
                        
                        if company_name and company_name.upper() not in [ticker, ticker_symbol, base_ticker]:
                            results.append({'name': company_name, 'ticker': ticker_symbol})
                            break  # Use first successful result with proper name
                except Exception as e:
                    # Continue trying other candidates
                    continue
        except Exception as e:
            # If all attempts fail, results will be empty
            pass
        
        # Don't add fallback with ticker as company name
        # Return empty results if we couldn't fetch a real company name
        # This allows the validation to try other APIs or fail gracefully
        return results
    
    def fetch_data(self, company_identifier: str, years: int) -> Optional[FinancialData]:
        """Fetch financial data from Yahoo Finance"""
        # Try different ticker variants
        ticker_candidates = self._resolve_ticker(company_identifier)
        
        for ticker_symbol in ticker_candidates:
            try:
                result = self._fetch_for_ticker(ticker_symbol, years)
                if result and (result.revenue or result.net_income):
                    return result
            except Exception:
                continue
        
        return None
    
    def _fetch_for_ticker(self, ticker_symbol: str, years: int) -> Optional[FinancialData]:
        """Fetch data for a specific ticker symbol"""
        try:
            # Suppress yfinance HTTP error messages
            with suppress_output():
                ticker = yf.Ticker(ticker_symbol)
                info = ticker.info
            
            if not info or 'symbol' not in info:
                return None
            
            fin_data = FinancialData(
                company_name=info.get('longName', info.get('shortName', ticker_symbol)),
                ticker=ticker_symbol.upper(),
                years_analyzed=years,
                data_source="Yahoo Finance",
                fetch_timestamp=datetime.now().isoformat()
            )
            
            # Get financial statements (suppress any yfinance warnings)
            with suppress_output():
                income_stmt = ticker.income_stmt
                balance_sheet = ticker.balance_sheet
                cash_flow = ticker.cashflow
            
            # Process income statement
            if income_stmt is not None and not income_stmt.empty:
                columns = list(income_stmt.columns)[:years]
                for col in columns:
                    year_label = str(col.year) if hasattr(col, 'year') else str(col)
                    
                    if 'Total Revenue' in income_stmt.index:
                        fin_data.revenue[year_label] = float(income_stmt.loc['Total Revenue', col] or 0)
                    if 'Net Income' in income_stmt.index:
                        fin_data.net_income[year_label] = float(income_stmt.loc['Net Income', col] or 0)
                    if 'Operating Income' in income_stmt.index:
                        fin_data.operating_income[year_label] = float(income_stmt.loc['Operating Income', col] or 0)
                    if 'Gross Profit' in income_stmt.index:
                        fin_data.gross_profit[year_label] = float(income_stmt.loc['Gross Profit', col] or 0)
                    if 'EBITDA' in income_stmt.index:
                        fin_data.ebitda[year_label] = float(income_stmt.loc['EBITDA', col] or 0)
            
            # Process balance sheet
            if balance_sheet is not None and not balance_sheet.empty:
                columns = list(balance_sheet.columns)[:years]
                for col in columns:
                    year_label = str(col.year) if hasattr(col, 'year') else str(col)
                    
                    if 'Total Assets' in balance_sheet.index:
                        fin_data.total_assets[year_label] = float(balance_sheet.loc['Total Assets', col] or 0)
                    if 'Total Liabilities Net Minority Interest' in balance_sheet.index:
                        fin_data.total_liabilities[year_label] = float(balance_sheet.loc['Total Liabilities Net Minority Interest', col] or 0)
                    if 'Stockholders Equity' in balance_sheet.index:
                        fin_data.shareholders_equity[year_label] = float(balance_sheet.loc['Stockholders Equity', col] or 0)
                    if 'Total Debt' in balance_sheet.index:
                        fin_data.total_debt[year_label] = float(balance_sheet.loc['Total Debt', col] or 0)
                    if 'Cash And Cash Equivalents' in balance_sheet.index:
                        fin_data.cash_and_equivalents[year_label] = float(balance_sheet.loc['Cash And Cash Equivalents', col] or 0)
            
            # Process cash flow
            if cash_flow is not None and not cash_flow.empty:
                columns = list(cash_flow.columns)[:years]
                for col in columns:
                    year_label = str(col.year) if hasattr(col, 'year') else str(col)
                    
                    if 'Operating Cash Flow' in cash_flow.index:
                        fin_data.operating_cash_flow[year_label] = float(cash_flow.loc['Operating Cash Flow', col] or 0)
                    if 'Free Cash Flow' in cash_flow.index:
                        fin_data.free_cash_flow[year_label] = float(cash_flow.loc['Free Cash Flow', col] or 0)
                    if 'Capital Expenditure' in cash_flow.index:
                        fin_data.capex[year_label] = float(cash_flow.loc['Capital Expenditure', col] or 0)
            
            # Additional info
            fin_data.sector = info.get('sector', '')
            fin_data.industry = info.get('industry', '')
            fin_data.market_cap = info.get('marketCap', 0)
            fin_data.pe_ratio = info.get('trailingPE', 0)
            fin_data.pb_ratio = info.get('priceToBook', 0)
            fin_data.dividend_yield = info.get('dividendYield', 0) * 100 if info.get('dividendYield') else 0
            
            # Calculate ratios
            self._calculate_ratios(fin_data)
            
            return fin_data
            
        except Exception as e:
            # Silent fail - multi-source fetcher will try next source
            return None
    
    def _calculate_ratios(self, fin_data: FinancialData):
        """Calculate financial ratios from raw data"""
        for year in fin_data.revenue.keys():
            # ROE = Net Income / Shareholders Equity
            if year in fin_data.net_income and year in fin_data.shareholders_equity:
                if fin_data.shareholders_equity[year] != 0:
                    fin_data.roe[year] = (fin_data.net_income[year] / fin_data.shareholders_equity[year]) * 100
            
            # ROA = Net Income / Total Assets
            if year in fin_data.net_income and year in fin_data.total_assets:
                if fin_data.total_assets[year] != 0:
                    fin_data.roa[year] = (fin_data.net_income[year] / fin_data.total_assets[year]) * 100
            
            # Debt to Equity = Total Debt / Shareholders Equity
            if year in fin_data.total_debt and year in fin_data.shareholders_equity:
                if fin_data.shareholders_equity[year] != 0:
                    fin_data.debt_to_equity[year] = fin_data.total_debt[year] / fin_data.shareholders_equity[year]
            
            # Operating Margin = Operating Income / Revenue
            if year in fin_data.operating_income and year in fin_data.revenue:
                if fin_data.revenue[year] != 0:
                    fin_data.operating_margin[year] = (fin_data.operating_income[year] / fin_data.revenue[year]) * 100
            
            # Net Margin = Net Income / Revenue
            if year in fin_data.net_income and year in fin_data.revenue:
                if fin_data.revenue[year] != 0:
                    fin_data.net_margin[year] = (fin_data.net_income[year] / fin_data.revenue[year]) * 100


class FMPFetcher(BaseDataFetcher):
    """Fetcher for Financial Modeling Prep API"""
    
    BASE_URL = "https://financialmodelingprep.com/api/v3"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    def search_company(self, query: str) -> List[Dict[str, str]]:
        """Search for companies using FMP API"""
        try:
            url = f"{self.BASE_URL}/search?query={query}&apikey={self.api_key}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                results = response.json()
                return [
                    {'name': item.get('name', ''), 'ticker': item.get('symbol', '')}
                    for item in results[:10]
                ]
        except Exception as e:
            print(f"Search error: {e}")
        return []
    
    def fetch_data(self, company_identifier: str, years: int) -> Optional[FinancialData]:
        """Fetch financial data from FMP API"""
        try:
            # Get company profile
            profile_url = f"{self.BASE_URL}/profile/{company_identifier}?apikey={self.api_key}"
            profile_resp = requests.get(profile_url, timeout=10)
            
            if profile_resp.status_code != 200:
                return None
            
            profile = profile_resp.json()[0] if profile_resp.json() else {}
            
            fin_data = FinancialData(
                company_name=profile.get('companyName', company_identifier),
                ticker=company_identifier.upper(),
                years_analyzed=years,
                data_source="Financial Modeling Prep",
                fetch_timestamp=datetime.now().isoformat()
            )
            
            # Get income statement
            income_url = f"{self.BASE_URL}/income-statement/{company_identifier}?limit={years}&apikey={self.api_key}"
            income_resp = requests.get(income_url, timeout=10)
            
            if income_resp.status_code == 200:
                for item in income_resp.json():
                    year = item.get('date', '')[:4]
                    fin_data.revenue[year] = item.get('revenue', 0)
                    fin_data.net_income[year] = item.get('netIncome', 0)
                    fin_data.operating_income[year] = item.get('operatingIncome', 0)
                    fin_data.gross_profit[year] = item.get('grossProfit', 0)
                    fin_data.ebitda[year] = item.get('ebitda', 0)
            
            # Get balance sheet
            balance_url = f"{self.BASE_URL}/balance-sheet-statement/{company_identifier}?limit={years}&apikey={self.api_key}"
            balance_resp = requests.get(balance_url, timeout=10)
            
            if balance_resp.status_code == 200:
                for item in balance_resp.json():
                    year = item.get('date', '')[:4]
                    fin_data.total_assets[year] = item.get('totalAssets', 0)
                    fin_data.total_liabilities[year] = item.get('totalLiabilities', 0)
                    fin_data.shareholders_equity[year] = item.get('totalStockholdersEquity', 0)
                    fin_data.total_debt[year] = item.get('totalDebt', 0)
                    fin_data.cash_and_equivalents[year] = item.get('cashAndCashEquivalents', 0)
            
            # Get cash flow
            cashflow_url = f"{self.BASE_URL}/cash-flow-statement/{company_identifier}?limit={years}&apikey={self.api_key}"
            cashflow_resp = requests.get(cashflow_url, timeout=10)
            
            if cashflow_resp.status_code == 200:
                for item in cashflow_resp.json():
                    year = item.get('date', '')[:4]
                    fin_data.operating_cash_flow[year] = item.get('operatingCashFlow', 0)
                    fin_data.free_cash_flow[year] = item.get('freeCashFlow', 0)
                    fin_data.capex[year] = item.get('capitalExpenditure', 0)
            
            # Set company info
            fin_data.sector = profile.get('sector', '')
            fin_data.industry = profile.get('industry', '')
            fin_data.market_cap = profile.get('mktCap', 0)
            fin_data.pe_ratio = profile.get('pe', 0)
            
            return fin_data
            
        except Exception as e:
            print(f"Error fetching data from FMP: {e}")
            return None


class DataFetcherFactory:
    """Factory to create appropriate data fetcher based on market/availability"""
    
    @staticmethod
    def create_fetcher(market: str = "auto", api_key: str = None) -> BaseDataFetcher:
        """
        Create a data fetcher based on market
        
        Args:
            market: 'india', 'us', 'global', or 'auto'
            api_key: API key for premium data sources
        """
        if market.lower() == "india":
            return ScreenerInFetcher()
        elif market.lower() in ["us", "global"]:
            if api_key:
                return FMPFetcher(api_key)
            return YahooFinanceFetcher()
        else:
            # Auto-detect: try Yahoo Finance first as it's most universal
            return YahooFinanceFetcher()
    
    @staticmethod
    def get_all_fetchers(fmp_api_key: str = None) -> List[BaseDataFetcher]:
        """Get all available fetchers for fallback"""
        fetchers = [ScreenerInFetcher()]
        
        if yf:
            fetchers.append(YahooFinanceFetcher())
        
        if fmp_api_key:
            fetchers.append(FMPFetcher(fmp_api_key))
        
        return fetchers


class MultiSourceFetcher:
    """Fetcher that tries multiple sources with fallback"""
    
    # Known Indian stock tickers for auto-detection
    INDIAN_TICKERS = {
        'TCS', 'RELIANCE', 'INFY', 'HDFCBANK', 'ICICIBANK', 'HINDUNILVR',
        'SBIN', 'BHARTIARTL', 'ITC', 'KOTAKBANK', 'LT', 'AXISBANK',
        'WIPRO', 'ASIANPAINT', 'MARUTI', 'HCLTECH', 'SUNPHARMA', 'TITAN',
        'ULTRACEMCO', 'BAJFINANCE', 'NESTLEIND', 'TECHM', 'POWERGRID',
        'NTPC', 'TATAMOTORS', 'TATASTEEL', 'JSWSTEEL', 'ONGC', 'COALINDIA'
    }
    
    def __init__(self, fmp_api_key: str = None):
        self.fetchers = DataFetcherFactory.get_all_fetchers(fmp_api_key)
    
    def _detect_market(self, company_identifier: str) -> str:
        """Auto-detect market based on ticker"""
        ticker = company_identifier.upper().strip()
        
        # Check for explicit exchange suffix
        if '.NS' in ticker or '.BO' in ticker:
            return 'india'
        
        # Check if it's a known Indian ticker
        if ticker in self.INDIAN_TICKERS:
            return 'india'
        
        return 'global'
    
    def fetch_data(self, company_identifier: str, years: int, preferred_market: str = "auto") -> Optional[FinancialData]:
        """Try to fetch data from multiple sources"""
        
        # Auto-detect market if needed
        if preferred_market.lower() == "auto":
            preferred_market = self._detect_market(company_identifier)
        
        # Reorder fetchers based on preferred market
        fetchers = self.fetchers.copy()
        if preferred_market.lower() == "india":
            # For Indian stocks: try Yahoo Finance with .NS suffix first (more reliable), then Screener.in
            fetchers = [f for f in fetchers if isinstance(f, YahooFinanceFetcher)] + \
                      [f for f in fetchers if isinstance(f, ScreenerInFetcher)] + \
                      [f for f in fetchers if not isinstance(f, (YahooFinanceFetcher, ScreenerInFetcher))]
        
        for fetcher in fetchers:
            try:
                data = fetcher.fetch_data(company_identifier, years)
                if data and (data.revenue or data.net_income):
                    return data
            except Exception as e:
                continue
        
        return None
    
    def search_company(self, query: str) -> List[Dict[str, str]]:
        """Search for company across all sources"""
        all_results = []
        seen = set()
        
        for fetcher in self.fetchers:
            try:
                results = fetcher.search_company(query)
                for r in results:
                    key = (r['name'].lower(), r['ticker'].upper())
                    if key not in seen:
                        seen.add(key)
                        all_results.append(r)
            except Exception:
                continue
        
        return all_results


def validate_company_name(company_name: str, fmp_api_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Validate company name or ticker and fetch matching information
    Accepts both company names and ticker symbols for validation
    
    Args:
        company_name: Company name or ticker symbol to validate
        fmp_api_key: Optional FMP API key for enhanced search
    
    Returns:
        Dict with:
            - 'valid': bool indicating if company was found
            - 'matches': List of matching companies with name and ticker
            - 'best_match': Best matching company (if found)
            - 'error': Error message (if any)
    """
    result = {
        'valid': False,
        'matches': [],
        'best_match': None,
        'error': None
    }
    
    if not company_name or not company_name.strip():
        result['error'] = "Company name or ticker cannot be empty"
        return result
    
    query = company_name.strip()
    
    try:
        # Auto-capitalize if it looks like a ticker
        if query and len(query) <= 15 and query.replace('.', '').replace('-', '').isalnum():
            query = query.upper()
        
        # Check if input looks like a ticker (short, uppercase, alphanumeric)
        # Remove dots and dashes for checking (to handle ALKEM.NS, BAJAJ-AUTO, etc.)
        clean_query = query.replace('.', '').replace('-', '')
        is_likely_ticker = (
            len(query) <= 15 and  # Extended to handle longer tickers with suffixes
            clean_query.isalnum() and
            clean_query.isupper()  # Check uppercase on cleaned string
        )
        
        # AUTO-ADD .NS suffix for likely Indian tickers without suffix
        if is_likely_ticker and '.NS' not in query and '.BO' not in query and len(clean_query) <= 12:
            # Short ticker without suffix - likely NSE stock
            query = f"{query}.NS"
        
        # FIRST PRIORITY: Accept ANY ticker with .NS or .BO suffix immediately
        # This allows validation of ANY NSE/BSE stock
        if '.NS' in query or '.BO' in query:
            # Will populate with company name later from hardcoded list or APIs
            result['matches'] = [{'name': query, 'ticker': query}]
            result['valid'] = True
            result['best_match'] = result['matches'][0]
            # Continue to try to fetch actual company name, but don't fail if we can't
        
        # Hardcoded mapping for major Indian stocks (use FIRST to avoid API issues)
        # Comprehensive list of NSE stocks - 150+ companies
        INDIAN_STOCK_NAMES = {
            # Nifty 50 - Large Caps
            'RELIANCE': 'Reliance Industries Limited',
            'TCS': 'Tata Consultancy Services Limited',
            'HDFCBANK': 'HDFC Bank Limited',
            'INFY': 'Infosys Limited',
            'ICICIBANK': 'ICICI Bank Limited',
            'HINDUNILVR': 'Hindustan Unilever Limited',
            'SBIN': 'State Bank of India',
            'BHARTIARTL': 'Bharti Airtel Limited',
            'ITC': 'ITC Limited',
            'KOTAKBANK': 'Kotak Mahindra Bank Limited',
            'LT': 'Larsen & Toubro Limited',
            'AXISBANK': 'Axis Bank Limited',
            'WIPRO': 'Wipro Limited',
            'ASIANPAINT': 'Asian Paints Limited',
            'MARUTI': 'Maruti Suzuki India Limited',
            'HCLTECH': 'HCL Technologies Limited',
            'SUNPHARMA': 'Sun Pharmaceutical Industries Limited',
            'TITAN': 'Titan Company Limited',
            'ULTRACEMCO': 'UltraTech Cement Limited',
            'BAJFINANCE': 'Bajaj Finance Limited',
            'NESTLEIND': 'Nestle India Limited',
            'TECHM': 'Tech Mahindra Limited',
            'POWERGRID': 'Power Grid Corporation of India Limited',
            'NTPC': 'NTPC Limited',
            'TATAMOTORS': 'Tata Motors Limited',
            'TATASTEEL': 'Tata Steel Limited',
            'JSWSTEEL': 'JSW Steel Limited',
            'ONGC': 'Oil and Natural Gas Corporation Limited',
            'COALINDIA': 'Coal India Limited',
            'ADANIENT': 'Adani Enterprises Limited',
            'ADANIPORTS': 'Adani Ports and Special Economic Zone Limited',
            'BAJAJFINSV': 'Bajaj Finserv Limited',
            'DRREDDY': 'Dr. Reddy\'s Laboratories Limited',
            'CIPLA': 'Cipla Limited',
            'EICHERMOT': 'Eicher Motors Limited',
            'GRASIM': 'Grasim Industries Limited',
            'DIVISLAB': 'Divi\'s Laboratories Limited',
            'BRITANNIA': 'Britannia Industries Limited',
            'APOLLOHOSP': 'Apollo Hospitals Enterprise Limited',
            'INDUSINDBK': 'IndusInd Bank Limited',
            'M&M': 'Mahindra & Mahindra Limited',
            'BPCL': 'Bharat Petroleum Corporation Limited',
            'HEROMOTOCO': 'Hero MotoCorp Limited',
            'HINDALCO': 'Hindalco Industries Limited',
            'TATACONSUM': 'Tata Consumer Products Limited',
            'BAJAJ-AUTO': 'Bajaj Auto Limited',
            'UPL': 'UPL Limited',
            
            # Nifty Next 50 & Popular Mid/Small Caps
            'VEDL': 'Vedanta Limited',
            'GODREJCP': 'Godrej Consumer Products Limited',
            'DABUR': 'Dabur India Limited',
            'MARICO': 'Marico Limited',
            'PIIND': 'PI Industries Limited',
            'BANKBARODA': 'Bank of Baroda',
            'PNB': 'Punjab National Bank',
            'CANBK': 'Canara Bank',
            'UNIONBANK': 'Union Bank of India',
            'INDHOTEL': 'The Indian Hotels Company Limited',
            'TRENT': 'Trent Limited',
            'PIDILITIND': 'Pidilite Industries Limited',
            'AMBUJACEM': 'Ambuja Cements Limited',
            'ACC': 'ACC Limited',
            'SHREECEM': 'Shree Cement Limited',
            'GAIL': 'GAIL (India) Limited',
            'IOC': 'Indian Oil Corporation Limited',
            'HINDZINC': 'Hindustan Zinc Limited',
            'HINDALCO': 'Hindalco Industries Limited',
            'SAIL': 'Steel Authority of India Limited',
            'NMDC': 'NMDC Limited',
            'ADANIGREEN': 'Adani Green Energy Limited',
            'ADANIPOWER': 'Adani Power Limited',
            'ADANITRANS': 'Adani Transmission Limited',
            'TATAPOWER': 'Tata Power Company Limited',
            'TORNTPOWER': 'Torrent Power Limited',
            'SIEMENS': 'Siemens Limited',
            'ABB': 'ABB India Limited',
            'HAVELLS': 'Havells India Limited',
            'CROMPTON': 'Crompton Greaves Consumer Electricals Limited',
            'VOLTAS': 'Voltas Limited',
            'BLUESTARCO': 'Blue Star Limited',
            'DIXON': 'Dixon Technologies (India) Limited',
            'GODREJPROP': 'Godrej Properties Limited',
            'DLF': 'DLF Limited',
            'OBEROIRLTY': 'Oberoi Realty Limited',
            'PRESTIGE': 'Prestige Estates Projects Limited',
            'PHOENIXLTD': 'The Phoenix Mills Limited',
            'INDIGOPNTS': 'Indigo Paints Limited',
            'BERGEPAINT': 'Berger Paints India Limited',
            'AKZOINDIA': 'Akzo Nobel India Limited',
            'MCDOWELL-N': 'United Spirits Limited',
            'RADICO': 'Radico Khaitan Limited',
            'UNITDSPR': 'United Spirits Limited',
            'VBL': 'Varun Beverages Limited',
            'TATACOMM': 'Tata Communications Limited',
            'TVSMOTOR': 'TVS Motor Company Limited',
            'BAJAJHLDNG': 'Bajaj Holdings & Investment Limited',
            'BOSCHLTD': 'Bosch Limited',
            'MOTHERSON': 'Samvardhana Motherson International Limited',
            'ESCORTS': 'Escorts Kubota Limited',
            'ASHOKLEY': 'Ashok Leyland Limited',
            'APOLLOTYRE': 'Apollo Tyres Limited',
            'MRF': 'MRF Limited',
            'CEAT': 'CEAT Limited',
            'ZYDUSLIFE': 'Zydus Lifesciences Limited',
            'TORNTPHARM': 'Torrent Pharmaceuticals Limited',
            'AUROPHARMA': 'Aurobindo Pharma Limited',
            'LUPIN': 'Lupin Limited',
            'BIOCON': 'Biocon Limited',
            'ALKEM': 'Alkem Laboratories Limited',
            'LALPATHLAB': 'Dr. Lal PathLabs Limited',
            'FORTIS': 'Fortis Healthcare Limited',
            'MAXHEALTH': 'Max Healthcare Institute Limited',
            'SYNGENE': 'Syngene International Limited',
            'PVR': 'PVR INOX Limited',
            'PVRINOX': 'PVR INOX Limited',
            'ZOMATO': 'Zomato Limited',
            'NYKAA': 'FSN E-Commerce Ventures Limited',
            'POLICYBZR': 'PB Fintech Limited',
            'PAYTM': 'One 97 Communications Limited',
            'DMART': 'Avenue Supermarts Limited',
            'TATAELXSI': 'Tata Elxsi Limited',
            'COFORGE': 'Coforge Limited',
            'LTTS': 'L&T Technology Services Limited',
            'PERSISTENT': 'Persistent Systems Limited',
            'MPHASIS': 'Mphasis Limited',
            'LTIM': 'LTIMindtree Limited',
            'OFSS': 'Oracle Financial Services Software Limited',
            'INDUSTOWER': 'Indus Towers Limited',
            'IRCTC': 'Indian Railway Catering and Tourism Corporation Limited',
            'CONCOR': 'Container Corporation of India Limited',
            'IRFC': 'Indian Railway Finance Corporation Limited',
            'RECLTD': 'REC Limited',
            'PFC': 'Power Finance Corporation Limited',
            'LICHSGFIN': 'LIC Housing Finance Limited',
            'HDFCLIFE': 'HDFC Life Insurance Company Limited',
            'SBILIFE': 'SBI Life Insurance Company Limited',
            'ICICIPRULI': 'ICICI Prudential Life Insurance Company Limited',
            'ICICIGI': 'ICICI Lombard General Insurance Company Limited',
            'BAJAJHFL': 'Bajaj Housing Finance Limited',
            'SHRIRAMFIN': 'Shriram Finance Limited',
            'CHOLAFIN': 'Cholamandalam Investment and Finance Company Limited',
            'MUTHOOTFIN': 'Muthoot Finance Limited',
            'MANAPPURAM': 'Manappuram Finance Limited',
            'JINDALSTEL': 'Jindal Steel & Power Limited',
            'CRISIL': 'CRISIL Limited',
            'ICRA': 'ICRA Limited',
            'PETRONET': 'Petronet LNG Limited',
            'INDIAMART': 'IndiaMART InterMESH Limited',
            'JUSTDIAL': 'Just Dial Limited',
            'INFO EDGE': 'Info Edge (India) Limited',
            'NAUKRI': 'Info Edge (India) Limited',
            'PGHH': 'Procter & Gamble Hygiene and Health Care Limited',
            'COLPAL': 'Colgate-Palmolive (India) Limited',
            'GILLETTE': 'Gillette India Limited',
            'HONAUT': 'Honeywell Automation India Limited',
            'PFIZER': 'Pfizer Limited',
            'GLAXO': 'GlaxoSmithKline Pharmaceuticals Limited',
            'ABBOTINDIA': 'Abbott India Limited',
            'SANOFI': 'Sanofi India Limited',
            
            # Additional popular stocks
            'POLYCAB': 'Polycab India Limited',
            'KANSAINER': 'Kansai Nerolac Paints Limited',
            'RAYMOND': 'Raymond Limited',
            'AIAENG': 'AIA Engineering Limited',
            'WHIRLPOOL': 'Whirlpool of India Limited',
            'SCHAEFFLER': 'Schaeffler India Limited',
            'EXIDEIND': 'Exide Industries Limited',
            'AMARARAJA': 'Amara Raja Energy & Mobility Limited',
            'RELAXO': 'Relaxo Footwears Limited',
            'BATAINDIA': 'Bata India Limited',
            'PAGEIND': 'Page Industries Limited',
            'VENKEYS': 'Venky\'s (India) Limited',
            'JUBLFOOD': 'Jubilant FoodWorks Limited',
            'WESTLIFE': 'Westlife Foodworld Limited',
            'SAPPHIRE': 'Sapphire Foods India Limited',
            'DEVYANI': 'Devyani International Limited',
            'BSOFT': 'KPIT Technologies Limited',
            'SONACOMS': 'Sona BLW Precision Forgings Limited',
            'KPITTECH': 'KPIT Technologies Limited',
        }
        
        # PRIORITY: Check hardcoded mapping to get actual company name
        if is_likely_ticker or result['valid']:  # Check even if already valid from .NS/.BO
            base_query = query.replace('.NS', '').replace('.BO', '')
            if base_query in INDIAN_STOCK_NAMES:
                company_name = INDIAN_STOCK_NAMES[base_query]
                ticker_symbol = f"{base_query}.NS" if '.NS' not in query and '.BO' not in query else query
                result['matches'] = [{'name': company_name, 'ticker': ticker_symbol}]
                result['valid'] = True
                result['best_match'] = result['matches'][0]
                return result
        
        # If already valid from .NS/.BO acceptance, return it
        if result['valid']:
            return result
        
        # For known Indian tickers, add .NS suffix for better API lookups
        INDIAN_TICKERS = set(INDIAN_STOCK_NAMES.keys())
        query_variants = [query]
        if is_likely_ticker:
            base_query = query.replace('.NS', '').replace('.BO', '')
            # Always try .NS suffix for tickers (not just known ones) - helps discover new stocks
            if '.NS' not in query and '.BO' not in query:
                # If it's a known Indian ticker, add .NS
                if base_query in INDIAN_TICKERS:
                    query_variants.append(f"{base_query}.NS")
                # For any short ticker (likely Indian), also try .NS as fallback
                elif len(base_query) <= 12:  # Most NSE tickers are short
                    query_variants.append(f"{base_query}.NS")
        
        # Try FMP API first if available (most comprehensive)
        if fmp_api_key:
            for query_variant in query_variants:
                try:
                    fmp_fetcher = FMPFetcher(fmp_api_key)
                    matches = fmp_fetcher.search_company(query_variant)
                    if matches and any(m.get('name', '').upper() not in [query, query_variant, query.replace('.NS', '').replace('.BO', '')] for m in matches):
                        result['matches'] = matches
                        result['valid'] = True
                        result['best_match'] = matches[0]
                        return result
                except Exception as e:
                    pass  # Fall through to other sources
        
        # Try Yahoo Finance if available
        if yf is not None:
            for query_variant in query_variants:
                try:
                    yf_fetcher = YahooFinanceFetcher()
                    matches = yf_fetcher.search_company(query_variant)
                    # Check if we got a real company name, not just the ticker
                    if matches and any(m.get('name', '').upper() not in [query, query_variant, query.replace('.NS', '').replace('.BO', '')] for m in matches):
                        result['matches'] = matches
                        result['valid'] = True
                        result['best_match'] = matches[0]
                        return result
                except Exception as e:
                    pass  # Continue if Yahoo Finance fails
        
        # If it looks like a ticker and we have FMP API, try direct ticker lookup
        if is_likely_ticker and fmp_api_key:
            for query_variant in query_variants:
                try:
                    # Direct ticker validation via FMP
                    fmp_fetcher = FMPFetcher(fmp_api_key)
                    profile_url = f"{fmp_fetcher.BASE_URL}/profile/{query_variant}?apikey={fmp_api_key}"
                    response = requests.get(profile_url, timeout=5)
                    if response.status_code == 200 and response.json():
                        profile = response.json()[0]
                        company_name = profile.get('companyName', '')
                        if company_name and company_name.upper() not in [query, query_variant.replace('.NS', '').replace('.BO', '')]:
                            result['matches'] = [{
                                'name': company_name,
                                'ticker': query_variant if '.' in query_variant else query.upper()
                            }]
                            result['valid'] = True
                            result['best_match'] = result['matches'][0]
                            return result
                except Exception as e:
                    pass
        
        # If no matches found, provide helpful error message
        if not result['matches']:
            if is_likely_ticker:
                result['error'] = f"Ticker '{query}' not found. For Indian stocks, try adding .NS suffix (e.g., {query}.NS)"
            else:
                result['error'] = f"No matching companies found for '{query}'. Please check the spelling or try entering a ticker symbol with .NS suffix."
        
        return result
        
    except Exception as e:
        result['error'] = f"Error during validation: {str(e)}"
        return result
