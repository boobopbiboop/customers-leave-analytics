import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

st.set_page_config(page_title="🎯 Customer Churn Analytics", page_icon="🎯", layout="wide")

# Custom CSS
st.markdown("""
<style>
.main-header { font-size: 3rem; color: #2c3e50; text-align: center; margin-bottom: 1rem; }
.alert-critical { background: #8B0000; padding: 1rem; border-radius: 10px; color: white; text-align: center; }
.alert-high { background: #e74c3c; padding: 1rem; border-radius: 10px; color: white; text-align: center; }
.alert-medium { background: #f39c12; padding: 1rem; border-radius: 10px; color: white; text-align: center; }
.alert-low { background: #27ae60; padding: 1rem; border-radius: 10px; color: white; text-align: center; }
.metric-big { font-size: 2rem; font-weight: bold; }
.insight-box { background: #e8f4fd; border-left: 4px solid #3498db; padding: 1rem; margin: 1rem 0; border-radius: 5px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-header">Customer Churn Analytics Dashboard</h1>', unsafe_allow_html=True)

# Load data from fix.csv
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('fix.csv')
        # st.sidebar.success(f"✅ Data loaded successfully: {len(df)} records from fix.csv")
        return df
    except FileNotFoundError:
        # st.error("❌ File fix.csv not found")
        st.stop()
    except Exception as e:
        # st.error(f"❌ Error loading data: {e}")
        st.stop()

df = load_data()

# Sidebar filters
st.sidebar.header("Data Filters")
status_filter = st.sidebar.selectbox("Customer Status", ['All'] + list(df['customer_status'].unique()))

# Filter by satisfaction_level
satisfaction_levels = sorted(df['satisfaction_level'].unique())
satisfaction_filter = st.sidebar.selectbox("Satisfaction Level", ['All'] + satisfaction_levels)

# Filter by churn_risk_level
risk_levels = sorted(df['churn_risk_level'].unique())
risk_filter = st.sidebar.selectbox("Churn Risk Level", ['All'] + risk_levels)

# CLTV Range Filter
cltv_min, cltv_max = int(df['cltv'].min()), int(df['cltv'].max())
cltv_range = st.sidebar.slider("CLTV Range ($)", cltv_min, cltv_max, (cltv_min, cltv_max))

# Apply filters
filtered_df = df.copy()
if status_filter != 'All':
    filtered_df = filtered_df[filtered_df['customer_status'] == status_filter]
if satisfaction_filter != 'All':
    filtered_df = filtered_df[filtered_df['satisfaction_level'] == satisfaction_filter]
if risk_filter != 'All':
    filtered_df = filtered_df[filtered_df['churn_risk_level'] == risk_filter]

# Apply CLTV range filter
filtered_df = filtered_df[(filtered_df['cltv'] >= cltv_range[0]) & (filtered_df['cltv'] <= cltv_range[1])]

# Calculate metrics
total = len(filtered_df)
churned = len(filtered_df[filtered_df['customer_status'] == 'Churned'])
stayed = len(filtered_df[filtered_df['customer_status'] == 'Stayed'])
joined = len(filtered_df[filtered_df['customer_status'] == 'Joined']) if 'Joined' in filtered_df['customer_status'].values else 0

churn_rate = (churned / total * 100) if total > 0 else 0
avg_cltv = filtered_df['cltv'].mean()

# Risk calculations based on churn_risk_level
critical_risk = len(filtered_df[filtered_df['churn_risk_level'] == 'Critical Risk'])
high_risk = len(filtered_df[filtered_df['churn_risk_level'] == 'High Risk'])
medium_risk = len(filtered_df[filtered_df['churn_risk_level'] == 'Medium Risk'])
low_risk = len(filtered_df[filtered_df['churn_risk_level'] == 'Low Risk'])

# Risk Alert System - 4 levels from fix.csv
st.header("Risk Alert System")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f'''
    <div class="alert-critical">
        <div class="metric-big">{critical_risk}</div>
        <div>CRITICAL RISK</div>
        <div>Emergency Action</div>
    </div>
    ''', unsafe_allow_html=True)

with col2:
    st.markdown(f'''
    <div class="alert-high">
        <div class="metric-big">{high_risk}</div>
        <div>HIGH RISK</div>
        <div>Immediate Action</div>
    </div>
    ''', unsafe_allow_html=True)

with col3:
    st.markdown(f'''
    <div class="alert-medium">
        <div class="metric-big">{medium_risk}</div>
        <div>MEDIUM RISK</div>
        <div>Monitor Closely</div>
    </div>
    ''', unsafe_allow_html=True)

with col4:
    st.markdown(f'''
    <div class="alert-low">
        <div class="metric-big">{low_risk}</div>
        <div>LOW RISK</div>
        <div>Stable</div>
    </div>
    ''', unsafe_allow_html=True)

st.divider()

# Key Metrics
st.header("Key Metrics")
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Total Customers", f"{total:,}")
with col2:
    st.metric("Churned Customers", f"{churned:,}")
with col3:
    st.metric("Retained Customers", f"{stayed:,}")
with col4:
    st.metric("Churn Rate", f"{churn_rate:.1f}%")
with col5:
    st.metric("Average CLTV", f"${avg_cltv:,.0f}")

st.divider()

# Revenue Impact Analysis based on churn_risk_level
st.header("Revenue Impact Analysis")
col1, col2 = st.columns(2)

with col1:
    # Revenue at Risk Gauge
    churned_revenue = filtered_df[filtered_df['customer_status'] == 'Churned']['cltv'].sum()
    total_revenue = filtered_df['cltv'].sum()
    revenue_at_risk_pct = (churned_revenue / total_revenue * 100) if total_revenue > 0 else 0
    
    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = revenue_at_risk_pct,
        title = {'text': "Revenue at Risk (%)"},
        gauge = {
            'axis': {'range': [None, 50]},
            'bar': {'color': "#e74c3c"},
            'steps': [
                {'range': [0, 15], 'color': "#27ae60"},
                {'range': [15, 30], 'color': "#f39c12"},
                {'range': [30, 50], 'color': "#e74c3c"}
            ],
            'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 25}
        }
    ))
    fig_gauge.update_layout(height=300)
    st.plotly_chart(fig_gauge, use_container_width=True)

with col2:
    # Revenue by Risk Level with numbers
    risk_revenue = filtered_df.groupby('churn_risk_level')['cltv'].sum().reset_index()
    
    fig_revenue = px.bar(risk_revenue, x='churn_risk_level', y='cltv',
                        color='churn_risk_level',
                        color_discrete_map={
                            'Critical Risk': '#8B0000',
                            'High Risk': '#e74c3c', 
                            'Medium Risk': '#f39c12', 
                            'Low Risk': '#27ae60'
                        },
                        title="Total CLTV by Risk Level",
                        text='cltv')
    fig_revenue.update_traces(texttemplate='$%{text:,.0f}', textposition='outside')
    fig_revenue.update_layout(showlegend=False, height=300)
    fig_revenue.update_xaxes(title_text="Risk Level")
    fig_revenue.update_yaxes(title_text="Total CLTV ($)")
    st.plotly_chart(fig_revenue, use_container_width=True)

# Satisfaction Analysis
st.header("Satisfaction Analysis")

col1, col2 = st.columns(2)

with col1:
    # Satisfaction Level Analysis
    satisfaction_analysis = filtered_df.groupby('satisfaction_level').agg({
        'customer_id': 'count',
        'churn_value': 'mean',
        'cltv': 'mean'
    }).reset_index()
    satisfaction_analysis['churn_rate'] = satisfaction_analysis['churn_value'] * 100
    satisfaction_analysis.columns = ['satisfaction_level', 'count', 'churn_value', 'avg_cltv', 'churn_rate']

    fig_satisfaction = make_subplots(specs=[[{"secondary_y": True}]])

    fig_satisfaction.add_trace(
        go.Bar(x=satisfaction_analysis['satisfaction_level'], y=satisfaction_analysis['churn_rate'], 
               name='Churn Rate (%)', marker_color='#e74c3c',
               text=satisfaction_analysis['churn_rate'].round(1),
               texttemplate='%{text}%', textposition='outside'),
        secondary_y=False,
    )

    fig_satisfaction.add_trace(
        go.Scatter(x=satisfaction_analysis['satisfaction_level'], y=satisfaction_analysis['avg_cltv'], 
                   mode='lines+markers', name='Average CLTV ($)', 
                   line=dict(color='#3498db', width=3),
                   text=satisfaction_analysis['avg_cltv'].round(0),
                   texttemplate='$%{text:,.0f}', textposition='top center'),
        secondary_y=True,
    )

    fig_satisfaction.update_xaxes(title_text="Satisfaction Level")
    fig_satisfaction.update_yaxes(title_text="Churn Rate (%)", secondary_y=False)
    fig_satisfaction.update_yaxes(title_text="Average CLTV ($)", secondary_y=True)
    fig_satisfaction.update_layout(title_text="Satisfaction Level Impact Analysis", height=400)

    st.plotly_chart(fig_satisfaction, use_container_width=True)

with col2:
    # Satisfaction Score Distribution
    score_counts = filtered_df['satisfaction_score'].value_counts().sort_index()
    
    fig_score = px.bar(x=score_counts.index, y=score_counts.values,
                      title="Satisfaction Score Distribution",
                      color_discrete_sequence=['#9b59b6'],
                      text=score_counts.values)
    fig_score.update_traces(texttemplate='%{text}', textposition='outside')
    fig_score.update_xaxes(title_text="Satisfaction Score (1-5)")
    fig_score.update_yaxes(title_text="Number of Customers")
    st.plotly_chart(fig_score, use_container_width=True)

# Customer Analysis
st.header("Customer Analysis")
col1, col2 = st.columns(2)

with col1:
    # Status Distribution with numbers
    status_counts = filtered_df['customer_status'].value_counts()
    fig_pie = px.pie(values=status_counts.values, names=status_counts.index, 
                     title="Customer Status Distribution",
                     color_discrete_sequence=['#e74c3c', '#2ecc71', '#3498db'])
    fig_pie.update_traces(textposition='inside', textinfo='percent+label+value')
    st.plotly_chart(fig_pie, use_container_width=True)

with col2:
    # CLTV Quartile Distribution with numbers
    quartile_counts = filtered_df['cltv_quartile'].value_counts()
    fig_quartile = px.bar(x=quartile_counts.index, y=quartile_counts.values,
                         title="CLTV Quartile Distribution",
                         color_discrete_sequence=['#3498db'],
                         text=quartile_counts.values)
    fig_quartile.update_traces(texttemplate='%{text}', textposition='outside')
    fig_quartile.update_xaxes(title_text="CLTV Quartile")
    fig_quartile.update_yaxes(title_text="Number of Customers")
    st.plotly_chart(fig_quartile, use_container_width=True)

col1, col2 = st.columns(2)

with col1:
    # Risk Level vs Satisfaction Level Heatmap with numbers
    risk_satisfaction = pd.crosstab(filtered_df['churn_risk_level'], filtered_df['satisfaction_level'])
    
    fig_heatmap = px.imshow(risk_satisfaction.values,
                           x=risk_satisfaction.columns,
                           y=risk_satisfaction.index,
                           color_continuous_scale='Reds',
                           title="Heatmap: Risk Level vs Satisfaction Level",
                           text_auto=True)
    fig_heatmap.update_xaxes(title_text="Satisfaction Level")
    fig_heatmap.update_yaxes(title_text="Risk Level")
    st.plotly_chart(fig_heatmap, use_container_width=True)

with col2:
    # Churn Category Analysis with numbers
    category_counts = filtered_df[filtered_df['churn_category'] != 'Not Applicable']['churn_category'].value_counts()
    
    if len(category_counts) > 0:
        fig_category = px.bar(x=category_counts.values, y=category_counts.index, 
                             orientation='h',
                             title="Churn Categories",
                             color_discrete_sequence=['#f39c12'],
                             text=category_counts.values)
        fig_category.update_traces(texttemplate='%{text}', textposition='outside')
        fig_category.update_layout(yaxis_title="Category", xaxis_title="Count")
        st.plotly_chart(fig_category, use_container_width=True)
    else:
        st.info("No churn category data available for current filters")

# Action Priority Analysis
st.header("Action Priority Analysis")

churn_reasons = filtered_df[
    (filtered_df['churn_reason'] != 'Unknown') & 
    (filtered_df['churn_reason'].notna()) &
    (filtered_df['customer_status'] == 'Churned')
]['churn_reason'].value_counts().head(10)

if len(churn_reasons) > 0:
    col1, col2 = st.columns(2)
    
    with col1:
        # Bubble chart for churn reasons
        reason_impact = []
        for reason in churn_reasons.index:
            reason_data = filtered_df[
                (filtered_df['churn_reason'] == reason) & 
                (filtered_df['customer_status'] == 'Churned')
            ]
            reason_impact.append({
                'reason': reason,
                'count': len(reason_data),
                'revenue': reason_data['cltv'].sum()
            })
        
        reason_df = pd.DataFrame(reason_impact)
        
        fig_bubble = px.scatter(reason_df, x='count', y='revenue', 
                               size='revenue', color='revenue',
                               hover_name='reason',
                               title="Churn Reasons: Frequency vs Revenue Impact",
                               color_continuous_scale='Reds')
        fig_bubble.update_xaxes(title_text="Number of Customers")
        fig_bubble.update_yaxes(title_text="Revenue Impact ($)")
        st.plotly_chart(fig_bubble, use_container_width=True)
    
    with col2:
        # Top reasons bar chart with numbers
        fig_reasons = px.bar(x=churn_reasons.values, y=churn_reasons.index, 
                            orientation='h',
                            title="Top Churn Reasons",
                            color_discrete_sequence=['#f39c12'],
                            text=churn_reasons.values)
        fig_reasons.update_traces(texttemplate='%{text}', textposition='outside')
        fig_reasons.update_layout(yaxis_title="Reason", xaxis_title="Count")
        st.plotly_chart(fig_reasons, use_container_width=True)
else:
    st.info("No churn reason data available for current filters")

# Actionable Insights
st.header("Actionable Insights")
col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
    <div class="insight-box">
    <h3>IMMEDIATE ACTIONS</h3>
    <ul>
    <li>Hubungi {critical_risk} pelanggan risiko kritis dalam 12 jam</li>
    <li>Hubungi {high_risk} pelanggan risiko tinggi dalam 24 jam</li>
    <li>Pantau {medium_risk} pelanggan risiko sedang mingguan</li>
    <li>Fokus pada alasan churn teratas untuk dampak maksimal</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="insight-box">
    <h3>POTENTIAL IMPACT</h3>
    <ul>
    <li>Pendapatan berisiko: ${churned_revenue:,.0f}</li>
    <li>Nilai pemulihan rata-rata: ${churned_revenue/churned if churned > 0 else 0:,.0f} per pelanggan</li>
    <li>Pelanggan risiko kritis + tinggi: {critical_risk + high_risk} orang</li>
    <li>Potensi ROI: 300-500% dari upaya retensi</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

# Data Explorer
with st.expander("Data Explorer"):
    st.subheader("Dataset Summary")
    
    # Dataset Info Cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Records", f"{len(df):,}")
    with col2:
        st.metric("Filtered Records", f"{len(filtered_df):,}")
    with col3:
        st.metric("Total Columns", len(df.columns))
    with col4:
        st.metric("Filter Efficiency", f"{len(filtered_df)/len(df)*100:.1f}%")
    
    st.divider()
    
    # Column Descriptions in Two Columns
    st.subheader("Column Dictionary")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        
        
        **Customer ID**  
        A unique identifier that distinguishes each customer in the dataset
        
        **Satisfaction Score**  
        Numerical rating from 1 (Very Unsatisfied) to 5 (Very Satisfied) measuring customer satisfaction
        
        **CLTV (Customer Lifetime Value)**  
        Total revenue potential from a customer in dollars over their entire relationship
        
        **Customer Status**  
        Current status at quarter end: Churned (left), Stayed (retained), or Joined (new customer)
        
        **Churn Score**  
        Predictive score from 0-100 indicating probability of customer churn based on ML model
        
        **Churn Label**  
        Binary indicator: Yes = customer left this quarter, No = customer remained
        """)
    
    with col2:
        st.markdown("""
        
        
        **Churn Value**  
        Numerical representation: 1 = churned customer, 0 = retained customer
        
        **Churn Category**  
        Primary reason category for churn: Competitor, Dissatisfaction, Price, Service, Product
        
        **Churn Reason**  
        Detailed specific reason for customer churn or 'Unknown' for retained customers
        
        **Satisfaction Level**  
        Categorical grouping: Very Low, Low, Medium, High based on satisfaction score
        
        **CLTV Quartile**  
        Revenue segmentation: Q1 (Low), Q2 (Medium-Low), Q3 (Medium-High), Q4 (High)
        
        **Churn Risk Level**  
        Risk categorization: Critical Risk, High Risk, Medium Risk, Low Risk
        """)
    
    st.divider()
    
    # Sample Data with better formatting
    st.subheader("Sample Data Preview")
    st.dataframe(
        filtered_df.head(10), 
        use_container_width=True,
        hide_index=True
    )

st.markdown("---")
# st.markdown("**🎯 Customer Churn Analytics Dashboard** | Using fix.csv | Built with Streamlit & Plotly")
