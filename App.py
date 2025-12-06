# app.py - Streamlit App
import streamlit as st
import pandas as pd
import json
import plotly.express as px

# Set page config
st.set_page_config(
    page_title="USD Exchange Rate Predictions",
    page_icon="💱",
    layout="wide"
)

# Title
st.title("💱 USD Exchange Rate Predictions")
st.markdown("### Next 7 Days Forecast")

# Load predictions
@st.cache_data
def load_predictions():
    # For local testing, you can load from local file
    # For production, load from cloud storage or GitHub
    try:
        df = pd.read_csv("usd_predictions.csv")
        return df
    except:
        # Sample data if file not found
        import datetime
        dates = [(datetime.date.today() + datetime.timedelta(days=i)).strftime('%Y-%m-%d') 
                for i in range(7)]
        rates = [83.5 + i*0.1 for i in range(7)]
        return pd.DataFrame({"day": dates, "usd_rate": rates})

# Load data
df = load_predictions()

# Display metrics
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Tomorrow's Rate", f"₹{df['usd_rate'].iloc[0]:.2f}")
with col2:
    st.metric("Weekly Avg", f"₹{df['usd_rate'].mean():.2f}")
with col3:
    change = ((df['usd_rate'].iloc[-1] - df['usd_rate'].iloc[0]) / df['usd_rate'].iloc[0]) * 100
    st.metric("Weekly Change", f"{change:+.1f}%")

# Chart
st.subheader("📈 Forecast Trend")
fig = px.line(
    df, 
    x="day", 
    y="usd_rate",
    markers=True,
    title="USD/INR Exchange Rate Forecast"
)
fig.update_layout(
    xaxis_title="Date",
    yaxis_title="Exchange Rate (INR)",
    hovermode="x unified"
)
st.plotly_chart(fig, use_container_width=True)

# Data table
st.subheader("📋 Detailed Predictions")
st.dataframe(
    df.style.format({"usd_rate": "₹{:.2f}"}),
    use_container_width=True
)

# Download buttons
st.subheader("📥 Download Predictions")
col1, col2, col3 = st.columns(3)

with col1:
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name="usd_predictions.csv",
        mime="text/csv"
    )

with col2:
    json_str = df.to_json(orient="records", indent=2)
    st.download_button(
        label="Download JSON",
        data=json_str,
        file_name="usd_predictions.json",
        mime="application/json"
    )

# Sidebar info
with st.sidebar:
    st.header("ℹ️ About")
    st.info("""
    This app shows USD/INR exchange rate 
    predictions for the next 7 days.
    
    Predictions are generated using 
    Linear Regression on historical data.
    """)
    
    st.header("🔄 Update Frequency")
    st.write("Daily updates at 10:00 AM IST")
    
    st.header("📊 Model Info")
    st.write("Algorithm: Linear Regression")
    st.write("Features: Time-series analysis")
    st.write("Training: Daily historical rates")
