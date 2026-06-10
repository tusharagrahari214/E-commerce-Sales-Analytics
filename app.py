import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import plotly.express as px
import plotly.graph_objects as go
import joblib, json, os, warnings
warnings.filterwarnings('ignore')

st.set_page_config(
    page_title='E-Commerce Sales Dashboard',
    page_icon='🛒',
    layout='wide'
)

# ── Load data and models ──────────────────────────────────────
@st.cache_data
def load_data():
    # Automatically download the data if it is missing on the cloud server
    if not os.path.exists('data/OnlineRetail.xlsx') and not os.path.exists('data/OnlineRetail.csv'):
        os.makedirs('data', exist_ok=True)
        import urllib.request
        try:
            url = "https://github.com/erkansirin78/datasets/raw/master/OnlineRetail.csv"
            urllib.request.urlretrieve(url, 'data/OnlineRetail.csv')
        except Exception as download_error:
            st.error(f"Failed to fetch dataset: {download_error}")

    try:
        df = pd.read_excel('data/OnlineRetail.xlsx', engine='openpyxl')
    except Exception as e:
        try:
            df = pd.read_csv('data/OnlineRetail.csv', encoding='ISO-8859-1', sep=';', decimal=',')
        except Exception as e2:
            df = pd.read_csv('data/OnlineRetail.csv', encoding='ISO-8859-1')

    try:
        df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'], dayfirst=True)
    except:
        df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])

    df = df[~df['InvoiceNo'].astype(str).str.startswith('C')]
    df = df[df['Quantity'] > 0]
    df = df[df['UnitPrice'] > 0]
    df = df.dropna(subset=['Description'])
    df['TotalPrice']  = df['Quantity'] * df['UnitPrice']
    df['Year']        = df['InvoiceDate'].dt.year
    df['Month']       = df['InvoiceDate'].dt.month
    df['MonthName']   = df['InvoiceDate'].dt.strftime('%b')
    df['DayName']     = df['InvoiceDate'].dt.strftime('%A')
    df['Hour']        = df['InvoiceDate'].dt.hour
    df['YearMonth']   = df['InvoiceDate'].dt.to_period('M').astype(str)
    df['Quarter']     = df['InvoiceDate'].dt.quarter
    df_rfm = df.dropna(subset=['CustomerID']).copy()
    df_rfm['CustomerID'] = df_rfm['CustomerID'].astype(int)
    return df, df_rfm

@st.cache_data
def load_rfm():
    return pd.read_csv('models/rfm_table.csv')

@st.cache_resource
def load_kpis():
    with open('models/kpis.json') as f:
        return json.load(f)

df, df_rfm = load_data()
rfm        = load_rfm()
kpis       = load_kpis()

# ── Sidebar ───────────────────────────────────────────────────
st.sidebar.title('🛒 E-Commerce Dashboard')
st.sidebar.markdown('---')
page = st.sidebar.radio('Navigate', [
    'Overview',
    'Sales Trends',
    'Products',
    'Customers & RFM',
    'Cohort Analysis'
])

countries = ['All'] + sorted(df['Country'].unique().tolist())
selected_country = st.sidebar.selectbox('Filter by Country', countries)

year_options = ['All'] + sorted(df['Year'].unique().tolist())
selected_year = st.sidebar.selectbox('Filter by Year', year_options)

if selected_country != 'All':
    df = df[df['Country'] == selected_country]
    df_rfm = df_rfm[df_rfm['Country'] == selected_country]

if selected_year != 'All':
    df = df[df['Year'] == selected_year]
    df_rfm = df_rfm[df_rfm['Year'] == selected_year]

