import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import plotly.graph_objects as go
import pickle
import os
import numpy as np
from scipy.stats import norm

all_tiers = ['challenger', 'master_plus', 'master_plus', 'master', 'diamond_plus', 'diamond', 'emerald_plus', 'master', 'platinum_plus', 'platinium', 'gold_plus', 'gold', 'silver_plus', 'silver', 'bronze_plus', 'bronze', 'iron_plus', 'iron']
all_roles = ['top', 'jungle', 'mid', 'adc', 'support']
all_patches = ['15.04']

def get_role_rank_patch_winrate(role, rank, patch):
    response = requests.get(f'https://www.op.gg/champions?position={role}&tier={rank}&patch={patch}')
    data = BeautifulSoup(response.text, 'html.parser').find('table')
    rows = data.find('tbody').find_all('tr', class_="")
    champions = []
    winrates = []
    pick_rates = []
    for row in rows:
        champions.append(row.find_all('td')[1].find('a').text.strip())
        winrates.append(float(row.find_all('td')[4].text.strip().replace('%', '')) / 100)
        pick_rates.append(float(row.find_all('td')[5].text.strip().replace('%', '')) / 100)
    return pd.DataFrame({'champion': champions, 'winrate': winrates, 'pick_rate': pick_rates})

st.title("OP.GG Stats Normal Distribution")
selected_tier = st.selectbox("Select Tier", options=all_tiers, index=9)
selected_patch = st.selectbox("Select Patch", options=all_patches, index=0)
refresh = st.button("Refresh Stats")
os.makedirs("data", exist_ok=True)
cache_file = "data/stats_cache.pkl"

if refresh:
    data_cache = {}
    for role in all_roles:
        key = (role, selected_tier, selected_patch)
        df = get_role_rank_patch_winrate(role, selected_tier, selected_patch)
        data_cache[key] = df
    with open(cache_file, "wb") as f:
        pickle.dump(data_cache, f)
else:
    if os.path.exists(cache_file):
        with open(cache_file, "rb") as f:
            data_cache = pickle.load(f)
    else:
        data_cache = {}

role_data = {}
for role in all_roles:
    key = (role, selected_tier, selected_patch)
    role_data[role] = data_cache.get(key, pd.DataFrame())

if all(df.empty for df in role_data.values()):
    st.write("No cached data available for the selected tier and patch. Please click Refresh Stats to load data.")
    st.stop()

fig = go.Figure()
x_range = np.linspace(0.4, 0.6, 1000)
for role in all_roles:
    if not role_data[role].empty:
        mean = role_data[role]['winrate'].mean()
        std = role_data[role]['winrate'].std()
        if std == 0:
            continue
        pdf = norm.pdf(x_range, loc=mean, scale=std)
        fig.add_trace(go.Scatter(x=x_range, y=pdf, mode='lines', name=role))
fig.update_layout(title="Normal Distribution of Winrate by Role", xaxis_title="Winrate", yaxis_title="Density", xaxis_range=[0.4, 0.6])
st.plotly_chart(fig, use_container_width=True)
