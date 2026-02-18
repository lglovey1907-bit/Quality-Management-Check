"""
Quality Management Analysis Engine
Analyzes financial data and provides quality scores, strengths, and red flags
"""

import os
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

from openai import OpenAI

from .data_fetcher import FinancialData


class ScoreCategory(Enum):
    """Categories for quality scoring"""
    PROFITABILITY = "Profitability & Margins"
    GROWTH = "Growth & Revenue Stability"
    FINANCIAL_HEALTH = "Financial Health & Leverage"
    CASH_MANAGEMENT = "Cash Flow Management"
    CAPITAL_EFFICIENCY = "Capital Efficiency & Returns"
    QUALITY_EARNINGS = "Quality of Earnings"
    GOVERNANCE = "Management & Governance Indicators"


@dataclass
class QualityScore:
    """Individual quality score for a category"""
    category: str
    score: float  # 0-10
    weight: float
    strengths: List[str]
    concerns: List[str]
    explanation: str


@dataclass
class RedFlag:
    """Red flag identified in analysis"""
    severity: str  # "High", "Medium", "Low"
    category: str
    description: str
    impact: str
    recommendation: str


@dataclass
class QualityReport:
    """Complete quality management report"""
    company_name: str
    ticker: str
    analysis_date: str
    years_analyzed: int
    
    # Scores - default to 0, will be calculated
    overall_score: float = 0.0  # 0-10
    category_scores: List[QualityScore] = field(default_factory=list)
    
    # Findings
    key_strengths: List[str] = field(default_factory=list)
    red_flags: List[RedFlag] = field(default_factory=list)
    
    # Summary
    executive_summary: str = ""
    investment_thesis: str = ""
    risk_assessment: str = ""
    
    # Raw metrics
    metrics_summary: Dict = field(default_factory=dict)


