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
class ManagementQualityAssessment:
    """Comprehensive management quality evaluation"""
    # 1. Management Guidance vs Reality
    guidance_vs_reality: Dict[str, str] = field(default_factory=dict)  # metric: achievement status
    achievement_rating: str = ""  # Achieved/Partially Achieved/Not Achieved/Over-promised
    
    # 2. Consistency & Honesty
    narrative_consistency: str = ""  # High/Medium/Low
    accepts_mistakes: bool = False
    external_blame_pattern: bool = False
    
    # 3. Visibility of Business
    business_visibility: str = ""  # High/Medium/Low
    clarity_score: int = 0  # 1-10
    provides_numbers: bool = False
    
    # 4. Vision & Long-Term Thinking
    vision_quality: str = ""  # Excellent/Good/Average/Weak
    long_term_focus: bool = False
    strategic_initiatives: List[str] = field(default_factory=list)
    
    # 5. Capital Allocation Skill
    capital_allocation_rating: str = ""  # Excellent/Good/Average/Poor
    allocation_analysis: str = ""
    bad_acquisitions: List[str] = field(default_factory=list)
    
    # 6. Shareholder Respect
    communication_quality: str = ""  # Excellent/Good/Average/Poor
    transparency_rating: str = ""  # High/Medium/Low
    answers_tough_questions: bool = False
    
    # 7. Red Flags
    management_red_flags: List[str] = field(default_factory=list)
    
    # 8. Overall Management Score
    management_score: float = 0.0  # 0-10
    management_category: str = ""  # Excellent/Good/Average/Weak
    
    # Detailed analysis
    detailed_analysis: str = ""


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
    
    # Management Quality Assessment
    management_quality_assessment: Optional['ManagementQualityAssessment'] = None
    
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
        
        # Build detailed explanation with figures
        explanation_parts = []
        
        # Add operating margin analysis
        if data.operating_margin:
            margins = list(data.operating_margin.values())
            avg_margin = sum(margins) / len(margins) if margins else 0
            trend = "improving" if len(margins) >= 2 and margins[0] > margins[-1] else "stable" if len(margins) >= 2 and abs(margins[0] - margins[-1]) < 1 else "declining"
            explanation_parts.append(f"Operating Margin: {avg_margin:.1f}% average over {len(margins)} years ({trend} trend)")
        
        # Add net margin analysis
        if data.net_margin:
            net_margins = list(data.net_margin.values())
            avg_net = sum(net_margins) / len(net_margins) if net_margins else 0
            explanation_parts.append(f"Net Profit Margin: {avg_net:.1f}% average")
        
        # Add ROE analysis
        if data.roe:
            roe_values = [v for v in data.roe.values() if isinstance(v, (int, float))]
            if roe_values:
                avg_roe = sum(roe_values) / len(roe_values)
                explanation_parts.append(f"Return on Equity (ROE): {avg_roe:.1f}% average, indicating {'excellent' if avg_roe > 20 else 'good' if avg_roe > 15 else 'moderate'} capital efficiency")
        
        # Combine into detailed explanation
        if explanation_parts:
            detailed_explanation = "Profitability Analysis: " + "; ".join(explanation_parts) + f". Overall profitability is {'excellent' if score >= 7.5 else 'strong' if score >= 6.5 else 'moderate' if score >= 5.5 else 'concerning'}."
        else:
            detailed_explanation = "Assessment of profit margins, ROE, and overall profitability trends."
        
        return QualityScore(
            category=ScoreCategory.PROFITABILITY.value,
            score=score,
            weight=self.CATEGORY_WEIGHTS[ScoreCategory.PROFITABILITY],
            strengths=strengths,
            concerns=concerns,
            explanation=detailed_explanation
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
        
        # Build detailed explanation with figures
        explanation_parts = []
        
        # Add revenue growth analysis
        if data.revenue and len(data.revenue) >= 2:
            revenues = list(data.revenue.values())
            if revenues[0] and revenues[-1] and revenues[-1] > 0:
                num_years = len(revenues) - 1
                if num_years > 0:
                    cagr = ((revenues[0] / revenues[-1]) ** (1/num_years) - 1) * 100
                    explanation_parts.append(f"Revenue CAGR: {cagr:.1f}% over {num_years} years")
                    
                    # Add consistency info
                    growth_rates = []
                    for i in range(len(revenues) - 1):
                        if revenues[i+1] > 0:
                            growth = (revenues[i] - revenues[i+1]) / revenues[i+1] * 100
                            growth_rates.append(growth)
                    
                    if growth_rates:
                        positive_years = sum(1 for g in growth_rates if g > 0)
                        explanation_parts.append(f"Growth consistency: {positive_years}/{len(growth_rates)} years positive")
        
        # Add profit growth analysis
        if data.net_income and len(data.net_income) >= 2:
            profits = list(data.net_income.values())
            if profits[0] and profits[-1] and profits[-1] > 0 and profits[0] > 0:
                num_years = len(profits) - 1
                if num_years > 0:
                    profit_cagr = ((profits[0] / profits[-1]) ** (1/num_years) - 1) * 100
                    explanation_parts.append(f"Profit CAGR: {profit_cagr:.1f}%")
        
        # Combine into detailed explanation
        if explanation_parts:
            detailed_explanation = "Growth & Revenue Stability: " + "; ".join(explanation_parts) + f". Overall growth momentum is {'excellent' if score >= 7.5 else 'strong' if score >= 6.5 else 'moderate' if score >= 5.5 else 'weak'}."
        else:
            detailed_explanation = "Assessment of revenue and profit growth trends and consistency."
        
        return QualityScore(
            category=ScoreCategory.GROWTH.value,
            score=score,
            weight=self.CATEGORY_WEIGHTS[ScoreCategory.GROWTH],
            strengths=strengths,
            concerns=concerns,
            explanation=detailed_explanation
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
        
        # Build detailed explanation with figures
        explanation_parts = []
        
        # Add debt to equity analysis
        if data.debt_to_equity:
            de_values = list(data.debt_to_equity.values())
            if de_values:
                avg_de = sum(de_values) / len(de_values)
                latest_de = de_values[0]
                trend = "increasing" if len(de_values) >= 2 and de_values[0] > de_values[-1] * 1.1 else "stable"
                explanation_parts.append(f"Debt-to-Equity: {latest_de:.2f} (avg: {avg_de:.2f}, {trend})")
        
        # Add interest coverage analysis
        if data.interest_coverage:
            ic_values = list(data.interest_coverage.values())
            if ic_values:
                avg_ic = sum(ic_values) / len(ic_values)
                explanation_parts.append(f"Interest Coverage: {avg_ic:.1f}x (debt servicing {'comfortable' if avg_ic > 5 else 'manageable' if avg_ic > 3 else 'concerning'})")
        
        # Add current ratio analysis
        if data.current_ratio:
            cr_values = list(data.current_ratio.values())
            if cr_values:
                avg_cr = sum(cr_values) / len(cr_values)
                explanation_parts.append(f"Current Ratio: {avg_cr:.2f} ({'strong' if avg_cr > 2 else 'adequate' if avg_cr > 1.5 else 'weak'} liquidity)")
        
        # Combine into detailed explanation
        if explanation_parts:
            detailed_explanation = "Financial Health & Leverage: " + "; ".join(explanation_parts) + f". Overall financial stability is {'excellent' if score >= 7.5 else 'strong' if score >= 6.5 else 'moderate' if score >= 5.5 else 'concerning'}."
        else:
            detailed_explanation = "Assessment of leverage, liquidity, and overall financial stability."
        
        return QualityScore(
            category=ScoreCategory.FINANCIAL_HEALTH.value,
            score=score,
            weight=self.CATEGORY_WEIGHTS[ScoreCategory.FINANCIAL_HEALTH],
            strengths=strengths,
            concerns=concerns,
            explanation=detailed_explanation
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
        
        # Build detailed explanation with figures
        explanation_parts = []
        
        # Add operating cash flow analysis
        if data.operating_cash_flow:
            ocf_values = list(data.operating_cash_flow.values())
            if ocf_values:
                positive_ocf = sum(1 for v in ocf_values if v > 0)
                avg_ocf = sum(ocf_values) / len(ocf_values) / 1e6 if ocf_values else 0  # Convert to millions
                explanation_parts.append(f"Operating Cash Flow: {positive_ocf}/{len(ocf_values)} years positive (avg: ${avg_ocf:.1f}M)")
        
        # Add OCF to Net Income comparison
        if data.operating_cash_flow and data.net_income:
            ocf_list = list(data.operating_cash_flow.values())
            ni_list = list(data.net_income.values())
            
            if ocf_list and ni_list:
                years_with_both = min(len(ocf_list), len(ni_list))
                ocf_greater = sum(1 for i in range(years_with_both) if ni_list[i] > 0 and ocf_list[i] > ni_list[i])
                explanation_parts.append(f"OCF exceeds Net Income in {ocf_greater}/{years_with_both} years ({'strong' if ocf_greater == years_with_both else 'moderate'} earnings quality)")
        
        # Add free cash flow analysis
        if data.free_cash_flow:
            fcf_values = list(data.free_cash_flow.values())
            if fcf_values:
                positive_fcf = sum(1 for v in fcf_values if v > 0)
                explanation_parts.append(f"Free Cash Flow: {positive_fcf}/{len(fcf_values)} years positive")
        
        # Combine into detailed explanation
        if explanation_parts:
            detailed_explanation = "Cash Flow Management: " + "; ".join(explanation_parts) + f". Overall cash generation is {'excellent' if score >= 7.5 else 'strong' if score >= 6.5 else 'moderate' if score >= 5.5 else 'weak'}."
        else:
            detailed_explanation = "Assessment of cash flow generation and quality."
        
        return QualityScore(
            category=ScoreCategory.CASH_MANAGEMENT.value,
            score=score,
            weight=self.CATEGORY_WEIGHTS[ScoreCategory.CASH_MANAGEMENT],
            strengths=strengths,
            concerns=concerns,
            explanation=detailed_explanation
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
        
        # Build detailed explanation with figures
        explanation_parts = []
        
        # Add ROCE analysis
        if data.roce:
            roce_values = [v for v in data.roce.values() if isinstance(v, (int, float))]
            if roce_values:
                avg_roce = sum(roce_values) / len(roce_values)
                consistency = "consistent" if len(roce_values) >= 3 and all(r > 15 for r in roce_values) else "variable"
                explanation_parts.append(f"Return on Capital Employed (ROCE): {avg_roce:.1f}% average ({consistency})")
        
        # Add ROA analysis
        if data.roa:
            roa_values = list(data.roa.values())
            if roa_values:
                avg_roa = sum(roa_values) / len(roa_values)
                explanation_parts.append(f"Return on Assets (ROA): {avg_roa:.1f}% average")
        
        # Add asset turnover analysis
        if data.revenue and data.total_assets:
            years = set(data.revenue.keys()) & set(data.total_assets.keys())
            if years:
                turnovers = []
                for year in years:
                    if data.total_assets[year] > 0:
                        turnovers.append(data.revenue[year] / data.total_assets[year])
                
                if turnovers:
                    avg_turnover = sum(turnovers) / len(turnovers)
                    explanation_parts.append(f"Asset Turnover: {avg_turnover:.2f}x ({'efficient' if avg_turnover > 1.0 else 'moderate'} utilization)")
        
        # Combine into detailed explanation
        if explanation_parts:
            detailed_explanation = "Capital Efficiency & Returns: " + "; ".join(explanation_parts) + f". Overall capital deployment is {'excellent' if score >= 7.5 else 'strong' if score >= 6.5 else 'moderate' if score >= 5.5 else 'inefficient'}."
        else:
            detailed_explanation = "Assessment of return on capital and asset efficiency."
        
        return QualityScore(
            category=ScoreCategory.CAPITAL_EFFICIENCY.value,
            score=score,
            weight=self.CATEGORY_WEIGHTS[ScoreCategory.CAPITAL_EFFICIENCY],
            strengths=strengths,
            concerns=concerns,
            explanation=detailed_explanation
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
        
        # Build detailed explanation with figures
        explanation_parts = []
        
        # Add accruals analysis
        if data.operating_cash_flow and data.net_income:
            ocf_list = list(data.operating_cash_flow.values())
            ni_list = list(data.net_income.values())
            
            if ocf_list and ni_list:
                years = min(len(ocf_list), len(ni_list))
                total_accruals = sum(ni_list[i] - ocf_list[i] for i in range(years) if ni_list[i] > 0)
                total_ocf = sum(ocf_list)
                
                if total_ocf > 0:
                    accrual_ratio = total_accruals / total_ocf
                    explanation_parts.append(f"Accruals Ratio: {accrual_ratio:.2f} ({'low - high cash quality' if accrual_ratio < 0.1 else 'moderate' if accrual_ratio < 0.3 else 'high - quality concerns'})")
        
        # Add earnings volatility analysis
        if data.net_income and len(data.net_income) >= 3:
            profits = list(data.net_income.values())
            avg_profit = sum(profits) / len(profits)
            
            if avg_profit > 0:
                variance = sum((p - avg_profit) ** 2 for p in profits) / len(profits)
                std_dev = variance ** 0.5
                cv = std_dev / avg_profit
                explanation_parts.append(f"Earnings Volatility (CV): {cv:.2f} ({'stable' if cv < 0.2 else 'moderate' if cv < 0.5 else 'volatile'})")
        
        # Add margin stability analysis
        if data.operating_margin and len(data.operating_margin) >= 2:
            margins = list(data.operating_margin.values())
            margin_range = max(margins) - min(margins)
            explanation_parts.append(f"Margin Stability: {margin_range:.1f}% range ({'consistent' if margin_range < 3 else 'variable' if margin_range < 10 else 'volatile'})")
        
        # Combine into detailed explanation
        if explanation_parts:
            detailed_explanation = "Quality of Earnings: " + "; ".join(explanation_parts) + f". Overall earnings quality is {'excellent' if score >= 7.5 else 'strong' if score >= 6.5 else 'acceptable' if score >= 5.5 else 'concerning'}."
        else:
            detailed_explanation = "Assessment of earnings sustainability and accounting quality."
        
        return QualityScore(
            category=ScoreCategory.QUALITY_EARNINGS.value,
            score=score,
            weight=self.CATEGORY_WEIGHTS[ScoreCategory.QUALITY_EARNINGS],
            strengths=strengths,
            concerns=concerns,
            explanation=detailed_explanation
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
        
        # Build detailed explanation with figures
        explanation_parts = []
        
        # Add dividend policy analysis
        if data.dividend_yield:
            explanation_parts.append(f"Dividend Yield: {data.dividend_yield:.1f}% ({'shareholder-friendly' if data.dividend_yield > 2 else 'maintained'})")
        
        # Add reporting consistency
        if data.revenue and len(data.revenue) >= data.years_analyzed:
            explanation_parts.append(f"Financial Reporting: Complete {data.years_analyzed}-year data available")
        
        # Add capital allocation analysis
        if data.free_cash_flow:
            fcf_values = list(data.free_cash_flow.values())
            positive_fcf = sum(1 for v in fcf_values if v > 0)
            explanation_parts.append(f"Capital Discipline: Positive FCF in {positive_fcf}/{len(fcf_values)} years")
        
        # Add accounting quality check
        if data.net_income and data.operating_cash_flow:
            ni_list = list(data.net_income.values())
            ocf_list = list(data.operating_cash_flow.values())
            
            concern_years = sum(1 for i in range(min(len(ni_list), len(ocf_list))) 
                              if ni_list[i] > 0 and ocf_list[i] > 0 and ni_list[i] > ocf_list[i] * 1.5)
            
            if concern_years > 0:
                explanation_parts.append(f"Accounting Quality: NI>OCF in {concern_years} years ({'concern' if concern_years >= 2 else 'monitor'})")
            else:
                explanation_parts.append("Accounting Quality: Clean pattern")
        
        # Combine into detailed explanation
        if explanation_parts:
            detailed_explanation = "Management & Governance: " + "; ".join(explanation_parts) + f". Overall management quality indicators are {'excellent' if score >= 7.5 else 'strong' if score >= 6.5 else 'acceptable' if score >= 5.5 else 'concerning'}."
        else:
            detailed_explanation = "Assessment of management quality through financial indicators."
        
        return QualityScore(
            category=ScoreCategory.GOVERNANCE.value,
            score=score,
            weight=self.CATEGORY_WEIGHTS[ScoreCategory.GOVERNANCE],
            strengths=strengths,
            concerns=concerns,
            explanation=detailed_explanation
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
            
            # Generate management quality assessment
            report.management_quality_assessment = self._analyze_management_quality(fin_data, report)
            
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
    
    def _analyze_management_quality(self, fin_data: FinancialData, report: QualityReport) -> ManagementQualityAssessment:
        """Comprehensive management quality assessment using AI"""
        if not self.client:
            # Return basic assessment without AI
            return self._generate_basic_management_assessment(fin_data, report)
        
        try:
            # Prepare detailed financial context
            context = self._prepare_management_context(fin_data, report)
            
            # Use AI to analyze management quality
            prompt = f"""You are an expert financial analyst evaluating management quality. Analyze the following company data and provide a comprehensive management quality assessment.

{context}

Please provide a detailed analysis covering these 8 areas:

1️⃣ **Management Guidance vs Reality**
   - What did management promise in previous years (revenue growth, profit, margins, expansions, ROE, ROCE)?
   - Did they achieve, partially achieve, or fail?
   - Rating: Achieved / Partially Achieved / Not Achieved / Over-promised
   
2️⃣ **Consistency & Honesty**
   - Is the narrative consistent across years or constantly changing?
   - Do they accept mistakes openly?
   - Do they blame external factors repeatedly?
   - Rating: High / Medium / Low consistency
   
3️⃣ **Visibility of Business**
   - Does management clearly explain the next 1-3 years?
   - Do they provide clear numbers or only vague statements?
   - Rating: High / Medium / Low visibility
   
4️⃣ **Vision & Long-Term Thinking**
   - Are they focused on 5-10 year vision?
   - Talking about capex, new markets, technology, brand, moat?
   - Is the vision practical or just fancy words?
   - Rating: Excellent / Good / Average / Weak
   
5️⃣ **Capital Allocation Skill**
   - How they used profits and cash (capex, acquisitions, debt reduction, dividends)?
   - Any value-destructive decisions?
   - Rating: Excellent / Good / Average / Poor
   
6️⃣ **Shareholder Respect**
   - Quality of communication and transparency
   - Do they answer tough questions clearly?
   - Rating: High / Medium / Low
   
7️⃣ **Red Flags**
   - Repeated delays
   - Constant changes in guidance
   - Aggressive language without backing
   - Related party concerns
   
8️⃣ **Overall Management Quality Score**
   - Score from 1 to 10
   - Category: Excellent (8-10) / Good (6-7.9) / Average (4-5.9) / Weak (<4)

Respond in JSON format with this structure:
{{
    "guidance_vs_reality": {{"revenue_growth": "Achieved", "margin_expansion": "Partially Achieved"}},
    "achievement_rating": "Achieved/Partially Achieved/Not Achieved/Over-promised",
    "narrative_consistency": "High/Medium/Low",
    "accepts_mistakes": true/false,
    "external_blame_pattern": true/false,
    "business_visibility": "High/Medium/Low",
    "clarity_score": 1-10,
    "provides_numbers": true/false,
    "vision_quality": "Excellent/Good/Average/Weak",
    "long_term_focus": true/false,
    "strategic_initiatives": ["initiative1", "initiative2"],
    "capital_allocation_rating": "Excellent/Good/Average/Poor",
    "allocation_analysis": "detailed analysis...",
    "bad_acquisitions": ["acquisition1" if any],
    "communication_quality": "Excellent/Good/Average/Poor",
    "transparency_rating": "High/Medium/Low",
    "answers_tough_questions": true/false,
    "management_red_flags": ["flag1", "flag2"],
    "management_score": 7.5,
    "management_category": "Excellent/Good/Average/Weak",
    "detailed_analysis": "comprehensive analysis covering all 8 points..."
}}
"""
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a financial analyst specializing in management quality assessment. Provide objective, data-driven analysis."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            # Parse AI response
            ai_response = response.choices[0].message.content.strip()
            
            # Extract JSON from response (handle markdown code blocks)
            if "```json" in ai_response:
                ai_response = ai_response.split("```json")[1].split("```")[0].strip()
            elif "```" in ai_response:
                ai_response = ai_response.split("```")[1].split("```")[0].strip()
            
            assessment_data = json.loads(ai_response)
            
            # Create ManagementQualityAssessment object
            assessment = ManagementQualityAssessment(
                guidance_vs_reality=assessment_data.get("guidance_vs_reality", {}),
                achievement_rating=assessment_data.get("achievement_rating", "Not Assessed"),
                narrative_consistency=assessment_data.get("narrative_consistency", "Medium"),
                accepts_mistakes=assessment_data.get("accepts_mistakes", False),
                external_blame_pattern=assessment_data.get("external_blame_pattern", False),
                business_visibility=assessment_data.get("business_visibility", "Medium"),
                clarity_score=assessment_data.get("clarity_score", 5),
                provides_numbers=assessment_data.get("provides_numbers", False),
                vision_quality=assessment_data.get("vision_quality", "Average"),
                long_term_focus=assessment_data.get("long_term_focus", False),
                strategic_initiatives=assessment_data.get("strategic_initiatives", []),
                capital_allocation_rating=assessment_data.get("capital_allocation_rating", "Average"),
                allocation_analysis=assessment_data.get("allocation_analysis", ""),
                bad_acquisitions=assessment_data.get("bad_acquisitions", []),
                communication_quality=assessment_data.get("communication_quality", "Average"),
                transparency_rating=assessment_data.get("transparency_rating", "Medium"),
                answers_tough_questions=assessment_data.get("answers_tough_questions", False),
                management_red_flags=assessment_data.get("management_red_flags", []),
                management_score=assessment_data.get("management_score", 5.0),
                management_category=assessment_data.get("management_category", "Average"),
                detailed_analysis=assessment_data.get("detailed_analysis", "")
            )
            
            return assessment
            
        except Exception as e:
            print(f"Management quality assessment failed: {e}")
            return self._generate_basic_management_assessment(fin_data, report)
    
    def _prepare_management_context(self, fin_data: FinancialData, report: QualityReport) -> str:
        """Prepare context for management quality analysis"""
        # Build comprehensive context from financial data and report
        context = f"""
COMPANY: {fin_data.company_name} ({fin_data.ticker})
SECTOR: {fin_data.sector} | INDUSTRY: {fin_data.industry}
ANALYSIS PERIOD: {fin_data.years_analyzed} years

FINANCIAL PERFORMANCE TRENDS:
Revenue Growth: {self._calculate_cagr(fin_data.revenue) if fin_data.revenue else 'N/A'}%
Profit Growth: {self._calculate_cagr(fin_data.net_income) if fin_data.net_income else 'N/A'}%
Operating Margin Trend: {self._analyze_trend(fin_data.operating_margin) if fin_data.operating_margin else 'N/A'}
ROE Trend: {self._analyze_trend(fin_data.roe) if fin_data.roe else 'N/A'}
ROCE Trend: {self._analyze_trend(fin_data.roce) if fin_data.roce else 'N/A'}

CAPITAL ALLOCATION:
Cash Flow from Operations: {list(fin_data.operating_cash_flow.values()) if fin_data.operating_cash_flow else 'N/A'}
Free Cash Flow: {list(fin_data.free_cash_flow.values()) if fin_data.free_cash_flow else 'N/A'}
Capex Trend: Analyzing capital expenditure patterns
Debt Management: D/E ratio trends {list(fin_data.debt_to_equity.values()) if fin_data.debt_to_equity else 'N/A'}
Dividend Policy: {fin_data.dividend_yield if hasattr(fin_data, 'dividend_yield') else 'N/A'}%

QUALITY METRICS:
Overall Quality Score: {report.overall_score}/10
Key Strengths: {', '.join(report.key_strengths[:3])}
Red Flags: {len(report.red_flags)} identified
Earnings Quality: {'High' if any('cash' in s.lower() for s in report.key_strengths) else 'Moderate'}

CONSISTENCY INDICATORS:
Revenue Consistency: {self._check_consistency(fin_data.revenue) if fin_data.revenue else 'N/A'}
Margin Stability: {self._check_consistency(fin_data.operating_margin) if fin_data.operating_margin else 'N/A'}
Cash Flow Reliability: {self._check_consistency(fin_data.operating_cash_flow) if fin_data.operating_cash_flow else 'N/A'}
"""
        return context.strip()
    
    def _calculate_cagr(self, data_dict: Dict) -> str:
        """Calculate CAGR from dictionary of values"""
        if not data_dict or len(data_dict) < 2:
            return "Insufficient data"
        
        values = list(data_dict.values())
        if values[0] and values[-1] and values[-1] > 0:
            years = len(values) - 1
            cagr = ((values[0] / values[-1]) ** (1/years) - 1) * 100
            return f"{cagr:.1f}"
        return "N/A"
    
    def _analyze_trend(self, data_dict: Dict) -> str:
        """Analyze trend direction"""
        if not data_dict or len(data_dict) < 2:
            return "Insufficient data"
        
        values = list(data_dict.values())
        if values[0] > values[-1] * 1.1:
            return "Improving"
        elif values[0] < values[-1] * 0.9:
            return "Declining"
        else:
            return "Stable"
    
    def _check_consistency(self, data_dict: Dict) -> str:
        """Check consistency of values"""
        if not data_dict or len(data_dict) < 3:
            return "Insufficient data"
        
        values = [v for v in data_dict.values() if v is not None]
        if not values:
            return "No data"
        
        avg = sum(values) / len(values)
        if avg == 0:
            return "No meaningful data"
        
        variance = sum((v - avg) ** 2 for v in values) / len(values)
        std_dev = variance ** 0.5
        cv = std_dev / avg
        
        if cv < 0.15:
            return "High (Consistent)"
        elif cv < 0.30:
            return "Medium (Moderate variation)"
        else:
            return "Low (High variation)"
    
    def _generate_basic_management_assessment(self, fin_data: FinancialData, report: QualityReport) -> ManagementQualityAssessment:
        """Generate basic management assessment without AI"""
        # Calculate basic metrics for management score
        score = 5.0
        
        # Adjust based on financial performance
        if report.overall_score >= 7:
            score += 2
        elif report.overall_score < 5:
            score -= 1
        
        # Adjust based on growth consistency
        if fin_data.revenue and len(fin_data.revenue) >= 3:
            revenues = list(fin_data.revenue.values())
            positive_growth = sum(1 for i in range(len(revenues)-1) if revenues[i] > revenues[i+1])
            if positive_growth == len(revenues) - 1:
                score += 1
        
        # Adjust based on cash flow quality
        if any('cash' in s.lower() for s in report.key_strengths):
            score += 0.5
        
        score = max(1, min(10, score))
        
        # Determine category
        if score >= 8:
            category = "Excellent"
        elif score >= 6:
            category = "Good"
        elif score >= 4:
            category = "Average"
        else:
            category = "Weak"
        
        return ManagementQualityAssessment(
            achievement_rating="Analysis based on financial metrics only",
            narrative_consistency="Medium",
            business_visibility="Medium",
            clarity_score=int(score),
            vision_quality="Average",
            capital_allocation_rating="Average",
            allocation_analysis="Based on financial metrics - detailed analysis requires AI",
            communication_quality="Average",
            transparency_rating="Medium",
            management_score=score,
            management_category=category,
            detailed_analysis=f"""
Basic management assessment (requires AI for detailed analysis):

Overall Score: {score:.1f}/10 - {category}

This assessment is based on quantitative financial metrics including:
- Overall company quality score: {report.overall_score}/10
- Growth consistency and performance trends
- Cash flow quality and capital efficiency
- Financial health indicators

For detailed management quality analysis including guidance tracking, communication quality, 
and strategic vision assessment, AI-enhanced analysis is recommended.
"""
        )
