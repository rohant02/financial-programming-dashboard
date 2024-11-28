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
# References: ChatGPT 4.0,
# https://youtu.be/fdFfpEtv5BU (Financial Programming with Ritvik, CFA)
# https://youtu.be/yaqO5J31ojQ (Financial Programming with Ritvik, CFA)
# Code Provided by Prof. Minh Phan in the coursework
#==============================================================================


#==============================================================================
# Sidebar
#==============================================================================



def render_sidebar():
    """
    This function renders the sidebar of the dashboard with the following items:
        - Title
        - Dashboard description
        - Selection boxes to select: Ticker, Start Date, End Date
        - Download button for data
    """
    st.sidebar.title("Financial Dashboard")
    st.sidebar.write("Data source:")
    st.sidebar.image('./img/yahoo_finance.png', width=100)

    # Get ticker list from Wikipedia
    ticker_list = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]['Symbol']

    # Selection inputs in the sidebar
    global ticker
    ticker = st.sidebar.selectbox("Ticker", ticker_list)

    global start_date, end_date
    start_date = st.sidebar.date_input("Start date", datetime.today().date() - timedelta(days=30))
    end_date = st.sidebar.date_input("End date", datetime.today().date())

    # Download data
    data = yf.download(ticker, start=start_date, end=end_date)
    df = pd.DataFrame(data)

    # Create CSV file and add download button
    csv = df.to_csv(index=True).encode('utf-8')
    st.sidebar.download_button(
        label="Download",
        data=csv,
        file_name=f'{ticker}_data.csv',
        mime='text/csv'
    )

    if st.sidebar.button("Refresh Data"):
        st.sidebar.success("Data refreshed successfully!")



       

#==============================================================================
# Tab 1
#==============================================================================

