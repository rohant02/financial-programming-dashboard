# -*- coding: utf-8 -*-
###############################################################################
# FINANCIAL DASHBOARD EXAMPLE - v3
###############################################################################

#==============================================================================
# Initiating
#==============================================================================

# Libraries
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from datetime import datetime, timedelta
import yfinance as yf
import streamlit as st
from plotly.subplots import make_subplots

#==============================================================================
# Header
#==============================================================================

def render_header():
    """
    This function render the header of the dashboard with the following items:
        - Title
        - Dashboard description
        - 3 selection boxes to select: Ticker, Start Date, End Date
    """
    
    # Add dashboard title and description
    st.title("Financial Dashboard")
    col1, col2 = st.columns([1,5])
    col1.write("Data source:")
    col2.image('./img/yahoo_finance.png', width=100)
    
    # Add the ticker selection on the sidebar
    # Get the list of stock tickers from S&P500
    ticker_list = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]['Symbol']
    
    # Add the selection boxes
    col1, col2, col3 = st.columns(3)  # Create 3 columns
    
    # Ticker name
    global ticker  # Set this variable as global, so the functions in all of the tabs can read it
    ticker = col1.selectbox("Ticker", ticker_list)
    # Begin and end dates
    global start_date, end_date  # Set this variable as global, so all functions can read it
    start_date = col2.date_input("Start date", datetime.today().date() - timedelta(days=30))
    end_date = col3.date_input("End date", datetime.today().date())

    

#==============================================================================
# Tab 1
#==============================================================================

def render_tab1():
    """
    This function render the Tab 1 - Company Profile of the dashboard.
    """
    
    # Show to stock image
    col1, col2, col3 = st.columns([1, 3, 1])
    col2.image('./img/stock_market.jpg', use_column_width=True,
               caption='Company Stock Information')
    
    # Get the company information
    @st.cache_data
    def GetCompanyInfo(ticker):
        """
        This function get the company information from Yahoo Finance.
        """
        return yf.Ticker(ticker).info
    
    # If the ticker is already selected
    if ticker != '':
        # Get the company information in list format
        info = GetCompanyInfo(ticker)
        
        # Show the company description using markdown + HTML
        st.write('**1. Business Summary:**')
        st.markdown('<div style="text-align: justify;">' + \
                    info['longBusinessSummary'] + \
                    '</div><br>',
                    unsafe_allow_html=True)
        
        # Show some statistics as a DataFrame
        st.write('**2. Key Statistics:**')
        info_keys = {'previousClose':'Previous Close',
                     'open'         :'Open',
                     'bid'          :'Bid',
                     'ask'          :'Ask',
                     'marketCap'    :'Market Cap',
                     'volume'       :'Volume',
                     }
        company_stats = {}  # Dictionary
        for key in info_keys:
            company_stats.update({info_keys[key]:info[key]})
        company_stats = pd.DataFrame({'Value':pd.Series(company_stats)})  # Convert to DataFrame
        st.dataframe(company_stats)

#==============================================================================
# Tab 2
#==============================================================================

