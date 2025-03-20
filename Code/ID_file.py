import ID_generator as id_gen
import pandas as pd

def read_population_data(csv_path):
    """讀取縣市人口數據，計算比例"""
    df = pd.read_csv(csv_path)
    total_population = df.iloc[:, 1:].sum().sum()  # 計算所有人口總數
    df["比例"] = df.iloc[:, 1:].sum(axis=1) / total_population  # 計算每個縣市人口占比
    return df

def generate_id_by_ratio(df, total_ids=1000):
    """根據縣市人口比例生成對應數量的身分證字號"""
    all_ids = []
    for _, row in df.iterrows():
        letter = row[0]  # 縣市的英文字母
        count = int(row["比例"] * total_ids)  # 根據比例計算生成數量
        #先隨機產生身分證，再根據比例替換英文字母
        all_ids.extend([id_gen.generate_taiwan_id().replace(id_gen.generate_taiwan_id()[0], letter, 1) for _ in range(count)])
    return all_ids

# 讀取人口數據
population_csv = ""  # CSV 路徑(人口)
df_population = read_population_data(population_csv)

# 生成對應比例的身分證字號
id_list = generate_id_by_ratio(df_population, total_ids=700)

# 建立 DataFrame
df = pd.DataFrame({"ID": id_list})

# 打亂數據
shuffle_df = df.sample(frac=1).reset_index(drop=True)

# 存成 CSV 檔案
shuffle_df.to_csv("id_list.csv", index=False, encoding="utf-8")

# 生成 EXCEL 檔案
excel_file = "id_list.xlsx"
with pd.ExcelWriter(excel_file, engine="xlsxwriter") as writer:
    shuffle_df.to_excel(writer, index=False, sheet_name="ID")

print(" CSV 檔案已生成：id_list.csv")
print(" EXCEL 檔案已生成：id_list.xlsx")
