"""
Streamlit Web Application for Pattern Pulse
Run with: streamlit run app.py
"""

import streamlit as st
import os
import tempfile
from pathlib import Path
from datetime import datetime

# Lazy imports - load heavy libraries only when needed
@st.cache_resource
def load_dependencies():
    """Cache heavy imports to speed up subsequent loads"""
    from src import QualityManagementAgent, ReportFormatter, parse_multiple_reports, generate_institutional_pdf
    from src.pdf_compressor import compress_pdf_for_upload
    import plotly.graph_objects as go
    import plotly.express as px
    return {
        'QualityManagementAgent': QualityManagementAgent,
        'ReportFormatter': ReportFormatter,
        'parse_multiple_reports': parse_multiple_reports,
        'generate_institutional_pdf': generate_institutional_pdf,
        'compress_pdf_for_upload': compress_pdf_for_upload,
        'go': go,
        'px': px
    }

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Load secrets from Streamlit Cloud (if deployed) or environment variables
# Streamlit Cloud uses st.secrets, local dev uses .env
if hasattr(st, 'secrets'):
    try:
        # Set environment variables from Streamlit secrets for compatibility
        for key in st.secrets:
            if key not in os.environ:  # Don't override existing env vars
                os.environ[key] = st.secrets[key]
    except Exception:
        pass  # Secrets not configured, will use .env

