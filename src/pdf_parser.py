"""
PDF Annual Report Parser
Extracts financial data from PDF annual reports using AI
"""

import os
import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import json

import pdfplumber
from openai import OpenAI

from .data_fetcher import FinancialData


class PDFReportParser:
    """
    Parses PDF annual reports and extracts financial data
    Uses AI to intelligently extract financial metrics from unstructured PDFs
    """
    
    def __init__(self, openai_api_key: str = None):
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError("OpenAI API key is required for PDF parsing. Set OPENAI_API_KEY environment variable.")
        self.client = OpenAI(api_key=self.openai_api_key)
    
    def extract_text_from_pdf(self, pdf_path: str, max_pages: int = 50) -> str:
        """Extract text content from PDF"""
        text_content = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                # Focus on first 50 pages where financial statements usually are
                pages_to_process = min(len(pdf.pages), max_pages)
                
                for i, page in enumerate(pdf.pages[:pages_to_process]):
                    # Extract text
                    page_text = page.extract_text()
                    if page_text:
                        text_content.append(f"--- Page {i+1} ---\n{page_text}\n")
                    
                    # Extract tables
                    tables = page.extract_tables()
                    if tables:
                        for table_idx, table in enumerate(tables):
                            text_content.append(f"\n[Table {table_idx+1} on Page {i+1}]\n")
                            for row in table:
                                if row:
                                    text_content.append(" | ".join([str(cell) if cell else "" for cell in row]))
                                    text_content.append("\n")
        
        except Exception as e:
            raise Exception(f"Error reading PDF: {e}")
        
        return "\n".join(text_content)
    
    def parse_financial_data_with_ai(
        self, 
        pdf_text: str, 
        company_name: str,
        years_to_analyze: int
    ) -> FinancialData:
        """Use AI to extract financial data from unstructured PDF text"""
        
        # Create a structured prompt for the AI
        prompt = f"""
You are a financial analyst extracting data from an annual report. 
Extract the following financial metrics for the most recent {years_to_analyze} years.

Company: {company_name}

Extract these metrics in JSON format:
{{
  "company_name": "full company name",
  "years": ["2024", "2023", "2022", ...],  // Most recent {years_to_analyze} fiscal years found
  "revenue": {{"2024": value, "2023": value, ...}},  // Annual revenue/sales in millions
  "net_income": {{"2024": value, ...}},  // Net profit in millions
  "operating_income": {{"2024": value, ...}},  // Operating profit/EBIT in millions
  "total_assets": {{"2024": value, ...}},  // Total assets in millions
  "total_liabilities": {{"2024": value, ...}},  // Total liabilities in millions
  "shareholders_equity": {{"2024": value, ...}},  // Shareholders' equity in millions
  "total_debt": {{"2024": value, ...}},  // Total debt/borrowings in millions
  "cash_and_equivalents": {{"2024": value, ...}},  // Cash and cash equivalents in millions
  "operating_cash_flow": {{"2024": value, ...}},  // Cash from operations in millions
  "free_cash_flow": {{"2024": value, ...}},  // Free cash flow in millions
  "capex": {{"2024": value, ...}},  // Capital expenditure in millions
  "sector": "industry sector",
  "industry": "specific industry",
  "market_cap": market_cap_value,  // in millions
  "pe_ratio": float,
  "dividend_yield": float  // as percentage
}}

IMPORTANT:
- Convert all amounts to millions (e.g., if reported in crores, divide by 10)
- Use positive numbers for all values
- If CAPEX is negative in cash flow statement, report as positive
- If a metric is not found, use 0
- Extract from: Balance Sheet, Income Statement, Cash Flow Statement
- Look for consolidated financials if available

Annual Report Text (truncated to relevant sections):

{pdf_text[:15000]}  

Return ONLY valid JSON, no additional text.
"""
        
        try:
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a precise financial data extraction assistant. Extract data accurately from financial statements and return valid JSON only."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,
                max_tokens=2000
            )
            
            # Parse response
            json_text = response.choices[0].message.content.strip()
            
            # Clean up response (remove markdown code blocks if present)
            if json_text.startswith("```"):
                json_text = json_text.split("```")[1]
                if json_text.startswith("json"):
                    json_text = json_text[4:]
            json_text = json_text.strip()
            
            data_dict = json.loads(json_text)
            
            # Get AI-extracted company name, but prioritize user input if provided
            extracted_name = data_dict.get("company_name", "")
            # If AI returned placeholder or empty, or user provided specific name, use user input
            if not extracted_name or extracted_name.lower() in ["(anonymous)", "anonymous", "n/a", "unknown"]:
                final_company_name = company_name if company_name else extracted_name
            else:
                # Use AI extracted name if it looks valid and user didn't provide specific input
                final_company_name = company_name if company_name and company_name.strip() else extracted_name
            
            # Convert to FinancialData object
            fin_data = FinancialData(
                company_name=final_company_name,
                ticker=final_company_name.upper().replace(" ", "_") if final_company_name else "UNKNOWN",
                years_analyzed=years_to_analyze,
                data_source="PDF Annual Report",
                fetch_timestamp=datetime.now().isoformat()
            )
            
            # Populate financial metrics
            fin_data.revenue = self._convert_to_float_dict(data_dict.get("revenue", {}))
            fin_data.net_income = self._convert_to_float_dict(data_dict.get("net_income", {}))
            fin_data.operating_income = self._convert_to_float_dict(data_dict.get("operating_income", {}))
            fin_data.total_assets = self._convert_to_float_dict(data_dict.get("total_assets", {}))
            fin_data.total_liabilities = self._convert_to_float_dict(data_dict.get("total_liabilities", {}))
            fin_data.shareholders_equity = self._convert_to_float_dict(data_dict.get("shareholders_equity", {}))
            fin_data.total_debt = self._convert_to_float_dict(data_dict.get("total_debt", {}))
            fin_data.cash_and_equivalents = self._convert_to_float_dict(data_dict.get("cash_and_equivalents", {}))
            fin_data.operating_cash_flow = self._convert_to_float_dict(data_dict.get("operating_cash_flow", {}))
            fin_data.free_cash_flow = self._convert_to_float_dict(data_dict.get("free_cash_flow", {}))
            fin_data.capex = self._convert_to_float_dict(data_dict.get("capex", {}))
            
            # Company info
            fin_data.sector = data_dict.get("sector", "")
            fin_data.industry = data_dict.get("industry", "")
            fin_data.market_cap = float(data_dict.get("market_cap", 0))
            fin_data.pe_ratio = float(data_dict.get("pe_ratio", 0))
            fin_data.dividend_yield = float(data_dict.get("dividend_yield", 0))
            
            # Calculate derived metrics
            self._calculate_ratios(fin_data)
            
            return fin_data
            
        except Exception as e:
            raise Exception(f"Error extracting financial data with AI: {e}")
    
    def _convert_to_float_dict(self, data: Dict) -> Dict[str, float]:
        """Convert dictionary values to float"""
        result = {}
        for key, value in data.items():
            try:
                result[str(key)] = float(value)
            except (ValueError, TypeError):
                result[str(key)] = 0.0
        return result
    
    def _calculate_ratios(self, fin_data: FinancialData):
        """Calculate financial ratios from extracted data"""
        for year in fin_data.revenue.keys():
            # ROE = Net Income / Shareholders Equity
            if year in fin_data.net_income and year in fin_data.shareholders_equity:
                if fin_data.shareholders_equity[year] != 0:
                    fin_data.roe[year] = (fin_data.net_income[year] / fin_data.shareholders_equity[year]) * 100
            
            # ROA = Net Income / Total Assets
            if year in fin_data.net_income and year in fin_data.total_assets:
                if fin_data.total_assets[year] != 0:
                    fin_data.roa[year] = (fin_data.net_income[year] / fin_data.total_assets[year]) * 100
            
            # ROCE = Operating Income / Capital Employed
            if year in fin_data.operating_income and year in fin_data.shareholders_equity and year in fin_data.total_debt:
                capital_employed = fin_data.shareholders_equity[year] + fin_data.total_debt[year]
                if capital_employed != 0:
                    fin_data.roce[year] = (fin_data.operating_income[year] / capital_employed) * 100
            
            # Debt to Equity
            if year in fin_data.total_debt and year in fin_data.shareholders_equity:
                if fin_data.shareholders_equity[year] != 0:
                    fin_data.debt_to_equity[year] = fin_data.total_debt[year] / fin_data.shareholders_equity[year]
            
            # Operating Margin
            if year in fin_data.operating_income and year in fin_data.revenue:
                if fin_data.revenue[year] != 0:
                    fin_data.operating_margin[year] = (fin_data.operating_income[year] / fin_data.revenue[year]) * 100
            
            # Net Margin
            if year in fin_data.net_income and year in fin_data.revenue:
                if fin_data.revenue[year] != 0:
                    fin_data.net_margin[year] = (fin_data.net_income[year] / fin_data.revenue[year]) * 100
            
            # Revenue Growth
            years_list = sorted(fin_data.revenue.keys(), reverse=True)
            for i in range(len(years_list) - 1):
                current_year = years_list[i]
                previous_year = years_list[i + 1]
                if fin_data.revenue[previous_year] != 0:
                    growth = ((fin_data.revenue[current_year] - fin_data.revenue[previous_year]) / 
                             fin_data.revenue[previous_year]) * 100
                    fin_data.revenue_growth[current_year] = growth
            
            # Profit Growth
            years_list = sorted(fin_data.net_income.keys(), reverse=True)
            for i in range(len(years_list) - 1):
                current_year = years_list[i]
                previous_year = years_list[i + 1]
                if fin_data.net_income[previous_year] != 0:
                    growth = ((fin_data.net_income[current_year] - fin_data.net_income[previous_year]) / 
                             fin_data.net_income[previous_year]) * 100
                    fin_data.profit_growth[current_year] = growth
    
    def parse_annual_report(
        self, 
        pdf_path: str, 
        company_name: str,
        years_to_analyze: int = 5
    ) -> FinancialData:
        """
        Main method to parse annual report PDF
        
        Args:
            pdf_path: Path to the PDF file
            company_name: Name of the company
            years_to_analyze: Number of years to extract data for
            
        Returns:
            FinancialData object with extracted metrics
        """
        # Extract text from PDF
        pdf_text = self.extract_text_from_pdf(pdf_path)
        
        if not pdf_text or len(pdf_text) < 100:
            raise Exception("Could not extract sufficient text from PDF")
        
        # Use AI to parse financial data
        fin_data = self.parse_financial_data_with_ai(pdf_text, company_name, years_to_analyze)
        
        return fin_data