def render_tab1():
    """
    This function renders first Tab - Company Profile of the dashboard.
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
        
        coll1,coll2,coll3 = st.columns(3)
        coll2.dataframe(company_stats)
        

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
    time_interval = st.selectbox("Select Time Interval", ["1d", "1mo", "1y"])

    # Define date range based on selected duration
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
        start_date = "1900-01-01"

    # Fetch stock data for the selected ticker and date range
    if ticker:
        stock_data = yf.download(ticker, start=start_date, end=end_date, interval=time_interval)

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
                showlegend=True,
                height=800
            )

            # Adjust the volume y-axis range for readability
            fig.update_yaxes(range=[0, stock_data['Volume'].max() * 1.1], secondary_y=False)

            # Display the chart
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.write("No data available for the selected time range.")

#==============================================================================
# Tab 3
#==============================================================================

def render_tab3():
    
    if ticker:
        stock_info = yf.Ticker(ticker)
        info = stock_info.info

        
        st.write("## Company Profile")
        st.write(info.get("longBusinessSummary", "Description not available."))

        
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

        
        st.write("## Stock Price Chart")
        interval = st.selectbox("Select Time Interval", ["1M", "3M", "6M", "YTD", "1Y", "3Y", "5Y", "Max"])

        
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

#==============================================================================
# Tab 4
#==============================================================================

def render_tab4():
    """
    This function renders the Monte Carlo simulation for stock price prediction
    with a detailed plot featuring distinct simulation lines and current stock price.
    """
    st.write("## Monte Carlo Simulation for Stock Price Prediction")
    
    # Inputs for the number of simulations and time horizon
    num_simulations = st.slider("Number of Simulations", 100, 2000, 500, step=100)
    time_horizon = st.slider("Time Horizon (Days)", 30, 365, 90, step=10)

    if ticker:
        stock_info = yf.Ticker(ticker)
        historical_data = stock_info.history(period="1y")  # Retrieve 1 year of data
        close_prices = historical_data['Close']

        if not close_prices.empty:
            # Calculate daily returns and standard deviation
            daily_returns = close_prices.pct_change().dropna()
            mu = daily_returns.mean()
            sigma = daily_returns.std()

            # Monte Carlo simulation
            last_price = close_prices[-1]
            simulation_results = []
            for _ in range(num_simulations):
                prices = [last_price]
                for _ in range(time_horizon):
                    next_price = prices[-1] * np.exp(
                        (mu - 0.5 * sigma**2) + sigma * np.random.normal()
                    )
                    prices.append(next_price)
                simulation_results.append(prices)

            # Convert simulation results to DataFrame
            simulation_df = pd.DataFrame(simulation_results).T

            # Plotting Monte Carlo simulations with Plotly
            st.write(f"### Simulation Results for {ticker}")
            fig = go.Figure()

            # Add simulation lines
            for i in range(simulation_df.shape[1]):
                fig.add_trace(go.Scatter(
                    x=simulation_df.index,
                    y=simulation_df[i],
                    mode='lines',
                    line=dict(width=0.7),
                    showlegend=False
                ))

            # Add a horizontal line for the current stock price
            fig.add_trace(go.Scatter(
                x=[0, time_horizon],
                y=[last_price, last_price],
                mode='lines',
                line=dict(color='red', dash='dash', width=1.5),
                name=f"Current Stock Price: ${last_price:.2f}"
            ))

            # Customize the layout
            fig.update_layout(
                title=f"Monte Carlo Simulation for {ticker} Stock Price - {time_horizon} Days",
                xaxis_title="Day",
                yaxis_title="Price (USD)",
                template='plotly_white',
                showlegend=True
            )

            # Display the chart
            st.plotly_chart(fig, use_container_width=True)

            # Value at Risk (VaR) calculation at 95% confidence level
            final_prices = simulation_df.iloc[-1, :]
            VaR_95 = np.percentile(final_prices, 5)
            expected_price = np.mean(final_prices)

            # Display calculated metrics
            st.write(f"### Monte Carlo Metrics")
            st.write(f"- **Value at Risk (95% confidence level):** ${VaR_95:.2f}")
            st.write(f"- **Expected Price:** ${expected_price:.2f}")
            st.write(
                f"- **Predicted Range (95% CI):** ${np.percentile(final_prices, 2.5):.2f} to ${np.percentile(final_prices, 97.5):.2f}"
            )
        else:
            st.error("Insufficient historical data to perform Monte Carlo simulation.")
    else:
        st.warning("Please select a valid ticker to proceed.")

#==============================================================================
# Tab 5
#==============================================================================

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
                data = stock_info.balance_sheet 
            else:
                data = stock_info.quarterly_balance_sheet  

        elif statement_type == "Cash Flow":
            if period_type == "Annual":
                data = stock_info.cashflow  
            else:
                data = stock_info.quarterly_cashflow 

        
        if not data.empty:
            st.write(f"### {statement_type} ({period_type})")
            st.dataframe(data, use_container_width=True)
        else:
            st.write(f"No {statement_type} data available for the selected period.")


#==============================================================================
# Tab 6
#==============================================================================    
    

# def render_tab6():
#     st.title("News")
#     if ticker:
#         stock_info = yf.Ticker(ticker)
        
        
#         if hasattr(stock_info, 'news') and stock_info.news:
#             articles = stock_info.news

            
#             for article in articles[:10]:  # Show up to 10 articles
#                 st.write(f"[{article['title']}]({article['link']})")
                
#                 st.write(article['publisher'])
                
#                 st.write("---")
#                 publish_time = datetime.fromtimestamp(article['providerPublishTime']).strftime('%Y-%m-%d %H:%M:%S')
#                 st.write(f"Published at: {publish_time}")
#         else:
#             st.write("No recent news articles found for this company.")

#==============================================================================
# Tab 6 - News with Company Logo
#==============================================================================    

def render_tab6():
    """
    Render the News tab with the company's logo and recent news articles.
    """
    st.title("News")

    if ticker:
        stock_info = yf.Ticker(ticker)
        info = stock_info.info

        # Display the company logo if available
        if "logo_url" in info and info["logo_url"]:
            st.image(info["logo_url"], width=150, caption=f"{info.get('shortName', ticker)} Logo")
        else:
            st.write("Company logo not available.")

        # Fetch and display news articles
        if hasattr(stock_info, 'news') and stock_info.news:
            st.write(f"### Latest News for {info.get('shortName', ticker)}")

            articles = stock_info.news
            for article in articles[:10]:  # Show up to 10 articles
                st.write(f"**[{article['title']}]({article['link']})**")
                st.write(f"*{article['publisher']}*")
                publish_time = datetime.fromtimestamp(article['providerPublishTime']).strftime('%Y-%m-%d %H:%M:%S')
                st.write(f"Published at: {publish_time}")
                st.write("---")
        else:
            st.write("No recent news articles found for this company.")


#==============================================================================
# Main body
#==============================================================================

# Render the header
render_sidebar()


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

    