# Page configuration
st.set_page_config(
    page_title="Pattern Pulse",
    page_icon="▪️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Advanced Professional CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        margin-bottom: 0.5rem;
        letter-spacing: -0.5px;
    }
    .sub-header {
        font-size: 1.1rem;
        text-align: center;
        color: #64748b;
        margin-bottom: 3rem;
        font-weight: 400;
    }
    
    /* Modern card styling */
    .score-box {
        padding: 2.5rem;
        border-radius: 16px;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        margin: 2rem 0;
        border: 1px solid rgba(255,255,255,0.3);
    }
    
    .metric-card {
        background: white;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.07);
        margin: 1rem 0;
        border-left: 4px solid #667eea;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 12px rgba(0,0,0,0.15);
    }
    
    /* Hide Streamlit branding but keep sidebar toggle */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Keep header visible for sidebar toggle button */
    
    /* Premium buttons */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.875rem 2.5rem;
        font-weight: 600;
        letter-spacing: 0.5px;
        border-radius: 8px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        text-transform: uppercase;
        font-size: 0.875rem;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }
    
    .stButton>button:active {
        transform: translateY(0);
    }
    
    /* Enhanced inputs */
    .stTextInput>div>div>input,
    .stNumberInput>div>div>input {
        border: 2px solid #e2e8f0;
        border-radius: 8px;
        padding: 0.75rem 1rem;
        font-size: 0.95rem;
        transition: border-color 0.3s;
    }
    
    .stTextInput>div>div>input:focus,
    .stNumberInput>div>div>input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Modern tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        background-color: #f8fafc;
        padding: 0.5rem;
        border-radius: 12px;
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 0.75rem 1.5rem;
        color: #64748b;
        font-weight: 500;
        border-radius: 8px;
        transition: all 0.3s;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }
    
    /* Progress bars */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Select boxes */
    .stSelectbox>div>div>div {
        border-radius: 8px;
        border: 2px solid #e2e8f0;
    }
    
    /* File uploader */
    .stFileUploader>div>div {
        border: 2px dashed #cbd5e1;
        border-radius: 12px;
        background-color: #f8fafc;
        padding: 2rem;
        transition: all 0.3s;
    }
    
    .stFileUploader>div>div:hover {
        border-color: #667eea;
        background-color: #f1f5f9;
    }
    
    /* Success/Error/Warning/Info boxes */
    .stSuccess, .stError, .stWarning, .stInfo {
        border-radius: 8px;
        padding: 1rem 1.5rem;
        border-left: 4px solid;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f8fafc 0%, #e2e8f0 100%);
    }
    
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        font-size: 0.95rem;
    }
    
    /* Radio buttons */
    .stRadio > div {
        background-color: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: #f8fafc;
        border-radius: 8px;
        border: 1px solid #e2e8f0;
        font-weight: 500;
    }
    
    .streamlit-expanderHeader:hover {
        background-color: #f1f5f9;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
        color: #1e293b;
    }
    
    /* Download button special styling */
    .stDownloadButton>button {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.4);
    }
    
    .stDownloadButton>button:hover {
        box-shadow: 0 6px 20px rgba(16, 185, 129, 0.6);
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False
if 'report' not in st.session_state:
    st.session_state.report = None
if 'deps_loaded' not in st.session_state:
    st.session_state.deps_loaded = False

# Lightweight helper function
def format_size(size_mb):
    """Format file size in MB - lightweight version"""
    return f"{size_mb:.2f} MB"

def display_report(report):
    """Display the analysis report in an advanced professional format"""
    
    # Load plotly lazily (only when displaying report)
    if not st.session_state.deps_loaded:
        deps = load_dependencies()
        go = deps['go']
        st.session_state.deps_loaded = True
    else:
        deps = load_dependencies()
        go = deps['go']
    
    # Overall Score Section with Premium Design
    st.markdown("---")
    st.markdown("## 📊 Quality Assessment Dashboard")
    
    # Premium score display with gradient and styling
    score = report.overall_score
    if score >= 7.5:
        rating = "EXCELLENT"
        gradient = "linear-gradient(135deg, #10b981 0%, #059669 100%)"
        bg_color = "#d1fae5"
    elif score >= 6.5:
        rating = "STRONG"
        gradient = "linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)"
        bg_color = "#dbeafe"
    elif score >= 5.5:
        rating = "GOOD"
        gradient = "linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)"
        bg_color = "#ede9fe"
    elif score >= 4.0:
        rating = "MODERATE"
        gradient = "linear-gradient(135deg, #f59e0b 0%, #d97706 100%)"
        bg_color = "#fed7aa"
    else:
        rating = "NEEDS IMPROVEMENT"
        gradient = "linear-gradient(135deg, #ef4444 0%, #dc2626 100%)"
        bg_color = "#fecaca"
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"""
            <div style='text-align: center; padding: 3rem 2rem; background: {gradient}; 
                        border-radius: 20px; color: white; box-shadow: 0 20px 60px rgba(0,0,0,0.2);
                        position: relative; overflow: hidden;'>
                <div style='position: relative; z-index: 2;'>
                    <p style='margin: 0; font-size: 1rem; font-weight: 500; opacity: 0.9; letter-spacing: 2px;'>OVERALL SCORE</p>
                    <h1 style='margin: 1rem 0; font-size: 5rem; font-weight: 800;'>{score:.1f}</h1>
                    <p style='margin: 0; font-size: 1.5rem; font-weight: 600; letter-spacing: 3px;'>{rating}</p>
                </div>
                <div style='position: absolute; top: -50%; right: -10%; width: 300px; height: 300px; 
                            background: rgba(255,255,255,0.1); border-radius: 50%; z-index: 1;'></div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Category Scores with Modern Design
    st.markdown("## 📈 Detailed Category Analysis")
    
    # Create a dictionary mapping category names to full CategoryScore objects
    category_score_map = {}
    if hasattr(report, 'category_scores') and report.category_scores:
        for cat_score in report.category_scores:
            category_score_map[cat_score.category] = cat_score
    
    # Define expected categories with fallback
    category_names_list = [
        "Profitability & Margins",
        "Growth & Revenue Stability",
        "Financial Health & Leverage",
        "Cash Flow Management",
        "Capital Efficiency & Returns",
        "Quality of Earnings",
        "Management & Governance Indicators"
    ]
    
    # Build categories list with full objects
    categories = []
    for cat_name in category_names_list:
        cat_obj = category_score_map.get(cat_name)
        if cat_obj:
            categories.append((cat_name, cat_obj.score, cat_obj.explanation))
        else:
            categories.append((cat_name, 0.0, "No data available for this category."))
    
    # Create modern tabs
    tab1, tab2, tab3 = st.tabs(["📊 Scorecard", "📈 Visual Analytics", "⚠️ Risk Alerts"])
    
    with tab1:
        # Display category scores in attractive cards with two columns
        col1, col2 = st.columns(2)
        
        for idx, (category, score, explanation) in enumerate(categories):
            target_col = col1 if idx % 2 == 0 else col2
            
            with target_col:
                # Determine color and rating
                if score >= 7.5:
                    rating = "⭐ Excellent"
                    color = "#10b981"
                    bg_gradient = "linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%)"
                elif score >= 6.5:
                    rating = "💎 Strong"
                    color = "#3b82f6"
                    bg_gradient = "linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%)"
                elif score >= 5.5:
                    rating = "✓ Good"
                    color = "#8b5cf6"
                    bg_gradient = "linear-gradient(135deg, #ede9fe 0%, #ddd6fe 100%)"
                elif score >= 4.0:
                    rating = "⚡ Moderate"
                    color = "#f59e0b"
                    bg_gradient = "linear-gradient(135deg, #fed7aa 0%, #fdba74 100%)"
                else:
                    rating = "⚠️ Needs Attention"
                    color = "#ef4444"
                    bg_gradient = "linear-gradient(135deg, #fecaca 0%, #fca5a5 100%)"
                
                st.markdown(f"""
                    <div style='padding: 1.5rem; background: {bg_gradient}; 
                                border-radius: 12px; margin-bottom: 0.5rem; 
                                border-left: 5px solid {color};
                                box-shadow: 0 4px 6px rgba(0,0,0,0.07);'>
                        <h4 style='margin: 0 0 1rem 0; color: #1e293b; font-weight: 600;'>{category}</h4>
                        <div style='display: flex; justify-content: space-between; align-items: center;'>
                            <span style='font-size: 2rem; font-weight: 700; color: {color};'>{score:.1f}</span>
                            <span style='color: {color}; font-weight: 600;'>{rating}</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                st.progress(score / 10.0)
                
                # Display reasoning/explanation below the scorecard
                st.markdown(f"""
                    <div style='padding: 1rem; background: white; 
                                border-radius: 8px; margin-bottom: 1.5rem;
                                border: 1px solid #e2e8f0;
                                box-shadow: 0 2px 4px rgba(0,0,0,0.05);'>
                        <p style='margin: 0; color: #475569; font-size: 0.9rem; line-height: 1.6;'>
                            <strong style='color: #1e293b;'>💡 Analysis:</strong> {explanation}
                        </p>
                    </div>
                """, unsafe_allow_html=True)
    
    with tab2:
        # Professional visualizations
        category_names = [cat[0] for cat in categories]
        category_scores = [cat[1] for cat in categories]
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Radar Chart
            fig_radar = go.Figure()
            
            fig_radar.add_trace(go.Scatterpolar(
                r=category_scores,
                theta=category_names,
                fill='toself',
                name='Quality Scores',
                line=dict(color='#667eea', width=3),
                fillcolor='rgba(102, 126, 234, 0.25)',
                marker=dict(size=8, color='#667eea')
            ))
            
            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 10],
                        gridcolor='#e2e8f0',
                        tickfont=dict(size=10)
                    ),
                    angularaxis=dict(
                        gridcolor='#e2e8f0'
                    ),
                    bgcolor='white'
                ),
                showlegend=False,
                title=dict(
                    text="Category Performance Radar",
                    font=dict(size=16, weight=600)
                ),
                height=450,
                paper_bgcolor='white',
                plot_bgcolor='white'
            )
            
            st.plotly_chart(fig_radar, use_container_width=True)
        
        with col2:
            # Gradient Horizontal Bar Chart
            category_colors = []
            for score in category_scores:
                if score >= 7.5:
                    category_colors.append('#10b981')
                elif score >= 6.5:
                    category_colors.append('#3b82f6')
                elif score >= 5.5:
                    category_colors.append('#8b5cf6')
                elif score >= 4.0:
                    category_colors.append('#f59e0b')
                else:
                    category_colors.append('#ef4444')
            
            fig_bar = go.Figure()
            
            fig_bar.add_trace(go.Bar(
                y=category_names,
                x=category_scores,
                orientation='h',
                marker=dict(
                    color=category_colors,
                    line=dict(color='white', width=2),
                    pattern=dict(shape="")
                ),
                text=[f'{score:.1f}' for score in category_scores],
                textposition='outside',
                textfont=dict(size=12, color='#1e293b', weight=600)
            ))
            
            fig_bar.update_layout(
                title=dict(
                    text="Category Scores Comparison",
                    font=dict(size=16, weight=600)
                ),
                xaxis=dict(
                    title="Score",
                    range=[0, 10.5],
                    gridcolor='#e2e8f0',
                    showgrid=True
                ),
                yaxis=dict(
                    title="",
                    gridcolor='#e2e8f0'
                ),
                height=450,
                plot_bgcolor='white',
                paper_bgcolor='white',
                showlegend=False,
                font=dict(size=11)
            )
            
            st.plotly_chart(fig_bar, use_container_width=True)
        
        # Premium Gauge Chart
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=report.overall_score,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Overall Quality Score", 'font': {'size': 20, 'color': '#1e293b'}},
            delta={'reference': 5.0, 'increasing': {'color': "#10b981"}, 'decreasing': {'color': "#ef4444"}},
            gauge={
                'axis': {'range': [None, 10], 'tickwidth': 2, 'tickcolor': "#94a3b8"},
                'bar': {'color': "#667eea", 'thickness': 0.75},
                'bgcolor': "white",
                'borderwidth': 3,
                'bordercolor': "#cbd5e1",
                'steps': [
                    {'range': [0, 4], 'color': '#fecaca'},
                    {'range': [4, 5.5], 'color': '#fed7aa'},
                    {'range': [5.5, 6.5], 'color': '#ddd6fe'},
                    {'range': [6.5, 7.5], 'color': '#bfdbfe'},
                    {'range': [7.5, 10], 'color': '#a7f3d0'}
                ],
                'threshold': {
                    'line': {'color': "#667eea", 'width': 5},
                    'thickness': 0.85,
                    'value': report.overall_score
                }
            }
        ))
        
        fig_gauge.update_layout(
            height=400,
            paper_bgcolor='white',
            font={'color': "#1e293b", 'family': "Inter"}
        )
        st.plotly_chart(fig_gauge, use_container_width=True)
    
    with tab3:
        # Professional Red Flag Display
        if report.red_flags:
            # Count by severity
            severity_counts = {'High': 0, 'Medium': 0, 'Low': 0}
            category_flags = {}
            
            for flag in report.red_flags:
                if hasattr(flag, 'severity'):
                    severity_counts[flag.severity] = severity_counts.get(flag.severity, 0) + 1
                    category = getattr(flag, 'category', 'Other')
                    category_flags[category] = category_flags.get(category, 0) + 1
            
            # Display severity metrics with attractive cards
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"""
                    <div style='padding: 1.5rem; background: linear-gradient(135deg, #fecaca 0%, #fca5a5 100%);
                                border-radius: 12px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
                        <p style='margin: 0; color: #7f1d1d; font-size: 0.9rem; font-weight: 600;'>HIGH SEVERITY</p>
                        <h2 style='margin: 0.5rem 0 0 0; color: #ef4444; font-size: 2.5rem; font-weight: 700;'>{severity_counts.get('High', 0)}</h2>
                    </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                    <div style='padding: 1.5rem; background: linear-gradient(135deg, #fed7aa 0%, #fdba74 100%);
                                border-radius: 12px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
                        <p style='margin: 0; color: #78350f; font-size: 0.9rem; font-weight: 600;'>MEDIUM SEVERITY</p>
                        <h2 style='margin: 0.5rem 0 0 0; color: #f59e0b; font-size: 2.5rem; font-weight: 700;'>{severity_counts.get('Medium', 0)}</h2>
                    </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                    <div style='padding: 1.5rem; background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
                                border-radius: 12px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
                        <p style='margin: 0; color: #713f12; font-size: 0.9rem; font-weight: 600;'>LOW SEVERITY</p>
                        <h2 style='margin: 0.5rem 0 0 0; color: #eab308; font-size: 2.5rem; font-weight: 700;'>{severity_counts.get('Low', 0)}</h2>
                    </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Red flags by category - Donut Chart
            if category_flags:
                fig_pie = go.Figure(data=[go.Pie(
                    labels=list(category_flags.keys()),
                    values=list(category_flags.values()),
                    hole=.4,
                    marker=dict(
                        colors=['#ef4444', '#f59e0b', '#eab308', '#84cc16', '#22c55e', '#14b8a6', '#06b6d4'],
                        line=dict(color='white', width=3)
                    ),
                    textfont=dict(size=13, color='white'),
                    textposition='inside'
                )])
                
                fig_pie.update_layout(
                    title=dict(
                        text="Red Flags Distribution by Category",
                        font=dict(size=16, weight=600)
                    ),
                    height=400,
                    paper_bgcolor='white',
                    showlegend=True,
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=-0.2,
                        xanchor="center",
                        x=0.5
                    )
                )
                
                st.plotly_chart(fig_pie, use_container_width=True)
            
            # Detailed red flags with better styling
            st.markdown("### 🔍 Detailed Risk Analysis")
            
            for idx, flag in enumerate(report.red_flags, 1):
                if hasattr(flag, 'severity'):
                    if flag.severity == "High":
                        severity_color = "#ef4444"
                        severity_bg = "#fecaca"
                        severity_icon = "🔴"
                    elif flag.severity == "Medium":
                        severity_color = "#f59e0b"
                        severity_bg = "#fed7aa"
                        severity_icon = "🟠"
                    else:
                        severity_color = "#eab308"
                        severity_bg = "#fef3c7"
                        severity_icon = "🟡"
                    
                    with st.expander(f"{severity_icon} **Alert #{idx}** | {flag.category} | **{flag.severity} Severity**"):
                        st.markdown(f"""
                            <div style='padding: 1rem; background: {severity_bg}; border-radius: 8px; border-left: 4px solid {severity_color};'>
                                <p style='margin: 0 0 0.5rem 0; color: #1e293b;'><strong>📋 Description:</strong> {flag.description}</p>
                                <p style='margin: 0.5rem 0; color: #1e293b;'><strong>⚡ Impact:</strong> {flag.impact}</p>
                                <p style='margin: 0.5rem 0 0 0; color: #1e293b;'><strong>💡 Recommendation:</strong> {flag.recommendation}</p>
                            </div>
                        """, unsafe_allow_html=True)
                else:
                    st.write(f"**{idx}.** {flag}")
        else:
            st.markdown("""
                <div style='padding: 3rem; text-align: center; background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
                            border-radius: 16px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
                    <h2 style='color: #065f46; margin: 0 0 1rem 0;'>🎉 Excellent!</h2>
                    <p style='color: #047857; font-size: 1.1rem; margin: 0;'>
                        No red flags identified across all evaluated categories.<br>
                        This indicates strong quality management and financial health.
                    </p>
                </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Key Strengths with attractive display
    if report.key_strengths:
        st.markdown("## ✨ Key Strengths")
        
        for idx, strength in enumerate(report.key_strengths, 1):
            st.markdown(f"""
                <div style='padding: 1rem 1.5rem; margin: 0.5rem 0; background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
                            border-left: 4px solid #3b82f6; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);'>
                    <p style='margin: 0; color: #1e293b;'><strong style='color: #3b82f6;'>#{idx}</strong> {strength}</p>
                </div>
            """, unsafe_allow_html=True)
        st.markdown("---")
    
    # Executive Summary with modern styling
    if hasattr(report, 'executive_summary') and report.executive_summary:
        st.markdown("## 📝 Executive Summary")
        st.markdown(f"""
            <div style='padding: 2rem; background: linear-gradient(135deg, #faf5ff 0%, #f3e8ff 100%);
                        border-radius: 12px; border-left: 5px solid #8b5cf6; box-shadow: 0 4px 6px rgba(0,0,0,0.07);'>
                <p style='margin: 0; color: #1e293b; line-height: 1.8; font-size: 1rem;'>{report.executive_summary}</p>
            </div>
        """, unsafe_allow_html=True)