def parse_multiple_reports(
    pdf_paths: List[str],
    company_name: str,
    openai_api_key: str = None
) -> FinancialData:
    """
    Parse multiple PDF annual reports (one per year) and combine data
    
    Args:
        pdf_paths: List of PDF file paths, ordered from most recent to oldest
        company_name: Name of the company
        openai_api_key: OpenAI API key for parsing
        
    Returns:
        Combined FinancialData object
    """
    parser = PDFReportParser(openai_api_key)
    
    combined_data = FinancialData(
        company_name=company_name,
        ticker=company_name.upper().replace(" ", "_"),
        years_analyzed=len(pdf_paths),
        data_source="PDF Annual Reports (Multiple)",
        fetch_timestamp=datetime.now().isoformat()
    )
    
    # Parse each PDF
    for pdf_path in pdf_paths:
        try:
            data = parser.parse_annual_report(pdf_path, company_name, 1)
            
            # Merge data
            combined_data.revenue.update(data.revenue)
            combined_data.net_income.update(data.net_income)
            combined_data.operating_income.update(data.operating_income)
            combined_data.total_assets.update(data.total_assets)
            combined_data.total_liabilities.update(data.total_liabilities)
            combined_data.shareholders_equity.update(data.shareholders_equity)
            combined_data.total_debt.update(data.total_debt)
            combined_data.cash_and_equivalents.update(data.cash_and_equivalents)
            combined_data.operating_cash_flow.update(data.operating_cash_flow)
            combined_data.free_cash_flow.update(data.free_cash_flow)
            combined_data.capex.update(data.capex)
            
            # Update company info from first report
            if not combined_data.sector:
                combined_data.sector = data.sector
                combined_data.industry = data.industry
                combined_data.market_cap = data.market_cap
                combined_data.pe_ratio = data.pe_ratio
                combined_data.dividend_yield = data.dividend_yield
                
        except Exception as e:
            print(f"Warning: Could not parse {pdf_path}: {e}")
            continue
    
    # Calculate ratios on combined data
    parser._calculate_ratios(combined_data)
    
    return combined_data