def render_tab2():
    """
    This function renders the Chart tab, providing options for selecting date range, 
    interval, and plot type, and displaying volume bars and a 50-day moving average.
    """

    st.write("## Stock Price and Volume Chart")

    # User options for date range, interval, and chart type
    interval = st.selectbox("Select Duration", ["1M", "3M", "6M", "YTD", "1Y", "3Y", "5Y", "Max"])
    chart_type = st.selectbox("Select Chart Type", ["Line", "Candlestick"])

    # Define date range based on selected duration
    end_date = datetime.today()
    if interval == "1M":
        start_date = end_date - timedelta(days=30)
        interval_str = '1d'
    elif interval == "3M":
        start_date = end_date - timedelta(days=90)
        interval_str = '1d'
    elif interval == "6M":
        start_date = end_date - timedelta(days=180)
        interval_str = '1d'
    elif interval == "YTD":
        start_date = datetime(end_date.year, 1, 1)
        interval_str = '1d'
    elif interval == "1Y":
        start_date = end_date - timedelta(days=365)
        interval_str = '1d'
    elif interval == "3Y":
        start_date = end_date - timedelta(days=3 * 365)
        interval_str = '1mo'
    elif interval == "5Y":
        start_date = end_date - timedelta(days=5 * 365)
        interval_str = '1mo'
    else:  # Max
        start_date = "1900-01-01"
        interval_str = '1mo'

    # Fetch stock data for the selected ticker and date range
    if ticker:
        stock_data = yf.download(ticker, start=start_date, end=end_date, interval=interval_str)

        if not stock_data.empty:
            # Calculate the 50-day moving average
            stock_data['MA50'] = stock_data['Close'].rolling(window=50).mean()

            # Initialize the plot with secondary y-axis
            fig = make_subplots(specs=[[{"secondary_y": True}]])

            # Select plot type based on user choice
            if chart_type == "Line":
                # Line plot with 50-day MA
                fig.add_trace(
                    go.Scatter(
                        x=stock_data.index,
                        y=stock_data['Close'],
                        mode='lines',
                        name='Stock Price',
                        line=dict(color='blue')
                    ),
                    secondary_y=True
                )
            else:
                # Candlestick plot
                fig.add_trace(
                    go.Candlestick(
                        x=stock_data.index,
                        open=stock_data['Open'],
                        high=stock_data['High'],
                        low=stock_data['Low'],
                        close=stock_data['Close'],
                        name='Candlestick'
                    ),
                    secondary_y=True
                )

            # Add the 50-day moving average
            fig.add_trace(
                go.Scatter(
                    x=stock_data.index,
                    y=stock_data['MA50'],
                    mode='lines',
                    name='50-day MA',
                    line=dict(color='orange', width=1.5, dash='dash')
                ),
                secondary_y=True
            )

            # Volume bars, colored by price change
            fig.add_trace(
                go.Bar(
                    x=stock_data.index,
                    y=stock_data['Volume'],
                    marker_color=np.where(stock_data['Close'].pct_change() < 0, 'red', 'green'),
                    name="Volume"
                ),
                secondary_y=False
            )

            # Add range selector buttons
            fig.update_xaxes(
                rangeslider_visible=False,
                rangeselector=dict(
                    buttons=list([
                        dict(count=1, label="1M", step="month", stepmode="backward"),
                        dict(count=3, label="3M", step="month", stepmode="backward"),
                        dict(count=6, label="6M", step="month", stepmode="backward"),
                        dict(count=1, label="YTD", step="year", stepmode="todate"),
                        dict(count=1, label="1Y", step="year", stepmode="backward"),
                        dict(count=3, label="3Y", step="year", stepmode="backward"),
                        dict(count=5, label="5Y", step="year", stepmode="backward"),
                        dict(step="all")
                    ])
                )
            )

            # Customize the layout
            fig.update_layout(
                title=f"{ticker} Stock Price and Volume",
                template='plotly_white',
                xaxis_title="Date",
                yaxis_title="Volume",
                yaxis2_title="Price (USD)",
                showlegend=True
            )

            # Adjust the volume y-axis range for readability
            fig.update_yaxes(range=[0, stock_data['Volume'].max() * 1.1], secondary_y=False)

            # Display the chart
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.write("No data available for the selected time range.")

def render_tab3():
    # Get the company information
    if ticker:
        stock_info = yf.Ticker(ticker)
        info = stock_info.info

        # Display Company Profile
        st.write("## Company Profile")
        st.write(info.get("longBusinessSummary", "Description not available."))

        # Display Key Statistics
        st.write("## Key Statistics")
        stats_keys = {
            "previousClose": "Previous Close",
            "open": "Open",
            "bid": "Bid",
            "ask": "Ask",
            "dayHigh": "Day's High",
            "dayLow": "Day's Low",
            "fiftyTwoWeekHigh": "52 Week High",
            "fiftyTwoWeekLow": "52 Week Low",
            "volume": "Volume",
            "averageVolume": "Avg. Volume",
            "marketCap": "Market Cap",
            "beta": "Beta (5Y Monthly)",
            "peRatio": "PE Ratio (TTM)",
            "epsTrailingTwelveMonths": "EPS (TTM)",
            "dividendYield": "Forward Dividend & Yield",
            "exDividendDate": "Ex-Dividend Date",
            "earningsDate": "Earnings Date",
        }
        stats_data = {label: info.get(key, "N/A") for key, label in stats_keys.items()}
        stats_df = pd.DataFrame(list(stats_data.items()), columns=["Metric", "Value"])
        st.table(stats_df)

        # Add option to select different time intervals
        st.write("## Stock Price Chart")
        interval = st.selectbox("Select Time Interval", ["1M", "3M", "6M", "YTD", "1Y", "3Y", "5Y", "Max"])

        # Define date range based on the selected interval
        end_date = datetime.today()
        if interval == "1M":
            start_date = end_date - timedelta(days=30)
        elif interval == "3M":
            start_date = end_date - timedelta(days=90)
        elif interval == "6M":
            start_date = end_date - timedelta(days=180)
        elif interval == "YTD":
            start_date = datetime(end_date.year, 1, 1)
        elif interval == "1Y":
            start_date = end_date - timedelta(days=365)
        elif interval == "3Y":
            start_date = end_date - timedelta(days=3 * 365)
        elif interval == "5Y":
            start_date = end_date - timedelta(days=5 * 365)
        else:  # Max
            start_date = "1900-01-01"  # Retrieve all available data

        # Retrieve historical stock data
        stock_data = stock_info.history(start=start_date, end=end_date)

        # Plot candlestick chart
        fig = go.Figure(data=[go.Candlestick(
            x=stock_data.index,
            open=stock_data['Open'],
            high=stock_data['High'],
            low=stock_data['Low'],
            close=stock_data['Close'],
        )])
        fig.update_layout(title=f"{ticker} Stock Price", xaxis_title="Date", yaxis_title="Price (USD)")
        st.plotly_chart(fig, use_container_width=True)

        # Display Major Shareholders if available
        st.write("## Major Shareholders")
        try:
            holders = stock_info.major_holders
            
            # Create a custom DataFrame with descriptive labels
            holders_data = {
                "Description": [
                    "% of Shares Held by All Insider",
                    "% of Shares Held by Institutions",
                    "% of Float Held by Institutions",
                    "Number of Institutions Holding Shares"
                ],
                "Value": [
                    f"{holders.iloc[0, 0] * 100:.2f}%",
                    f"{holders.iloc[1, 0] * 100:.2f}%",
                    f"{holders.iloc[2, 0] * 100:.2f}%",
                    f"{holders.iloc[3, 0]:,.0f}"
                ]
            }
            holders_df = pd.DataFrame(holders_data)
            st.table(holders_df)
            
        except Exception as e:
            st.write("Shareholder information is not available.")
            st.write(e)
