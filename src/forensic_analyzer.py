"""
Forensic Management Quality Analysis Engine
Advanced institutional-grade forensic analysis using comprehensive prompts
"""

import os
import json
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

from openai import OpenAI

from .analyzer import QualityReport, QualityScore, RedFlag


class ForensicQualityAnalyzer:
    """
    Advanced forensic analysis engine for institutional-grade management quality assessment
    """
    
    def __init__(self, use_ai: bool = True):
        """Initialize the forensic analyzer"""
        self.use_ai = use_ai
        if use_ai:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key or api_key == "your-openai-api-key-here":
                raise ValueError("OpenAI API key not configured")
            self.client = OpenAI(api_key=api_key)
    
    def analyze_from_pdf_text(
        self,
        pdf_text: str,
        company_name: str,
        years_analyzed: int
    ) -> QualityReport:
        """
        Perform comprehensive forensic analysis from PDF annual report text
        
        Args:
            pdf_text: Extracted text from annual report PDF(s)
            company_name: Name of the company
            years_analyzed: Number of years covered in the analysis
            
        Returns:
            QualityReport with detailed forensic analysis
        """
        
        # Generate forensic analysis using comprehensive prompt
        analysis_result = self._generate_forensic_analysis(pdf_text, company_name, years_analyzed)
        
        # Parse the analysis result and create QualityReport
        report = self._parse_analysis_to_report(analysis_result, company_name, years_analyzed)
        
        return report
    
    def _generate_forensic_analysis(self, pdf_text: str, company_name: str, years: int) -> str:
        """
        Generate comprehensive forensic analysis using advanced institutional prompt
        """
        
        # Truncate PDF text to fit in context window (keep most recent sections)
        max_text_length = 50000  # Approx 50k chars for GPT-4
        if len(pdf_text) > max_text_length:
            pdf_text = pdf_text[:max_text_length] + "\n\n[Document truncated for processing...]"
        
        system_prompt = """You are operating in **Forensic Equity Research Mode** with 20+ years of experience in:

* Forensic accounting
* Governance evaluation
* Capital allocation analysis
* Financial statement integrity review
* Management stewardship assessment

Your task is to evaluate **Management Quality** using only disclosures contained in the uploaded Annual Report(s).

Your output must reflect the depth, rigor, and analytical precision expected from a **senior institutional research analyst**."""

        user_prompt = f"""
# STRICT RULES

✔ Use ONLY disclosed report data
✔ Do NOT use external sources or assumptions
✔ Highlight missing disclosures explicitly
✔ Maintain professional institutional tone
✔ Avoid promotional or motivational language
✔ Provide evidence-based observations

If data is missing: **State:** "Not adequately disclosed."

---

# INPUT DATA

Company: {company_name}
Years Analyzed: {years}

Annual Report Content:
{pdf_text}

---

# ANALYSIS FRAMEWORK

Analyze the following dimensions:

## 1️⃣ STRATEGIC DIRECTION & EXECUTION CONSISTENCY

Evaluate:
* Strategy continuity vs sudden pivots
* Clarity of long-term priorities
* Alignment between strategy and capital deployment
* Organic growth vs acquisition-driven growth
* Execution credibility vs narrative positioning

Detect:
✔ Strategy evolution supported by outcomes
✖ Repetitive strategic narrative without measurable progress
✖ Frequent shifts in strategic direction

---

## 2️⃣ CAPITAL ALLOCATION DISCIPLINE

Assess Management's Capital Deployment Effectiveness:

### Efficiency Indicators
* ROCE / ROIC trend
* Asset turnover trend
* Incremental return on invested capital
* Capex productivity & utilization

### Funding Discipline
* Debt/Equity trend
* Interest coverage
* Equity dilution history
* Leverage vs growth alignment

### Cash Flow Stewardship
* CFO vs PAT consistency
* Free cash flow generation
* Working capital efficiency
* Dividend vs reinvestment balance
* Acquisition returns & capital allocation rationale

---

## 3️⃣ GOVERNANCE QUALITY & BOARD EFFECTIVENESS

Evaluate:
* Board independence & composition
* Director tenure and attendance
* Separation of Chairman & CEO roles (if disclosed)
* Auditor tenure & independence
* Promoter shareholding trend
* Promoter pledge disclosures

### Management Compensation Integrity
Compare:
* Executive remuneration growth vs PAT growth
* Performance-linked incentives clarity
* ESOP dilution and shareholder impact

---

## 4️⃣ DISCLOSURE QUALITY & TRANSPARENCY

Assess:
* Improvement vs dilution in disclosures year-on-year
* Clarity of notes to accounts
* Transparency in related party transactions
* Auditor reporting tone & emphasis
* Contingent liabilities clarity
* Accounting policy changes & their impact

Watch For:
* Increasing reporting complexity
* Segment restructuring without clear rationale
* Restatements or reclassifications

---

## 5️⃣ EXECUTION vs NARRATIVE VALIDATION

Create analytical validation table:

| Management Claim | Supporting Metric | Consistency |
| ---------------- | ----------------- | ----------- |

Cross-verify:
* Margin expansion claims
* Growth drivers
* Efficiency improvement claims
* Cost optimization narratives

---

# RED FLAG DETECTION MODULE

## 🔴 Governance Red Flags
* Promoter pledge increase
* Frequent auditor or CFO changes
* Independent director resignations
* Excessive promoter remuneration
* Weak board independence indicators

## 🔴 Financial Integrity Red Flags
* PAT growth without operating cash flow support
* Rising receivables or inventory days
* Capitalized expenses growth
* Frequent exceptional/one-time adjustments
* Rising contingent liabilities

## 🔴 Reporting & Disclosure Red Flags
* Accounting policy changes affecting profitability
* Segment reclassification without explanation
* Increase in related party transactions
* Complex subsidiary or associate structures

## 🔴 Strategic Red Flags
* Frequent shifts in strategic direction
* Diversification beyond core competence
* Acquisitions without synergy clarity
* ESG narrative without measurable performance indicators

---

# ADVANCED FORENSIC QUALITY CHECKS

### Earnings Quality
* CFO/PAT ratio
* EBITDA vs operating cash flow alignment
* Working capital absorption trends
* One-time income dependency

### Balance Sheet Integrity
* Intangible asset growth trend
* Capital WIP ageing
* Deferred tax asset/liability movement
* Off-balance sheet exposures (if disclosed)

---

# MULTI-YEAR TREND ANALYSIS

Evaluate sustainability of:
✔ Revenue growth
✔ Operating margins
✔ ROCE / capital efficiency
✔ Levers of profitability
✔ Debt & leverage trends
✔ Cash conversion cycle

---

# OUTPUT STRUCTURE (MANDATORY JSON FORMAT)

Return your analysis in this exact JSON structure:

{{
  "strategic_alignment": {{
    "analysis": "Detailed evidence-based analysis of strategy clarity and execution consistency.",
    "score": 0-2,
    "key_findings": ["finding1", "finding2", ...]
  }},
  "capital_allocation": {{
    "analysis": "Evaluation of efficiency of capital deployment and cash flow stewardship.",
    "score": 0-2,
    "key_findings": ["finding1", "finding2", ...]
  }},
  "governance_transparency": {{
    "analysis": "Analysis of board effectiveness, auditor tone, compensation integrity, and disclosure quality.",
    "score": 0-2,
    "key_findings": ["finding1", "finding2", ...]
  }},
  "execution_vs_narrative": {{
    "analysis": "Identify divergence between management commentary and financial outcomes.",
    "score": 0-2,
    "validation_table": [
      {{"claim": "...", "supporting_metric": "...", "consistency": "Aligned/Divergent"}}
    ]
  }},
  "red_flags": {{
    "critical": [
      {{
        "category": "Governance/Financial Integrity/Reporting/Strategic",
        "description": "...",
        "impact": "...",
        "recommendation": "..."
      }}
    ],
    "moderate": [...],
    "strengths": [...]
  }},
  "quantitative_scoring": {{
    "strategy_clarity": 0-2,
    "execution_consistency": 0-2,
    "capital_allocation_discipline": 0-2,
    "governance_quality": 0-2,
    "disclosure_transparency": 0-2,
    "earnings_quality": 0-2,
    "balance_sheet_integrity": 0-2,
    "minority_shareholder_fairness": 0-2,
    "total_score": 0-16,
    "normalized_score": 0-10
  }},
  "earnings_quality_metrics": {{
    "cfo_pat_ratio": "...",
    "working_capital_trend": "...",
    "one_time_dependency": "..."
  }},
  "multi_year_trends": {{
    "revenue_growth_sustainability": "...",
    "margin_sustainability": "...",
    "roce_trend": "...",
    "leverage_trend": "..."
  }},
  "final_verdict": {{
    "summary": "Concise institutional-style conclusion",
    "classification": "Exceptional/Strong/Average/Concerning/High Risk",
    "investment_perspective": "..."
  }},
  "key_strengths": ["strength1", "strength2", "strength3"],
  "executive_summary": "200-250 word comprehensive summary"
}}

Return ONLY valid JSON. No additional text or markdown formatting.
"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,  # Lower temperature for more consistent, analytical output
                max_tokens=4000,
                response_format={"type": "json_object"}
            )
            
            result = response.choices[0].message.content.strip()
            return result
            
        except Exception as e:
            raise Exception(f"Error generating forensic analysis: {str(e)}")
    
    def _parse_analysis_to_report(
        self,
        analysis_json: str,
        company_name: str,
        years_analyzed: int
    ) -> QualityReport:
        """
        Parse the JSON analysis result into a QualityReport object
        """
        try:
            data = json.loads(analysis_json)
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse analysis JSON: {str(e)}")
        
        # Extract overall score
        scoring = data.get("quantitative_scoring", {})
        overall_score = scoring.get("normalized_score", 0.0)
        
        # Create category scores
        category_scores = [
            QualityScore(
                category="Profitability & Margins",
                score=float(scoring.get("earnings_quality", 0)) * 5,  # Scale 0-2 to 0-10
                weight=0.20,
                strengths=[],
                concerns=[],
                explanation=data.get("earnings_quality_metrics", {}).get("cfo_pat_ratio", "")
            ),
            QualityScore(
                category="Growth & Revenue Stability",
                score=float(scoring.get("strategy_clarity", 0)) * 5,
                weight=0.15,
                strengths=[],
                concerns=[],
                explanation=data.get("multi_year_trends", {}).get("revenue_growth_sustainability", "")
            ),
            QualityScore(
                category="Financial Health & Leverage",
                score=float(scoring.get("balance_sheet_integrity", 0)) * 5,
                weight=0.20,
                strengths=[],
                concerns=[],
                explanation=data.get("multi_year_trends", {}).get("leverage_trend", "")
            ),
            QualityScore(
                category="Cash Flow Management",
                score=float(scoring.get("capital_allocation_discipline", 0)) * 5,
                weight=0.15,
                strengths=[],
                concerns=[],
                explanation=data.get("capital_allocation", {}).get("analysis", "")[:200]
            ),
            QualityScore(
                category="Capital Efficiency & Returns",
                score=float(scoring.get("execution_consistency", 0)) * 5,
                weight=0.15,
                strengths=[],
                concerns=[],
                explanation=data.get("multi_year_trends", {}).get("roce_trend", "")
            ),
            QualityScore(
                category="Quality of Earnings",
                score=float(scoring.get("earnings_quality", 0)) * 5,
                weight=0.10,
                strengths=[],
                concerns=[],
                explanation=data.get("earnings_quality_metrics", {}).get("working_capital_trend", "")
            ),
            QualityScore(
                category="Management & Governance Indicators",
                score=float(scoring.get("governance_quality", 0)) * 5,
                weight=0.05,
                strengths=[],
                concerns=[],
                explanation=data.get("governance_transparency", {}).get("analysis", "")[:200]
            )
        ]
        
        # Parse red flags
        red_flags = []
        red_flag_data = data.get("red_flags", {})
        
        # Critical red flags
        for flag in red_flag_data.get("critical", []):
            red_flags.append(RedFlag(
                severity="High",
                category=flag.get("category", "General"),
                description=flag.get("description", ""),
                impact=flag.get("impact", ""),
                recommendation=flag.get("recommendation", "")
            ))
        
        # Moderate red flags
        for flag in red_flag_data.get("moderate", []):
            if isinstance(flag, dict):
                red_flags.append(RedFlag(
                    severity="Medium",
                    category=flag.get("category", "General"),
                    description=flag.get("description", ""),
                    impact=flag.get("impact", ""),
                    recommendation=flag.get("recommendation", "")
                ))
            else:
                red_flags.append(RedFlag(
                    severity="Medium",
                    category="General",
                    description=str(flag),
                    impact="Requires monitoring",
                    recommendation="Further investigation recommended"
                ))
        
        # Extract key strengths
        key_strengths = data.get("key_strengths", [])
        if not key_strengths:
            key_strengths = red_flag_data.get("strengths", [])
        
        # Create final report
        report = QualityReport(
            company_name=company_name,
            ticker=company_name.upper().replace(" ", "_"),
            analysis_date=datetime.now().strftime("%Y-%m-%d"),
            years_analyzed=years_analyzed,
            overall_score=float(overall_score),
            category_scores=category_scores,
            key_strengths=key_strengths,
            red_flags=red_flags,
            executive_summary=data.get("executive_summary", ""),
            investment_thesis=data.get("final_verdict", {}).get("investment_perspective", ""),
            risk_assessment=data.get("final_verdict", {}).get("summary", ""),
            metrics_summary={
                "forensic_analysis": data.get("final_verdict", {}),
                "earnings_quality": data.get("earnings_quality_metrics", {}),
                "multi_year_trends": data.get("multi_year_trends", {}),
                "execution_validation": data.get("execution_vs_narrative", {})
            }
        )
        
        return report
