# streamlit_app.py

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import pymysql

# Initialize connection.
# Uses st.cache to only run once.
@st.cache(allow_output_mutation=True, hash_funcs={"_thread.RLock": lambda _: None})

def init_connection():
    return pymysql.connect(**st.secrets["singlestore"])

conn = init_connection()

symbol = st.sidebar.text_input("Symbol", value = "AAPL", max_chars = None, key = None, type = "default")
num_days = st.sidebar.slider("Number of days", 2, 30, 5)

# Perform query.

data = pd.read_sql("""
SELECT TIME_BUCKET(%s) AS day,
    symbol,
    MIN(price) AS low,
    MAX(price) AS high,
    FIRST(price) AS open,
    LAST(price) AS close
FROM tick
WHERE symbol = %s
GROUP BY 2, 1
ORDER BY 2, 1;
""", conn, params = (str(num_days) + "d", symbol.upper()))

st.subheader(symbol.upper())

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

st.write(data)