# ── PAGE 1: Overview ─────────────────────────────────────────
if page == 'Overview':
    st.title('Sales Overview')

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric('Total Revenue',    f"£{df['TotalPrice'].sum():,.0f}")
    k2.metric('Total Orders',     f"{df['InvoiceNo'].nunique():,}")
    k3.metric('Total Customers',  f"{df_rfm['CustomerID'].nunique():,}")
    k4.metric('Total Products',   f"{df['StockCode'].nunique():,}")
    aov = df.groupby('InvoiceNo')['TotalPrice'].sum().mean()
    k5.metric('Avg Order Value',  f"£{aov:,.2f}")

    st.markdown('---')

    # Monthly revenue trend
    monthly_rev = (df.groupby('YearMonth')['TotalPrice']
                   .sum().reset_index().sort_values('YearMonth'))
    fig1 = px.line(monthly_rev, x='YearMonth', y='TotalPrice',
                   title='Monthly Revenue Trend',
                   labels={'TotalPrice':'Revenue (£)','YearMonth':'Month'},
                   markers=True, color_discrete_sequence=['#3498db'])
    fig1.update_layout(xaxis_tickangle=45)
    st.plotly_chart(fig1, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        top_c = (df.groupby('Country')['TotalPrice']
                 .sum().sort_values(ascending=False).head(10).reset_index())
        fig2 = px.bar(top_c, x='Country', y='TotalPrice',
                      title='Top 10 Countries by Revenue',
                      color='TotalPrice', color_continuous_scale='Blues',
                      labels={'TotalPrice':'Revenue (£)'})
        fig2.update_layout(xaxis_tickangle=30)
        st.plotly_chart(fig2, use_container_width=True)

    with col2:
        qtr = (df.groupby(['Year','Quarter'])['TotalPrice']
               .sum().reset_index())
        qtr['Label'] = qtr['Year'].astype(str) + ' Q' + qtr['Quarter'].astype(str)
        fig3 = px.bar(qtr, x='Label', y='TotalPrice',
                      title='Quarterly Revenue',
                      color='TotalPrice', color_continuous_scale='RdYlGn',
                      labels={'TotalPrice':'Revenue (£)'})
        st.plotly_chart(fig3, use_container_width=True)

# ── PAGE 2: Sales Trends ─────────────────────────────────────
elif page == 'Sales Trends':
    st.title('Sales Trends')

    col1, col2 = st.columns(2)
    with col1:
        dow_rev = df.groupby('DayName')['TotalPrice'].sum()
        day_order = ['Monday','Tuesday','Wednesday','Thursday',
                     'Friday','Saturday','Sunday']
        dow_rev = dow_rev.reindex(day_order).reset_index()
        fig4 = px.bar(dow_rev, x='DayName', y='TotalPrice',
                      title='Revenue by Day of Week',
                      color='TotalPrice', color_continuous_scale='Viridis',
                      labels={'TotalPrice':'Revenue (£)','DayName':'Day'})
        st.plotly_chart(fig4, use_container_width=True)

    with col2:
        hr_rev = df.groupby('Hour')['TotalPrice'].sum().reset_index()
        fig5 = px.line(hr_rev, x='Hour', y='TotalPrice',
                       title='Revenue by Hour of Day',
                       markers=True, color_discrete_sequence=['#9b59b6'],
                       labels={'TotalPrice':'Revenue (£)'})
        st.plotly_chart(fig5, use_container_width=True)

    # AOV over time
    monthly_aov = (df.groupby(['YearMonth','InvoiceNo'])['TotalPrice']
                   .sum().reset_index()
                   .groupby('YearMonth')['TotalPrice'].mean()
                   .reset_index().sort_values('YearMonth'))
    monthly_aov.columns = ['YearMonth','AOV']
    fig6 = px.line(monthly_aov, x='YearMonth', y='AOV',
                   title='Monthly Average Order Value (AOV)',
                   markers=True, color_discrete_sequence=['#e74c3c'],
                   labels={'AOV':'AOV (£)'})
    fig6.update_layout(xaxis_tickangle=45)
    st.plotly_chart(fig6, use_container_width=True)

# ── PAGE 3: Products ─────────────────────────────────────────
elif page == 'Products':
    st.title('Product Analysis')

    top_n = st.slider('Show top N products', 5, 30, 10)

    col1, col2 = st.columns(2)
    with col1:
        top_rev = (df.groupby('Description')['TotalPrice']
                   .sum().sort_values(ascending=False).head(top_n).reset_index())
        top_rev['Description'] = top_rev['Description'].str[:35]
        fig7 = px.bar(top_rev, x='TotalPrice', y='Description',
                      orientation='h', title=f'Top {top_n} by Revenue',
                      color='TotalPrice', color_continuous_scale='Blues',
                      labels={'TotalPrice':'Revenue (£)'})
        fig7.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig7, use_container_width=True)

    with col2:
        top_qty = (df.groupby('Description')['Quantity']
                   .sum().sort_values(ascending=False).head(top_n).reset_index())
        top_qty['Description'] = top_qty['Description'].str[:35]
        fig8 = px.bar(top_qty, x='Quantity', y='Description',
                      orientation='h', title=f'Top {top_n} by Quantity',
                      color='Quantity', color_continuous_scale='Greens',
                      labels={'Quantity':'Units Sold'})
        fig8.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig8, use_container_width=True)

    # Product search
    st.markdown('---')
    st.subheader('Product Search')
    search = st.text_input('Search product name:')
    if search:
        results = (df[df['Description'].str.contains(search, case=False, na=False)]
                   .groupby('Description')
                   .agg(Revenue=('TotalPrice','sum'),
                        Quantity=('Quantity','sum'),
                        Orders=('InvoiceNo','nunique'))
                   .sort_values('Revenue', ascending=False)
                   .head(20))
        results['Revenue'] = results['Revenue'].apply(lambda x: f'£{x:,.2f}')
        st.dataframe(results)