class QualityAnalyzer:
    """
    Core analyzer for quality management assessment
    """
    
    # Weights for each category
    CATEGORY_WEIGHTS = {
        ScoreCategory.PROFITABILITY: 0.20,
        ScoreCategory.GROWTH: 0.15,
        ScoreCategory.FINANCIAL_HEALTH: 0.20,
        ScoreCategory.CASH_MANAGEMENT: 0.15,
        ScoreCategory.CAPITAL_EFFICIENCY: 0.15,
        ScoreCategory.QUALITY_EARNINGS: 0.10,
        ScoreCategory.GOVERNANCE: 0.05,
    }
    
    def __init__(self):
        pass
    
    def analyze(self, fin_data: FinancialData) -> QualityReport:
        """
        Perform comprehensive quality analysis
        """
        report = QualityReport(
            company_name=fin_data.company_name,
            ticker=fin_data.ticker,
            analysis_date=fin_data.fetch_timestamp,
            years_analyzed=fin_data.years_analyzed
        )
        
        # Analyze each category
        report.category_scores.append(self._analyze_profitability(fin_data))
        report.category_scores.append(self._analyze_growth(fin_data))
        report.category_scores.append(self._analyze_financial_health(fin_data))
        report.category_scores.append(self._analyze_cash_management(fin_data))
        report.category_scores.append(self._analyze_capital_efficiency(fin_data))
        report.category_scores.append(self._analyze_earnings_quality(fin_data))
        report.category_scores.append(self._analyze_governance(fin_data))
        
        # Calculate overall score
        report.overall_score = self._calculate_overall_score(report.category_scores)
        
        # Identify key strengths
        report.key_strengths = self._identify_key_strengths(report.category_scores)
        
        # Identify red flags
        report.red_flags = self._identify_red_flags(fin_data, report.category_scores)
        
        # Generate metrics summary
        report.metrics_summary = self._generate_metrics_summary(fin_data)
        
        return report
    
    def _analyze_profitability(self, data: FinancialData) -> QualityScore:
        """Analyze profitability metrics"""
        score = 5.0  # Base score
        strengths = []
        concerns = []
        
        # Analyze operating margins
        if data.operating_margin:
            margins = list(data.operating_margin.values())
            avg_margin = sum(margins) / len(margins) if margins else 0
            
            if avg_margin > 20:
                score += 2
                strengths.append(f"Strong operating margin of {avg_margin:.1f}%")
            elif avg_margin > 15:
                score += 1
                strengths.append(f"Healthy operating margin of {avg_margin:.1f}%")
            elif avg_margin < 5:
                score -= 2
                concerns.append(f"Low operating margin of {avg_margin:.1f}%")
            elif avg_margin < 10:
                score -= 1
                concerns.append(f"Below-average operating margin of {avg_margin:.1f}%")
            
            # Check margin trend
            if len(margins) >= 2:
                if margins[0] > margins[-1]:  # Improving (most recent first)
                    score += 0.5
                    strengths.append("Improving operating margins over time")
                elif margins[0] < margins[-1] * 0.9:  # Declining by 10%+
                    score -= 0.5
                    concerns.append("Declining operating margins")
        
        # Analyze net margins
        if data.net_margin:
            net_margins = list(data.net_margin.values())
            avg_net = sum(net_margins) / len(net_margins) if net_margins else 0
            
            if avg_net > 15:
                score += 1
                strengths.append(f"Excellent net profit margin of {avg_net:.1f}%")
            elif avg_net < 0:
                score -= 2
                concerns.append("Company is operating at a loss")
        
        # Analyze ROE
        if data.roe:
            roe_values = [v for v in data.roe.values() if isinstance(v, (int, float))]
            if roe_values:
                avg_roe = sum(roe_values) / len(roe_values)
                
                if avg_roe > 20:
                    score += 1
                    strengths.append(f"High ROE of {avg_roe:.1f}% indicates efficient equity usage")
                elif avg_roe < 10:
                    score -= 0.5
                    concerns.append(f"Low ROE of {avg_roe:.1f}%")
        
        score = max(0, min(10, score))
        
        return QualityScore(
            category=ScoreCategory.PROFITABILITY.value,
            score=score,
            weight=self.CATEGORY_WEIGHTS[ScoreCategory.PROFITABILITY],
            strengths=strengths,
            concerns=concerns,
            explanation="Assessment of profit margins, ROE, and overall profitability trends"
        )
    
    def _analyze_growth(self, data: FinancialData) -> QualityScore:
        """Analyze growth metrics"""
        score = 5.0
        strengths = []
        concerns = []
        
        # Analyze revenue growth
        if data.revenue and len(data.revenue) >= 2:
            revenues = list(data.revenue.values())
            years = list(data.revenue.keys())
            
            # Calculate CAGR
            if revenues[0] and revenues[-1] and revenues[-1] > 0:
                num_years = len(revenues) - 1
                if num_years > 0:
                    cagr = ((revenues[0] / revenues[-1]) ** (1/num_years) - 1) * 100
                    
                    if cagr > 20:
                        score += 2
                        strengths.append(f"Excellent revenue CAGR of {cagr:.1f}%")
                    elif cagr > 10:
                        score += 1
                        strengths.append(f"Strong revenue CAGR of {cagr:.1f}%")
                    elif cagr < 0:
                        score -= 2
                        concerns.append(f"Declining revenue (CAGR: {cagr:.1f}%)")
                    elif cagr < 5:
                        score -= 0.5
                        concerns.append(f"Slow revenue growth (CAGR: {cagr:.1f}%)")
            
            # Check consistency
            growth_rates = []
            for i in range(len(revenues) - 1):
                if revenues[i+1] > 0:
                    growth = (revenues[i] - revenues[i+1]) / revenues[i+1] * 100
                    growth_rates.append(growth)
            
            if growth_rates:
                # Check for consistent positive growth
                positive_years = sum(1 for g in growth_rates if g > 0)
                if positive_years == len(growth_rates):
                    score += 1
                    strengths.append("Consistent revenue growth across all analyzed years")
                elif positive_years < len(growth_rates) / 2:
                    concerns.append("Inconsistent revenue growth")
        
        # Analyze profit growth
        if data.net_income and len(data.net_income) >= 2:
            profits = list(data.net_income.values())
            
            if profits[0] and profits[-1] and profits[-1] > 0 and profits[0] > 0:
                num_years = len(profits) - 1
                if num_years > 0:
                    profit_cagr = ((profits[0] / profits[-1]) ** (1/num_years) - 1) * 100
                    
                    if profit_cagr > 25:
                        score += 1
                        strengths.append(f"Strong profit growth (CAGR: {profit_cagr:.1f}%)")
                    elif profit_cagr < -10:
                        score -= 1.5
                        concerns.append(f"Declining profits (CAGR: {profit_cagr:.1f}%)")
        
        score = max(0, min(10, score))
        
        return QualityScore(
            category=ScoreCategory.GROWTH.value,
            score=score,
            weight=self.CATEGORY_WEIGHTS[ScoreCategory.GROWTH],
            strengths=strengths,
            concerns=concerns,
            explanation="Assessment of revenue and profit growth trends and consistency"
        )
    
    def _analyze_financial_health(self, data: FinancialData) -> QualityScore:
        """Analyze financial health and leverage"""
        score = 5.0
        strengths = []
        concerns = []
        
        # Analyze debt to equity
        if data.debt_to_equity:
            de_values = list(data.debt_to_equity.values())
            if de_values:
                latest_de = de_values[0] if de_values else 0
                avg_de = sum(de_values) / len(de_values)
                
                if avg_de < 0.3:
                    score += 2
                    strengths.append(f"Very low debt levels (D/E: {avg_de:.2f})")
                elif avg_de < 0.5:
                    score += 1
                    strengths.append(f"Conservative debt levels (D/E: {avg_de:.2f})")
                elif avg_de > 1.5:
                    score -= 2
                    concerns.append(f"High leverage (D/E: {avg_de:.2f})")
                elif avg_de > 1:
                    score -= 1
                    concerns.append(f"Elevated debt levels (D/E: {avg_de:.2f})")
                
                # Check if debt is increasing
                if len(de_values) >= 2 and de_values[0] > de_values[-1] * 1.3:
                    concerns.append("Increasing leverage over time")
                    score -= 0.5
        
        # Analyze interest coverage
        if data.interest_coverage:
            ic_values = list(data.interest_coverage.values())
            if ic_values:
                avg_ic = sum(ic_values) / len(ic_values)
                
                if avg_ic > 10:
                    score += 1
                    strengths.append(f"Excellent interest coverage ({avg_ic:.1f}x)")
                elif avg_ic < 2:
                    score -= 2
                    concerns.append(f"Low interest coverage ({avg_ic:.1f}x) - potential debt servicing risk")
                elif avg_ic < 3:
                    score -= 1
                    concerns.append(f"Moderate interest coverage ({avg_ic:.1f}x)")
        
        # Analyze current ratio
        if data.current_ratio:
            cr_values = list(data.current_ratio.values())
            if cr_values:
                avg_cr = sum(cr_values) / len(cr_values)
                
                if avg_cr > 2:
                    score += 0.5
                    strengths.append(f"Strong liquidity position (Current Ratio: {avg_cr:.2f})")
                elif avg_cr < 1:
                    score -= 1.5
                    concerns.append(f"Liquidity concerns (Current Ratio: {avg_cr:.2f})")
        
        # Check total debt vs equity/assets
        if data.total_debt and data.shareholders_equity:
            latest_debt = list(data.total_debt.values())[0] if data.total_debt else 0
            latest_equity = list(data.shareholders_equity.values())[0] if data.shareholders_equity else 0
            
            if latest_debt == 0 or (latest_equity > 0 and latest_debt / latest_equity < 0.1):
                score += 1
                strengths.append("Debt-free or minimal debt balance sheet")
        
        score = max(0, min(10, score))
        
        return QualityScore(
            category=ScoreCategory.FINANCIAL_HEALTH.value,
            score=score,
            weight=self.CATEGORY_WEIGHTS[ScoreCategory.FINANCIAL_HEALTH],
            strengths=strengths,
            concerns=concerns,
            explanation="Assessment of leverage, liquidity, and overall financial stability"
        )
    
    def _analyze_cash_management(self, data: FinancialData) -> QualityScore:
        """Analyze cash flow management"""
        score = 5.0
        strengths = []
        concerns = []
        
        # Analyze operating cash flow
        if data.operating_cash_flow:
            ocf_values = list(data.operating_cash_flow.values())
            if ocf_values:
                # Check if consistently positive
                positive_ocf = sum(1 for v in ocf_values if v > 0)
                
                if positive_ocf == len(ocf_values):
                    score += 2
                    strengths.append("Consistently positive operating cash flow")
                elif positive_ocf < len(ocf_values) / 2:
                    score -= 2
                    concerns.append("Inconsistent or negative operating cash flows")
                
                # Check OCF trend
                if len(ocf_values) >= 2:
                    if ocf_values[0] > ocf_values[-1] * 1.5:
                        score += 0.5
                        strengths.append("Growing operating cash flow")
                    elif ocf_values[0] < ocf_values[-1] * 0.7:
                        concerns.append("Declining operating cash flow")
        
        # Compare OCF to Net Income (quality check)
        if data.operating_cash_flow and data.net_income:
            ocf_list = list(data.operating_cash_flow.values())
            ni_list = list(data.net_income.values())
            
            if ocf_list and ni_list:
                years_with_both = min(len(ocf_list), len(ni_list))
                
                ocf_greater = 0
                for i in range(years_with_both):
                    if ni_list[i] > 0 and ocf_list[i] > ni_list[i]:
                        ocf_greater += 1
                
                if ocf_greater == years_with_both:
                    score += 1
                    strengths.append("OCF consistently exceeds net income - high earnings quality")
                elif ocf_greater < years_with_both / 2 and all(n > 0 for n in ni_list[:years_with_both]):
                    score -= 1
                    concerns.append("Net income often exceeds OCF - potential earnings quality issue")
        
        # Analyze free cash flow
        if data.free_cash_flow:
            fcf_values = list(data.free_cash_flow.values())
            if fcf_values:
                positive_fcf = sum(1 for v in fcf_values if v > 0)
                
                if positive_fcf == len(fcf_values):
                    score += 1
                    strengths.append("Consistently positive free cash flow")
                elif positive_fcf == 0:
                    score -= 1
                    concerns.append("Negative free cash flow across all years")
        
        score = max(0, min(10, score))
        
        return QualityScore(
            category=ScoreCategory.CASH_MANAGEMENT.value,
            score=score,
            weight=self.CATEGORY_WEIGHTS[ScoreCategory.CASH_MANAGEMENT],
            strengths=strengths,
            concerns=concerns,
            explanation="Assessment of cash flow generation and quality"
        )
    
    def _analyze_capital_efficiency(self, data: FinancialData) -> QualityScore:
        """Analyze capital efficiency metrics"""
        score = 5.0
        strengths = []
        concerns = []
        
        # Analyze ROCE
        if data.roce:
            roce_values = [v for v in data.roce.values() if isinstance(v, (int, float))]
            if roce_values:
                avg_roce = sum(roce_values) / len(roce_values)
                
                if avg_roce > 20:
                    score += 2
                    strengths.append(f"Excellent ROCE of {avg_roce:.1f}% - efficient capital deployment")
                elif avg_roce > 15:
                    score += 1
                    strengths.append(f"Good ROCE of {avg_roce:.1f}%")
                elif avg_roce < 8:
                    score -= 1.5
                    concerns.append(f"Low ROCE of {avg_roce:.1f}% - poor capital efficiency")
                elif avg_roce < 10:
                    score -= 0.5
                    concerns.append(f"Below-average ROCE of {avg_roce:.1f}%")
                
                # Check consistency
                if len(roce_values) >= 3:
                    if all(r > 15 for r in roce_values):
                        strengths.append("Consistently high returns on capital employed")
                        score += 0.5
        
        # Analyze ROA
        if data.roa:
            roa_values = list(data.roa.values())
            if roa_values:
                avg_roa = sum(roa_values) / len(roa_values)
                
                if avg_roa > 10:
                    score += 1
                    strengths.append(f"Strong ROA of {avg_roa:.1f}%")
                elif avg_roa < 3:
                    score -= 1
                    concerns.append(f"Low ROA of {avg_roa:.1f}%")
        
        # Analyze asset turnover (revenue/assets)
        if data.revenue and data.total_assets:
            years = set(data.revenue.keys()) & set(data.total_assets.keys())
            if years:
                turnovers = []
                for year in years:
                    if data.total_assets[year] > 0:
                        turnovers.append(data.revenue[year] / data.total_assets[year])
                
                if turnovers:
                    avg_turnover = sum(turnovers) / len(turnovers)
                    
                    if avg_turnover > 1.5:
                        strengths.append(f"High asset turnover ({avg_turnover:.2f}x)")
                    elif avg_turnover < 0.3:
                        concerns.append(f"Low asset utilization ({avg_turnover:.2f}x)")
        
        score = max(0, min(10, score))
        
        return QualityScore(
            category=ScoreCategory.CAPITAL_EFFICIENCY.value,
            score=score,
            weight=self.CATEGORY_WEIGHTS[ScoreCategory.CAPITAL_EFFICIENCY],
            strengths=strengths,
            concerns=concerns,
            explanation="Assessment of return on capital and asset efficiency"
        )
    
    def _analyze_earnings_quality(self, data: FinancialData) -> QualityScore:
        """Analyze quality and sustainability of earnings"""
        score = 5.0
        strengths = []
        concerns = []
        
        # Accruals analysis (OCF vs Net Income)
        if data.operating_cash_flow and data.net_income:
            ocf_list = list(data.operating_cash_flow.values())
            ni_list = list(data.net_income.values())
            
            if ocf_list and ni_list:
                years = min(len(ocf_list), len(ni_list))
                
                # Calculate accruals ratio
                total_accruals = 0
                total_ocf = 0
                for i in range(years):
                    if ni_list[i] > 0:
                        accrual = ni_list[i] - ocf_list[i]
                        total_accruals += accrual
                        total_ocf += ocf_list[i]
                
                if total_ocf > 0:
                    accrual_ratio = total_accruals / total_ocf
                    
                    if accrual_ratio < 0:  # Negative accruals = good
                        score += 2
                        strengths.append("High cash conversion - earnings backed by cash")
                    elif accrual_ratio > 0.5:
                        score -= 2
                        concerns.append("High accruals - earnings quality concerns")
                    elif accrual_ratio > 0.3:
                        score -= 1
                        concerns.append("Moderate accruals in earnings")
        
        # Earnings volatility
        if data.net_income and len(data.net_income) >= 3:
            profits = list(data.net_income.values())
            avg_profit = sum(profits) / len(profits)
            
            if avg_profit > 0:
                variance = sum((p - avg_profit) ** 2 for p in profits) / len(profits)
                std_dev = variance ** 0.5
                cv = std_dev / avg_profit  # Coefficient of variation
                
                if cv < 0.2:
                    score += 1
                    strengths.append("Stable and predictable earnings")
                elif cv > 0.5:
                    score -= 1
                    concerns.append("High earnings volatility")
        
        # Revenue concentration risk (implied by margin stability)
        if data.operating_margin and len(data.operating_margin) >= 2:
            margins = list(data.operating_margin.values())
            margin_range = max(margins) - min(margins)
            
            if margin_range < 3:
                score += 0.5
                strengths.append("Stable margins indicating consistent business model")
            elif margin_range > 10:
                concerns.append("Volatile margins - business model stability concerns")
        
        score = max(0, min(10, score))
        
        return QualityScore(
            category=ScoreCategory.QUALITY_EARNINGS.value,
            score=score,
            weight=self.CATEGORY_WEIGHTS[ScoreCategory.QUALITY_EARNINGS],
            strengths=strengths,
            concerns=concerns,
            explanation="Assessment of earnings sustainability and accounting quality"
        )
    
    def _analyze_governance(self, data: FinancialData) -> QualityScore:
        """Analyze governance indicators (limited from financial data)"""
        score = 5.0
        strengths = []
        concerns = []
        
        # Dividend policy as governance indicator
        if data.dividend_yield:
            if data.dividend_yield > 2:
                score += 1
                strengths.append(f"Regular dividend payer ({data.dividend_yield:.1f}% yield)")
            elif data.dividend_yield > 0.5:
                strengths.append("Maintains dividend payments")
        
        # Consistent reporting (having all years of data)
        if data.revenue and len(data.revenue) >= data.years_analyzed:
            score += 0.5
            strengths.append("Consistent financial reporting")
        
        # Capital allocation (FCF usage)
        if data.free_cash_flow:
            fcf_values = list(data.free_cash_flow.values())
            positive_fcf = sum(1 for v in fcf_values if v > 0)
            
            if positive_fcf == len(fcf_values):
                score += 1
                strengths.append("Positive FCF indicates disciplined capital allocation")
        
        # Check for any signs of aggressive accounting
        if data.net_income and data.operating_cash_flow:
            ni_list = list(data.net_income.values())
            ocf_list = list(data.operating_cash_flow.values())
            
            # Multiple years where NI >> OCF is a concern
            concern_years = 0
            for i in range(min(len(ni_list), len(ocf_list))):
                if ni_list[i] > 0 and ocf_list[i] > 0:
                    if ni_list[i] > ocf_list[i] * 1.5:
                        concern_years += 1
            
            if concern_years >= 2:
                score -= 1
                concerns.append("Pattern of net income significantly exceeding cash flow")
        
        score = max(0, min(10, score))
        
        return QualityScore(
            category=ScoreCategory.GOVERNANCE.value,
            score=score,
            weight=self.CATEGORY_WEIGHTS[ScoreCategory.GOVERNANCE],
            strengths=strengths,
            concerns=concerns,
            explanation="Assessment of management quality through financial indicators"
        )
    
    def _calculate_overall_score(self, category_scores: List[QualityScore]) -> float:
        """Calculate weighted overall score"""
        total_score = 0
        total_weight = 0
        
        for cs in category_scores:
            total_score += cs.score * cs.weight
            total_weight += cs.weight
        
        if total_weight > 0:
            return round(total_score / total_weight, 1)
        return 5.0
    
    def _identify_key_strengths(self, category_scores: List[QualityScore]) -> List[str]:
        """Identify top strengths from analysis"""
        all_strengths = []
        
        # Prioritize strengths from high-scoring categories
        sorted_scores = sorted(category_scores, key=lambda x: x.score, reverse=True)
        
        for cs in sorted_scores:
            for strength in cs.strengths:
                all_strengths.append(f"[{cs.category}] {strength}")
        
        return all_strengths[:8]  # Top 8 strengths
    
    def _identify_red_flags(self, data: FinancialData, category_scores: List[QualityScore]) -> List[RedFlag]:
        """Identify red flags from analysis"""
        red_flags = []
        
        # Check for critical red flags
        
        # 1. Declining revenue for multiple years
        if data.revenue and len(data.revenue) >= 3:
            revenues = list(data.revenue.values())
            declining_years = 0
            for i in range(len(revenues) - 1):
                if revenues[i] < revenues[i+1]:
                    declining_years += 1
            
            if declining_years >= 2:
                red_flags.append(RedFlag(
                    severity="High",
                    category="Growth",
                    description="Revenue declining for multiple consecutive years",
                    impact="May indicate loss of competitive position or market share",
                    recommendation="Investigate reasons for revenue decline and management's turnaround plans"
                ))
        
        # 2. Negative or declining profitability
        if data.net_income:
            profits = list(data.net_income.values())
            if all(p < 0 for p in profits):
                red_flags.append(RedFlag(
                    severity="High",
                    category="Profitability",
                    description="Company has been consistently unprofitable",
                    impact="Cash burn may require additional funding, diluting shareholders",
                    recommendation="Assess path to profitability and cash runway"
                ))
        
        # 3. High and increasing debt
        if data.debt_to_equity:
            de_values = list(data.debt_to_equity.values())
            if de_values and de_values[0] > 2:
                severity = "High" if de_values[0] > 3 else "Medium"
                red_flags.append(RedFlag(
                    severity=severity,
                    category="Financial Health",
                    description=f"High debt-to-equity ratio of {de_values[0]:.2f}",
                    impact="High interest burden and vulnerability to rising rates",
                    recommendation="Monitor debt covenants and refinancing risk"
                ))
        
        # 4. Negative operating cash flow
        if data.operating_cash_flow:
            ocf_values = list(data.operating_cash_flow.values())
            negative_ocf = sum(1 for v in ocf_values if v < 0)
            
            if negative_ocf >= len(ocf_values) / 2:
                red_flags.append(RedFlag(
                    severity="High",
                    category="Cash Management",
                    description="Negative operating cash flow in multiple years",
                    impact="Core business not generating cash - sustainability concerns",
                    recommendation="Analyze working capital and cash conversion cycle"
                ))
        
        # 5. Earnings quality concern
        if data.net_income and data.operating_cash_flow:
            ni_list = list(data.net_income.values())
            ocf_list = list(data.operating_cash_flow.values())
            
            concern_years = 0
            for i in range(min(len(ni_list), len(ocf_list))):
                if ni_list[i] > 0 and ocf_list[i] > 0:
                    if ni_list[i] > ocf_list[i] * 2:
                        concern_years += 1
            
            if concern_years >= 2:
                red_flags.append(RedFlag(
                    severity="Medium",
                    category="Earnings Quality",
                    description="Net income significantly exceeds operating cash flow",
                    impact="Earnings may include non-cash items or aggressive accounting",
                    recommendation="Review receivables aging and revenue recognition policies"
                ))
        
        # 6. Add concerns from low-scoring categories
        for cs in category_scores:
            if cs.score < 4:
                for concern in cs.concerns[:2]:
                    red_flags.append(RedFlag(
                        severity="Medium",
                        category=cs.category,
                        description=concern,
                        impact=f"Below-average performance in {cs.category.lower()}",
                        recommendation=f"Deep-dive analysis of {cs.category.lower()} required"
                    ))
        
        return red_flags
    
    def _generate_metrics_summary(self, data: FinancialData) -> Dict:
        """Generate summary of key metrics"""
        summary = {
            "company_info": {
                "name": data.company_name,
                "ticker": data.ticker,
                "sector": data.sector,
                "industry": data.industry,
                "market_cap": data.market_cap,
            },
            "valuation": {
                "pe_ratio": data.pe_ratio,
                "pb_ratio": data.pb_ratio,
                "dividend_yield": data.dividend_yield,
            },
            "revenue_trend": data.revenue,
            "profit_trend": data.net_income,
            "margins": {
                "operating_margin": data.operating_margin,
                "net_margin": data.net_margin,
            },
            "returns": {
                "roe": data.roe,
                "roce": data.roce,
                "roa": data.roa,
            },
            "leverage": {
                "debt_to_equity": data.debt_to_equity,
            },
            "cash_flow": {
                "operating_cf": data.operating_cash_flow,
                "free_cf": data.free_cash_flow,
            },
        }
        
        return summary


