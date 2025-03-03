import os
import pickle
import pandas as pd
from tqdm import tqdm
import requests
from bs4 import BeautifulSoup

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

def scrape_all_data():
    data_cache = {}
    for tier in tqdm(all_tiers):
        for patch in all_patches:
            for role in all_roles:
                key = (role, tier, patch)
                df = get_role_rank_patch_winrate(role, tier, patch)
                data_cache[key] = df
    folder = 'data'
    if not os.path.exists(folder):
        os.makedirs(folder)
    with open(os.path.join(folder, 'stats_cache.pkl'), 'wb') as f:
        pickle.dump(data_cache, f)

if __name__ == '__main__':
    scrape_all_data()
