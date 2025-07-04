import streamlit as st
import feedparser
from datetime import datetime
import requests
import plotly.graph_objects as go

st.set_page_config(
    page_title="Bitcoin News + Sentiment",
    layout="centered",
    menu_items={
        'Get Help': None,
        'Report a Bug': None,
        'About': None
    }
)
# --- Set up app ---
st.set_page_config(page_title="Bitcoin News + Sentiment", layout="centered")
st.title("📰 Bitcoin News via RSS (CoinDesk)")

# --- Fetch and display Crypto Fear & Greed Index (from Alternative.me API) ---
try:
    response = requests.get("https://api.alternative.me/fng/")
    data = response.json()
    value = int(data["data"][0]["value"])
    label = data["data"][0]["value_classification"]
    st.metric(label="📈 Crypto Fear & Greed Index", value=value, delta=label)
except Exception as e:
    st.error(f"Could not fetch Fear & Greed Index: {e}")
    value = 0
    label = "N/A"

st.markdown("---")

# --- Gauge Color ---
if value < 25:
    gauge_color = "red"
elif value < 50:
    gauge_color = "orange"
elif value < 75:
    gauge_color = "yellow"
else:
    gauge_color = "green"

# --- Gauge Chart ---
fig = go.Figure(go.Indicator(
    mode="gauge+number",
    value=value,
    title={'text': "Fear & Greed Index"},
    gauge={
        'axis': {'range': [0, 100]},
        'bar': {'color': gauge_color},
    }
))
st.plotly_chart(fig)

# --- Parse RSS feed from CoinDesk ---
RSS_URL = "https://www.coindesk.com/arc/outboundfeeds/rss/"
feed = feedparser.parse(requests.get(RSS_URL, headers={"User-Agent": "Mozilla/5.0"}).content)
entries = feed.entries[:100]

# --- Filter for Bitcoin News ---
bitcoin_entries = [
    post for post in entries
    if "bitcoin" in post.get("title", "").lower()
    or "bitcoin" in post.get("summary", "").lower()
]

# --- Display News ---
if not bitcoin_entries:
    st.warning("No Bitcoin news found.")
else:
    for post in bitcoin_entries:
        title, link = post.title, post.link
        ts = post.get("published_parsed")
        date_str = datetime(*ts[:6]).strftime("%b %d, %Y %H:%M") if ts else "Unknown"

        image = None
        if post.get("media_thumbnail"):
            image = post.media_thumbnail[0]["url"]
        elif post.get("media_content"):
            image = post.media_content[0]["url"]
        elif post.get("links"):
            for link_obj in post.links:
                if link_obj.get("rel") == "enclosure" and link_obj.get("type", "").startswith("image"):
                    image = link_obj["href"]
                    break

        if image and image.startswith("http"):
            st.image(image, use_container_width=True)
        st.markdown(f"### [{title}]({link})")
        st.caption(f"🕒 {date_str}")
        st.markdown("---")
