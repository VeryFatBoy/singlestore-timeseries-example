# streamlit_app.py

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sqlalchemy

# Initialise connection
conn = st.connection("singlestore", type = "sql")

symbol = st.sidebar.text_input("Symbol", value = "AAPL", max_chars = None)
num_days = st.sidebar.slider("Number of days", 2, 30, 5)

symbol = symbol.upper()
num_days_str = f'"{num_days}d"'

stmt = f"""
SELECT TIME_BUCKET({num_days_str}) AS day,
       symbol,
       MIN(price) AS low,
       MAX(price) AS high,
       FIRST(price) AS open,
       LAST(price) AS close
FROM tick
WHERE symbol = :symbol
GROUP BY symbol, day
ORDER BY symbol, day;
"""

data = conn.query(stmt, params = {"symbol": symbol})

# Check if data was returned
if not data.empty:
    st.subheader(symbol)

    # Plot the candlestick chart using Plotly
    fig = go.Figure(data = [go.Candlestick(
        x = data["day"],
        open = data["open"],
        high = data["high"],
        low = data["low"],
        close = data["close"],
        name = symbol,
    )])

    fig.update_xaxes(type = "category")
    fig.update_layout(height = 700)

    st.plotly_chart(fig, use_container_width = True)
else:
    st.write("No data found for the symbol.")

st.write(data)