class AIEnhancedAnalyzer:
    """
    AI-enhanced analyzer using LLM for deeper insights
    """
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = None
        if self.api_key:
            self.client = OpenAI(api_key=self.api_key)
        self.base_analyzer = QualityAnalyzer()
    
    def analyze(self, fin_data: FinancialData) -> QualityReport:
        """Perform AI-enhanced analysis"""
        # First do base analysis
        report = self.base_analyzer.analyze(fin_data)
        
        # Then enhance with AI insights
        if self.client:
            report = self._enhance_with_ai(fin_data, report)
        
        return report
    
    def _enhance_with_ai(self, fin_data: FinancialData, report: QualityReport) -> QualityReport:
        """Enhance report with AI-generated insights"""
        try:
            # Prepare context for AI
            context = self._prepare_ai_context(fin_data, report)
            
            # Generate executive summary
            report.executive_summary = self._generate_executive_summary(context)
            
            # Generate investment thesis
            report.investment_thesis = self._generate_investment_thesis(context)
            
            # Generate risk assessment
            report.risk_assessment = self._generate_risk_assessment(context)
            
        except Exception as e:
            print(f"AI enhancement failed: {e}")
            # Fall back to basic summaries
            report.executive_summary = self._generate_basic_summary(report)
            report.investment_thesis = self._generate_basic_thesis(report)
            report.risk_assessment = self._generate_basic_risks(report)
        
        return report
    
    def _prepare_ai_context(self, fin_data: FinancialData, report: QualityReport) -> str:
        """Prepare context string for AI"""
        context = f"""
Company: {fin_data.company_name} ({fin_data.ticker})
Sector: {fin_data.sector}
Industry: {fin_data.industry}
Years Analyzed: {fin_data.years_analyzed}

FINANCIAL METRICS:
- Revenue Trend: {json.dumps(fin_data.revenue)}
- Net Income Trend: {json.dumps(fin_data.net_income)}
- Operating Margin: {json.dumps(fin_data.operating_margin)}
- ROE: {json.dumps(fin_data.roe)}
- ROCE: {json.dumps(fin_data.roce)}
- Debt-to-Equity: {json.dumps(fin_data.debt_to_equity)}
- Operating Cash Flow: {json.dumps(fin_data.operating_cash_flow)}
- Free Cash Flow: {json.dumps(fin_data.free_cash_flow)}

QUALITY SCORES:
- Overall Score: {report.overall_score}/10
"""
        for cs in report.category_scores:
            context += f"- {cs.category}: {cs.score}/10\n"
        
        context += "\nKEY STRENGTHS:\n"
        for s in report.key_strengths[:5]:
            context += f"- {s}\n"
        
        context += "\nRED FLAGS:\n"
        for rf in report.red_flags[:5]:
            context += f"- [{rf.severity}] {rf.description}\n"
        
        return context
    
    def _generate_executive_summary(self, context: str) -> str:
        """Generate executive summary using AI"""
        prompt = f"""Based on the following financial analysis, write a concise executive summary (200-250 words) for a research analyst. Focus on the key takeaways about the company's quality and investment merit.

{context}

Write in a professional, analytical tone. Include the overall quality score and highlight the most important findings."""
        
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a senior financial analyst specializing in quality management assessment. Provide clear, actionable insights."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=400,
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
    
    def _generate_investment_thesis(self, context: str) -> str:
        """Generate investment thesis using AI"""
        prompt = f"""Based on the following financial analysis, write a brief investment thesis (150-200 words). Include:
1. Core investment case (bull case)
2. Key risks to the thesis
3. Suitable investor profile

{context}

Be balanced but actionable."""
        
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a senior financial analyst. Provide practical investment guidance."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
    
    def _generate_risk_assessment(self, context: str) -> str:
        """Generate risk assessment using AI"""
        prompt = f"""Based on the following financial analysis, write a focused risk assessment (150-200 words). Prioritize the most material risks and their potential impact on the investment.

{context}

Include both quantifiable risks from the data and qualitative risks implied by the analysis."""
        
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a risk analyst. Focus on material risks with specific implications."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
    
    def _generate_basic_summary(self, report: QualityReport) -> str:
        """Generate basic summary without AI"""
        return f"""
{report.company_name} ({report.ticker}) received an overall quality score of {report.overall_score}/10 
based on {report.years_analyzed} years of financial data analysis. 

The analysis evaluated profitability, growth, financial health, cash management, capital efficiency, 
earnings quality, and governance indicators.

Top strengths: {', '.join(report.key_strengths[:3]) if report.key_strengths else 'See detailed analysis'}
Key concerns: {len(report.red_flags)} red flags identified requiring attention.
""".strip()
    
    def _generate_basic_thesis(self, report: QualityReport) -> str:
        """Generate basic thesis without AI"""
        quality_level = "high" if report.overall_score >= 7 else "moderate" if report.overall_score >= 5 else "concerning"
        return f"""
{report.company_name} demonstrates {quality_level} quality characteristics with a score of {report.overall_score}/10.
Investors should consider the identified strengths and red flags in their analysis.
Further due diligence recommended on specific concerns identified in this report.
""".strip()
    
    def _generate_basic_risks(self, report: QualityReport) -> str:
        """Generate basic risk assessment without AI"""
        risks = [f"- {rf.description} ({rf.severity} severity)" for rf in report.red_flags[:5]]
        return f"""
Key risks identified:
{chr(10).join(risks) if risks else '- No critical red flags identified'}

Monitor these factors as they may impact future performance and investment returns.
""".strip()
