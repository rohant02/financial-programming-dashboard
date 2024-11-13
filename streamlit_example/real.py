import numpy as np
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import yfinance as yf
import streamlit as st
from plotly.subplots import make_subplots
import plotly.express as px
from dateutil.relativedelta import relativedelta  # Use relativedelta for years

# Set today's date
today = datetime.today()

# Configure Streamlit layout to wide
st.set_page_config(layout="wide")

# Home Page Title
st.title('Financial Dashboard')
summary_data, chart_data, financials_data, monte_carlo , top10_news  = st.tabs(['Summary','Chart','Financials','Monte Carlo Simulation','Top 10 News'])
# Sidebar for inputs
st.sidebar.title("Choose stock and time interval")

# Fetch S&P 500 ticker list
ticker_list = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]['Symbol']

# Sidebar user inputs
ticker_symbol = st.sidebar.selectbox('Select a Stock Ticker', ticker_list)
ticker = yf.Ticker(ticker_symbol)
start_date = st.sidebar.date_input('Start Date', value=today - relativedelta(years=1))
end_date = st.sidebar.date_input('End Date', value=today)

# Download data
data = yf.download(ticker_symbol, start=start_date, end=end_date)

# Prepare DataFrame
df = pd.DataFrame(data)

# Convert data to CSV for download
csv = df.to_csv(index=True).encode('utf-8')

# Sidebar Buttons
if "show_data" not in st.session_state:
    st.session_state.show_data = False

if st.sidebar.button("Show/Hide Data"):
    st.session_state.show_data = not st.session_state.show_data

st.sidebar.download_button(
    label="Download Data as CSV",
    data=csv,
    file_name=f'{ticker_symbol}_data.csv',
    mime='text/csv'
)

# Main Page: Conditionally render the dataframe
if st.session_state.show_data:
    st.subheader(f"Stock Data for {ticker_symbol}")
    st.dataframe(data, use_container_width=True)


# Main Page: Line Chart
fig = px.line(data, x=data.index, y='Adj Close', title=f'{ticker_symbol} Stock Prices')
st.plotly_chart(fig)


import streamlit as st



# Summary Data Tab
with summary_data:
    st.write('Summary of Company')
    col1, col2 = st.columns([1,5])
    col1.write("Company:")
    logo = ticker.info.get("logo_url")
    col2.image(logo, caption="Company Logo")

# Chart Data Tab
with chart_data:
    st.write('Chart')
    

# Financials Data Tab
with financials_data:
    st.write('Financials')
    

# Monte Carlo Simulation Tab
with monte_carlo:
    st.write('Monte Carlo Simulation')
    

# Top 10 News Tab
with top10_news:
    st.write('Top 10 News')
    