def render_tab4():
    st.write("## Monte Carlo Simulation for Stock Price Prediction")
    num_simulations = st.selectbox("Select Number of Simulations", [200, 500, 1000])
    time_horizon = st.selectbox("Select Time Horizon (Days)", [30, 60, 90])

    if ticker:
        stock_info = yf.Ticker(ticker)
        historical_data = stock_info.history(period="1y")  # Get 1 year of data
        close_prices = historical_data['Close']
        
        # Calculate daily returns and standard deviation
        daily_returns = close_prices.pct_change().dropna()
        mu = daily_returns.mean()
        sigma = daily_returns.std()

        # Monte Carlo simulation
        last_price = close_prices[-1]
        simulation_df = pd.DataFrame()

        for _ in range(num_simulations):
            prices = [last_price]
            for _ in range(time_horizon):
                price = prices[-1] * np.exp((mu - 0.5 * sigma**2) + sigma * np.random.normal())
                prices.append(price)
            simulation_df[_] = prices

        # Plotting the Monte Carlo simulation
        fig, ax = plt.subplots()
        simulation_df.plot(ax=ax, legend=False, alpha=0.1, color="blue")
        ax.set_title(f"Monte Carlo Simulation for {ticker} stock price in next {time_horizon} days")
        ax.set_xlabel("Day")
        ax.set_ylabel("Price")
        ax.axhline(y=last_price, color="red", linestyle="--", label=f"Current stock price: {last_price:.2f}")
        ax.legend()

        # Display the plot
        st.pyplot(fig)

        # Value at Risk (VaR) calculation at 95% confidence level
        final_prices = simulation_df.iloc[-1, :]
        VaR_95 = np.percentile(final_prices, 5)
        st.write(f" Value at Risk (VaR) at 95% confidence level is ${VaR_95:.2f}")
def render_tab5():
    st.title("Financials")
    statement_type = st.selectbox("Select Financial Statement", ["Income Statement", "Balance Sheet", "Cash Flow"])
    period_type = st.selectbox("Select Period", ["Annual", "Quarterly"])
    if ticker:
        stock_info = yf.Ticker(ticker)

        # Display the selected financial statement
        if statement_type == "Income Statement":
            if period_type == "Annual":
                data = stock_info.financials  # Annual income statement
            else:
                data = stock_info.quarterly_financials  # Quarterly income statement

        elif statement_type == "Balance Sheet":
            if period_type == "Annual":
                data = stock_info.balance_sheet  # Annual balance sheet
            else:
                data = stock_info.quarterly_balance_sheet  # Quarterly balance sheet

        elif statement_type == "Cash Flow":
            if period_type == "Annual":
                data = stock_info.cashflow  # Annual cash flow
            else:
                data = stock_info.quarterly_cashflow  # Quarterly cash flow

        # Display the data in a table format
        if not data.empty:
            st.write(f"### {statement_type} ({period_type})")
            st.dataframe(data, use_container_width=True)
        else:
            st.write(f"No {statement_type} data available for the selected period.")