# ── PAGE 4: Customers & RFM ──────────────────────────────────
elif page == 'Customers & RFM':
    st.title('Customer Analysis & RFM Segmentation')

    col1, col2, col3 = st.columns(3)
    col1.metric('Total Customers',   f"{rfm.shape[0]:,}")
    col2.metric('Champions',
                f"{(rfm['Segment']=='Champions').sum():,}")
    col3.metric('At Risk + Lost',
                f"{rfm['Segment'].isin(['At Risk','Lost Customers']).sum():,}")

    col1, col2 = st.columns(2)
    with col1:
        seg_counts = rfm['Segment'].value_counts().reset_index()
        seg_counts.columns = ['Segment','Count']
        fig9 = px.pie(seg_counts, names='Segment', values='Count',
                      title='Customer Distribution by RFM Segment',
                      color_discrete_sequence=px.colors.qualitative.Set2)
        st.plotly_chart(fig9, use_container_width=True)

    with col2:
        seg_rev = rfm.groupby('Segment')['Monetary'].sum().reset_index()
        fig10 = px.bar(seg_rev, x='Segment', y='Monetary',
                       title='Revenue by RFM Segment',
                       color='Segment',
                       color_discrete_sequence=px.colors.qualitative.Set2,
                       labels={'Monetary':'Revenue (£)'})
        st.plotly_chart(fig10, use_container_width=True)

    # RFM Scatter
    fig11 = px.scatter(rfm, x='Recency', y='Monetary',
                       color='Segment', size='Frequency',
                       title='RFM Scatter: Recency vs Monetary Value',
                       labels={'Recency':'Days Since Last Purchase',
                               'Monetary':'Total Spend (£)'},
                       color_discrete_sequence=px.colors.qualitative.Set2,
                       opacity=0.7)
    st.plotly_chart(fig11, use_container_width=True)

    # Customer lookup
    st.markdown('---')
    st.subheader('Customer Lookup')
    cust_id = st.number_input('Enter Customer ID (e.g., 17850, 12347, 12346):', min_value=12346, max_value=18287, value=17850, step=1)
    if cust_id >= 12346:
        row = rfm[rfm['CustomerID'] == cust_id]
        if not row.empty:
            r = row.iloc[0]
            c1, c2, c3, c4 = st.columns(4)
            c1.metric('Recency',   f"{int(r['Recency'])} days")
            c2.metric('Frequency', f"{int(r['Frequency'])} orders")
            c3.metric('Monetary',  f"£{r['Monetary']:,.2f}")
            c4.metric('Segment',   r['Segment'])
        else:
            st.warning(f"Customer {cust_id} not found.")

# ── PAGE 5: Cohort Analysis ───────────────────────────────────
elif page == 'Cohort Analysis':
    st.title('Cohort Retention Analysis')
    st.markdown('Each cell shows the % of customers from the cohort who returned that month.')

    img = plt.imread('charts/11_cohort_analysis.png')
    st.image(img, use_column_width=True)

    st.markdown('---')
    st.subheader('How to read this chart')
    st.markdown('''
- **Row** = month when the customer first purchased (their cohort)
- **Column 0** = their first month (always 100%)
- **Column 1** = % who came back in month 2
- **Column 2** = % who came back in month 3
- **Darker red** = lower retention | **Lighter/yellow** = higher retention
- A good e-commerce business targets 20%+ month-1 retention
''')

st.markdown('---')
st.caption('Dataset: UCI Online Retail | Period: Dec 2010 — Dec 2011')