def main():
    # Show welcome message on first load
    if not st.session_state.get('app_initialized', False):
        with st.spinner('🚀 Initializing Pattern Pulse...'):
            # This allows the page to render quickly first
            st.session_state.app_initialized = True
    
    # Professional Header with Gradient
    st.markdown('''
        <div style="text-align: center; padding: 2rem 0 1rem 0;">
            <h1 class="main-header">Pattern Pulse</h1>
            <p class="sub-header">Advanced Financial Analysis & Quality Assessment Platform</p>
        </div>
    ''', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        # Performance note (only show once)
        if not st.session_state.get('perf_note_shown', False):
            st.info("⚡ **First Load**: App may take 10-15 seconds to wake up. Subsequent visits are faster!")
            st.session_state.perf_note_shown = True
        
        # Mode Selection
        analysis_mode = st.radio(
            "📊 Analysis Mode",
            ["📄 PDF Upload", "🌐 Online Data Fetch"],
            help="Choose your preferred data source"
        )
        
        st.markdown("---")
        
        # About section with modern styling
        st.markdown('''
            <div style="padding: 1rem; background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
                        border-radius: 8px; border-left: 4px solid #3b82f6;">
                <h4 style="color: #1e293b; margin: 0 0 0.75rem 0;">📊 Analysis Coverage</h4>
                <ul style="margin: 0; padding-left: 1.25rem; color: #475569; font-size: 0.9rem;">
                    <li>💰 Profitability & Margins</li>
                    <li>📈 Growth & Revenue Stability</li>
                    <li>🏦 Financial Health & Leverage</li>
                    <li>💵 Cash Flow Management</li>
                    <li>⚡ Capital Efficiency</li>
                    <li>✅ Quality of Earnings</li>
                    <li>👔 Management & Governance</li>
                </ul>
            </div>
        ''', unsafe_allow_html=True)
    
    # Main content area
    if "PDF Upload" in analysis_mode:
            # PDF Mode with professional header
            st.markdown("""
                <div style='padding: 1.5rem; background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
                            border-radius: 12px; border-left: 5px solid #667eea; margin-bottom: 2rem;'>
                    <h2 style='margin: 0; color: #1e293b; font-weight: 600;'>📊 Management Quality Assessment</h2>
                    <p style='margin: 0.5rem 0 0 0; color: #64748b;'>Upload annual reports for comprehensive quality assessment</p>
                </div>
            """, unsafe_allow_html=True)
            
            # User name input
            user_name = st.text_input(
                "👤 Your Name",
                placeholder="e.g., John Doe",
                help="Enter your name for the analysis report"
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                company_name = st.text_input(
                    "🏢 Company Name",
                    placeholder="e.g., ABC Corporation",
                    help="Enter the full company name for analysis"
                )
            
            with col2:
                years_to_analyze = st.number_input(
                    "📅 Years to Analyze",
                    min_value=1,
                    max_value=10,
                    value=5,
                    help="Number of years of historical data to analyze"
                )
            
            uploaded_files = None
            
            # Compression Helper Section
            with st.expander("🗜️ Need to Compress Your PDF? (Files larger than 20MB)", expanded=False):
                st.markdown("""
                    <div style='padding: 1rem; background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
                                border-radius: 8px; border-left: 4px solid #3b82f6;'>
                        <p style='margin: 0 0 0.75rem 0; color: #1e40af; font-size: 1rem; font-weight: 600;'>
                            📦 Compress the PDF File
                        </p>
                        <p style='margin: 0 0 1rem 0; color: #334155; font-size: 0.9rem;'>
                            If your PDF exceeds 20MB, use this free online tool to compress it before uploading:
                        </p>
                    </div>
                """, unsafe_allow_html=True)
                
                # Use Streamlit's link button (opens in new tab)
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    st.link_button(
                        "🗜️ Open PDF Compression Tool",
                        "https://tools.pdf24.org/en/compress-pdf",
                        type="primary",
                        use_container_width=True
                    )
                
                st.markdown("""
                    <p style='margin: 1rem 0 0 0; color: #64748b; font-size: 0.85rem; text-align: center;'>
                        ✓ Free & Secure | ✓ No Registration Required | ✓ Fast Processing
                    </p>
                    <p style='margin: 0.5rem 0 0 0; color: #94a3b8; font-size: 0.8rem; text-align: center; font-style: italic;'>
                        Opens in a new tab. After compressing, download and upload the file below.
                    </p>
                """, unsafe_allow_html=True)
            
            
            # Upload method with modern styling
            st.markdown("<br>", unsafe_allow_html=True)
            upload_mode = st.radio(
                    "📂 Upload Mode",
                    ["Single PDF (Multiple Years)", "Multiple PDFs (One per Year)"],
                    horizontal=True,
                    key="upload_mode_radio"
                )
                
            if "Single PDF" in upload_mode:
                st.markdown("""
                    <div style='padding: 0.75rem; background: #fff7ed; border-left: 3px solid #f59e0b;
                                border-radius: 6px; margin: 1rem 0;'>
                        <p style='margin: 0; color: #92400e; font-size: 0.9rem;'>
                            <strong>⚡ File Limit:</strong> Maximum 20 MB per file | 
                            <a href='https://tools.pdf24.org/en/compress-pdf' target='_blank' style='color: #f59e0b; text-decoration: none; font-weight: 600;'>🗜️ Compress PDF File</a>
                        </p>
                    </div>
                """, unsafe_allow_html=True)
                
                uploaded_file = st.file_uploader(
                    "📄 Upload Annual Report (PDF)",
                    type=['pdf'],
                    key="single_pdf_uploader",
                    help="Drag and drop or click to browse"
                )
                if uploaded_file:
                    # Check file size
                    file_size_mb = uploaded_file.size / (1024 * 1024)
                    
                    if file_size_mb > 20:
                        st.error(f"❌ **File Too Large:** {format_size(file_size_mb)} exceeds 20MB limit. Please compress your PDF before uploading.")
                        st.markdown("""<div style='margin-top: 0.5rem;'>
                            <a href='https://tools.pdf24.org/en/compress-pdf' target='_blank' 
                               style='display: inline-block; padding: 0.5rem 1rem; background: #f59e0b; 
                               color: white; text-decoration: none; border-radius: 6px; font-weight: 600;'>
                                🗜️ Compress the PDF File
                            </a>
                        </div>""", unsafe_allow_html=True)
                        uploaded_file = None
                    else:
                        st.success(f"✅ **{uploaded_file.name}** `{format_size(file_size_mb)}` — Ready for analysis!")
                        uploaded_files = [uploaded_file]
            else:
                st.markdown("""
                    <div style='padding: 0.75rem; background: #fff7ed; border-left: 3px solid #f59e0b;
                                border-radius: 6px; margin: 1rem 0;'>
                        <p style='margin: 0; color: #92400e; font-size: 0.9rem;'>
                            <strong>⚡ Per-File Limit:</strong> 20 MB maximum per file | 
                            <a href='https://tools.pdf24.org/en/compress-pdf' target='_blank' style='color: #f59e0b; text-decoration: none; font-weight: 600;'>🗜️ Compress PDF File</a>
                        </p>
                    </div>
                """, unsafe_allow_html=True)
                
                uploaded_files_raw = st.file_uploader(
                    "📂 Upload Multiple Annual Reports (PDFs)",
                    type=['pdf'],
                    accept_multiple_files=True,
                    key="multi_pdf_uploader",
                    help="Select multiple PDF files (one per year)"
                )
                if uploaded_files_raw:
                    # Check individual file sizes
                    valid_files = []
                    total_size_mb = 0
                    
                    for f in uploaded_files_raw:
                        file_size_mb = f.size / (1024 * 1024)
                        
                        if file_size_mb > 20:
                            st.error(f"❌ **{f.name}**: Exceeds 20MB limit `{format_size(file_size_mb)}`")
                        else:
                            st.success(f"✅ **{f.name}** `{format_size(file_size_mb)}`")
                            valid_files.append(f)
                            total_size_mb += file_size_mb
                    
                    if valid_files:
                        st.markdown(f"""
                            <div style='padding: 1rem; background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
                                        border-radius: 8px; text-align: center; margin: 1rem 0;'>
                                <p style='margin: 0; color: #065f46; font-weight: 600;'>
                                    📦 Total: {format_size(total_size_mb)} | {len(valid_files)} files ready for analysis
                                </p>
                            </div>
                        """, unsafe_allow_html=True)
                        uploaded_files = valid_files
                    else:
                        st.warning("⚠️ **No valid files found.** Please ensure all files are under 20MB.")
                        uploaded_files = None
            
            # Analyze button with icon
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🚀 Start Analysis", type="primary", use_container_width=True):
                if not user_name:
                    st.error("⚠️ **Missing Information:** Please enter your name")
                elif not company_name:
                    st.error("⚠️ **Missing Information:** Please enter a company name")
                elif not uploaded_files:
                    st.error("⚠️ **No Files:** Please upload at least one PDF file")
                else:
                    # Determine PDF paths based on selection method
                    temp_dir = None
                    pdf_paths = []
                    
                    try:
                        # Save uploaded files to temporary directory
                        # Create progress container
                        progress_text = st.empty()
                        progress_bar = st.progress(0)
                        
                        progress_text.text("📤 Preparing to save files...")
                        temp_dir = tempfile.mkdtemp()
                        
                        total_files = len(uploaded_files)
                        
                        for idx, uploaded_file in enumerate(uploaded_files):
                            try:
                                progress_text.text(f"📤 Saving {uploaded_file.name} ({idx + 1}/{total_files})...")
                                progress_bar.progress((idx + 1) / total_files)
                                
                                temp_path = os.path.join(temp_dir, uploaded_file.name)
                                
                                # Read file in chunks to avoid memory issues
                                file_bytes = uploaded_file.getvalue()  # Using getvalue() instead of getbuffer()
                                
                                # Write to temp file
                                with open(temp_path, 'wb') as f:
                                    f.write(file_bytes)
                                
                                # Verify file was written
                                if not os.path.exists(temp_path):
                                    raise IOError(f"Failed to save {uploaded_file.name}")
                                
                                file_size = os.path.getsize(temp_path)
                                if file_size == 0:
                                    raise IOError(f"File {uploaded_file.name} is empty after saving")
                                
                                pdf_paths.append(temp_path)
                                
                            except Exception as e:
                                progress_text.empty()
                                progress_bar.empty()
                                st.error(f"Error saving file {uploaded_file.name}: {str(e)}")
                                st.error(f"**File size:** {uploaded_file.size / (1024 * 1024):.2f}MB")
                                st.markdown("""
                                **Possible solutions:**
                                1. Try uploading files one at a time
                                2. Clear browser cache and retry
                                """)
                                st.markdown("""<div style='margin-top: 0.5rem;'>
                                    <a href='https://tools.pdf24.org/en/compress-pdf' target='_blank' 
                                       style='display: inline-block; padding: 0.5rem 1rem; background: #f59e0b; 
                                       color: white; text-decoration: none; border-radius: 6px; font-weight: 600;'>
                                        🗜️ Compress the PDF File First
                                    </a>
                                </div>""", unsafe_allow_html=True)
                                raise
                        
                        progress_text.text("✅ All files saved successfully!")
                        progress_bar.progress(1.0)
                        
                        import time
                        time.sleep(0.5)  # Brief pause to show success
                        
                        progress_text.empty()
                        progress_bar.empty()
                    
                    except Exception as e:
                        st.error(f"Error during file processing: {str(e)}")
                        st.info("""
                        💡 **Recommended Solutions:**
                        
                        - Upload files individually instead of all at once
                        - Clear browser cache and try again
                        - Ensure PDF file size is under 20 MB
                        """)
                        st.markdown("""<div style='margin-top: 0.5rem;'>
                            <a href='https://tools.pdf24.org/en/compress-pdf' target='_blank' 
                               style='display: inline-block; padding: 0.75rem 1.5rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                               color: white; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 1rem; 
                               box-shadow: 0 4px 6px rgba(102, 126, 234, 0.25);'>
                                🗜️ Compress the PDF File
                            </a>
                        </div>""", unsafe_allow_html=True)
                        if temp_dir and os.path.exists(temp_dir):
                            import shutil
                            shutil.rmtree(temp_dir, ignore_errors=True)
                    else:
                        # Run analysis only if file upload succeeded
                        try:
                            with st.spinner("Loading analysis tools..."):
                                # Load dependencies
                                deps = load_dependencies()
                                QualityManagementAgent = deps['QualityManagementAgent']
                                parse_multiple_reports = deps['parse_multiple_reports']
                            
                            with st.spinner("Analyzing PDFs..."):
                                # Initialize agent in PDF mode
                                agent = QualityManagementAgent(use_ai=True, pdf_mode=True)
                                
                                # Analyze from PDF(s)
                                if len(pdf_paths) == 1:
                                    report = agent.analyze_from_pdf(
                                        pdf_path=pdf_paths[0],
                                        company_name=company_name,
                                        years=years_to_analyze
                                    )
                                else:
                                    # Multiple PDFs
                                    financial_data = parse_multiple_reports(pdf_paths, company_name)
                                    report = agent.analyzer.analyze(financial_data)
                            
                            st.session_state.report = report
                            st.session_state.analysis_complete = True
                            
                            # Clean up temp files
                            import shutil
                            shutil.rmtree(temp_dir, ignore_errors=True)
                            
                            st.success("✨ **Analysis Complete!** Your comprehensive quality assessment is ready.")
                            st.rerun()
                            
                        except Exception as e:
                            st.error(f"Error during analysis: {str(e)}")
                            st.exception(e)
                            st.info("Troubleshooting:")
                            st.markdown("""
                            - Ensure your OpenAI API key is configured in the .env file
                            - Check if the PDF contains extractable text (not scanned images)
                            - Try with a different PDF file
                            - Check the error details above
                            """)
                            # Clean up temp files
                            import shutil
                            shutil.rmtree(temp_dir, ignore_errors=True)
    
    else:
        # Online Mode with professional design
        st.markdown("""
            <div style='padding: 1.5rem; background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
                        border-radius: 12px; border-left: 5px solid #3b82f6; margin-bottom: 2rem;'>
                <h2 style='margin: 0; color: #1e293b; font-weight: 600;'>🌐 Online Data Fetch</h2>
                <p style='margin: 0.5rem 0 0 0; color: #64748b;'>Automatically fetch financial data from Yahoo Finance & Screener.in</p>
            </div>
        """, unsafe_allow_html=True)
        
        # User name input
        user_name = st.text_input(
            "👤 Your Name",
            placeholder="e.g., John Doe",
            help="Enter your name for the analysis report"
        )
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            company_identifier = st.text_input(
                "🏢 Company Ticker / Name",
                placeholder="e.g., RELIANCE.NS, TCS.NS, AAPL",
                help="Enter stock ticker with exchange suffix or company name"
            )
        
        with col2:
            years_to_analyze = st.number_input(
                "📅 Years to Analyze",
                min_value=1,
                max_value=10,
                value=5,
                help="Number of years of historical data"
            )
        
        with col3:
            market = st.selectbox(
                "🌍 Market",
                ["india", "us", "global"],
                help="Select the primary trading market"
            )
        
        # Analyze button with icon
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚀 Start Analysis", type="primary", use_container_width=True):
            if not user_name:
                st.error("⚠️ **Missing Information:** Please enter your name")
            elif not company_identifier:
                st.error("⚠️ **Missing Information:** Please enter a company ticker or name")
            else:
                try:
                    with st.spinner("Loading analysis tools..."):
                        # Load dependencies
                        deps = load_dependencies()
                        QualityManagementAgent = deps['QualityManagementAgent']
                    
                    with st.spinner(f"🔍 Fetching financial data for **{company_identifier}**..."):
                        # Initialize agent
                        agent = QualityManagementAgent(use_ai=True, pdf_mode=False)
                        
                        # Analyze company
                        report = agent.analyze_company(
                            company_identifier=company_identifier,
                            years=years_to_analyze,
                            market=market
                        )
                    
                    st.session_state.report = report
                    st.session_state.analysis_complete = True
                    
                    st.success("Analysis Complete")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Error during analysis: {str(e)}")
                    st.info("""
                    **Tips:**
                    - For Indian stocks: Use NSE ticker (e.g., 'TCS', 'RELIANCE', 'INFY')
                    - For US stocks: Use ticker symbol (e.g., 'AAPL', 'MSFT', 'GOOGL')
                    - You can also add exchange suffix: 'TCS.NS' for NSE
                    """)
    
    # Display results if analysis is complete
    if st.session_state.analysis_complete and st.session_state.report:
        st.markdown("---")
        display_report(st.session_state.report)
        
        # Download options
        st.markdown("---")
        st.markdown("## � Export Institutional Report")
        
        st.info("""
        **📑 Professional PDF Report Includes:**
        - ✓ Executive Summary
        - ✓ Quantitative Scoring Breakdown
        - ✓ Visual Analytics (Radar, Bar, Gauge & Pie Charts)
        - ✓ Strategic Alignment Analysis
        - ✓ Capital Allocation Discipline
        - ✓ Governance Quality Assessment
        - ✓ Execution vs Narrative Gap Analysis
        - ✓ Comprehensive Red Flags Section
        - ✓ Final Rating & Investment Perspective
        """)
        
        col1, col2, col3 = st.columns([2, 1, 2])
        
        with col2:
            if st.button("📝 Generate Professional PDF Report", use_container_width=True, type="primary"):
                with st.spinner("Loading PDF generator..."):
                    # Load dependencies
                    deps = load_dependencies()
                    generate_institutional_pdf = deps['generate_institutional_pdf']
                
                with st.spinner("Generating institutional-grade PDF report..."):
                    try:
                        report = st.session_state.report
                        
                        # Generate PDF in temporary file
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        pdf_filename = f"Quality_Report_{report.ticker}_{timestamp}.pdf"
                        
                        # Create temp directory if needed
                        temp_dir = tempfile.gettempdir()
                        pdf_path = os.path.join(temp_dir, pdf_filename)
                        
                        # Generate PDF
                        generate_institutional_pdf(report, pdf_path)
                        
                        # Read PDF file
                        with open(pdf_path, 'rb') as pdf_file:
                            pdf_data = pdf_file.read()
                        
                        # Offer download
                        st.success("🎉 **PDF Report Generated Successfully!** Your institutional-grade report is ready for download.")
                        
                        st.download_button(
                            label="📥 Download Institutional Report (PDF)",
                            data=pdf_data,
                            file_name=pdf_filename,
                            mime="application/pdf",
                            use_container_width=True
                        )
                        
                        # Clean up temp file
                        try:
                            os.remove(pdf_path)
                        except:
                            pass
                            
                    except Exception as e:
                        st.error(f"Error generating PDF: {str(e)}")
                        st.info("The report is still viewable above. Please try again or contact support.")
        
        st.markdown("---")
        
        # Reset button
        col1, col2, col3 = st.columns([2, 1, 2])
        with col2:
            if st.button("🔄 Start New Analysis", use_container_width=True):
                st.session_state.analysis_complete = False
                st.session_state.report = None
                st.rerun()

if __name__ == "__main__":
    main()
