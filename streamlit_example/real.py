import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from datetime import datetime, timedelta
import yfinance as yf
import streamlit as st
from plotly.subplots import make_subplots


st.title('Financial Dashboard')
st.sidebar.title("Navigation")
page = st.sidebar.button("Summary", "Chart", "Financials","Monte Carlo Simulation")


if page == "Summary":
    st.title("Summary")
    
    # Add more content here

# Data Analysis Page
elif page == "Financials":
    st.title("Financials")
    
    # Add your data analysis code here

# Visualization Page
elif page == "Chart":
    st.title("Chart")
    st.write("Chart")
    # Add your visualization code here