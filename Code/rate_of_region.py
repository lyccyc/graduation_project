import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# 一個函式讀取數字成二維陣列，另一個根據陣列繪圖

#%%
'''讀取 CSV 檔案，轉換成二維陣列'''
def population(path):
    df = pd.read_csv(path)
    return df.values.tolist()

#%%
'''可能有問題'''
# 提取縣市名稱與總人口數
def extract_population_info(data):
    cities = [row[0] for row in data]  # 縣市代碼
    populations = [row[1] + row[2] for row in data]  # 男性 + 女性總人口
    return cities, populations

#%%
'''繪製人口圓餅圖'''
def plot_population_pie_chart(cities, populations):
    plt.figure(figsize=(8, 8))
    plt.pie(populations, labels=cities, autopct="%1.1f%%", startangle=140, wedgeprops={'edgecolor': 'black'})
    plt.title("各縣市總人口比例")
    plt.show()