#def fetch_news():
    
    

def render_tab6():
    st.title("News")
    if ticker:
        stock_info = yf.Ticker(ticker)
        
        # Try to fetch news using yfinance (note that not all tickers may have news available)
        if hasattr(stock_info, 'news') and stock_info.news:
            articles = stock_info.news

            # Display each article
            for article in articles[:10]:  # Show up to 10 articles
                st.write(f"[{article['title']}]({article['link']})")
                #st.write(f"Published at: {article['providerPublishTime']}")
                st.write(article['publisher'])
                #st.write(article['summary'])
                #st.image(article.get('thumbnail', {}).get('resolutions', [{}])[-1].get('url'), use_column_width=True)
                st.write("---")
                publish_time = datetime.fromtimestamp(article['providerPublishTime']).strftime('%Y-%m-%d %H:%M:%S')
                st.write(f"Published at: {publish_time}")
        else:
            st.write("No recent news articles found for this company.")

def render_tab7():
    """
    This function renders the Chart tab with an interactive line chart
    with a shaded area under it, a gradient background, and volume bars.
    """

    st.write("## Stock Price Chart")

    # Add a selection for different time intervals
    interval = st.selectbox("Select Time Interval", ["1D", "5D", "1M", "6M", "YTD", "1Y", "5Y", "Max"])

    # Define date range based on the selected interval
    end_date = datetime.today()
    if interval == "1D":
        start_date = end_date - timedelta(days=1)
        interval_str = '1m'  # 1 minute interval for intraday data
    elif interval == "5D":
        start_date = end_date - timedelta(days=5)
        interval_str = '15m'  # 15-minute interval for 5-day range
    elif interval == "1M":
        start_date = end_date - timedelta(days=30)
        interval_str = '1d'
    elif interval == "6M":
        start_date = end_date - timedelta(days=180)
        interval_str = '1d'
    elif interval == "YTD":
        start_date = datetime(end_date.year, 1, 1)
        interval_str = '1d'
    elif interval == "1Y":
        start_date = end_date - timedelta(days=365)
        interval_str = '1d'
    elif interval == "5Y":
        start_date = end_date - timedelta(days=5 * 365)
        interval_str = '1wk'
    else:  # Max
        start_date = "1900-01-01"  # Retrieve all available data
        interval_str = '1mo'

    # Fetch stock data for the selected ticker and date range
    if ticker:
        stock_data = yf.download(ticker, start=start_date, end=end_date, interval=interval_str)

        if not stock_data.empty:
            # Create a line chart with shaded area
            fig = go.Figure()

            # Line with shaded area
            fig.add_trace(
                go.Scatter(
                    x=stock_data.index,
                    y=stock_data['Close'],
                    mode='lines',
                    line=dict(color='blue', width=2),
                    fill='tozeroy',
                    name='Price'
                )
            )

            # Volume bars
            fig.add_trace(
                go.Bar(
                    x=stock_data.index,
                    y=stock_data['Volume'],
                    name="Volume",
                    marker=dict(color='rgba(0, 100, 255, 0.4)'),  # Semi-transparent blue for volume
                    yaxis="y2"
                )
            )

            # Add a gradient background by using a background image
            fig.update_layout(
                title=f"{ticker} Stock Price",
                xaxis_title="Time",
                yaxis_title="Price (USD)",
                yaxis2=dict(
                    title="Volume",
                    overlaying="y",
                    side="right",
                    showgrid=False
                ),
                showlegend=False,
                xaxis_rangeslider_visible=False,
                template="plotly_white",
                images=[dict(
                    source="https://www.gradientmagic.com/static/images/gradients/preview/1.svg",  # URL of a white-to-blue gradient image
                    xref="paper", yref="paper",
                    x=0, y=1,
                    sizex=1, sizey=1,
                    sizing="stretch",
                    opacity=0.2,
                    layer="below"
                )]
            )

            # Display the chart
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.write("No data available for the selected time range.")

#==============================================================================
# Main body
#==============================================================================

# Render the header
render_header()

# Render the tabs
tab1, tab2, tab3, tab4, tab5,tab6 = st.tabs(["Company profile", "Chart", "Summary","Monte Carlo Simulation","Financial Information",'News'])
with tab1:
    render_tab1()
with tab2:
    render_tab2()
with tab3:
    render_tab3()
with tab4:
    render_tab4()
with tab5:
    render_tab5()
with tab6:
    render_tab6()

    
# Customize the dashboard with CSS
st.markdown(
    """
    <style>
        .stApp {
            background: #ffffff;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

###############################################################################
# END
###############################################################################