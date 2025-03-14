import ID_generator as id_gen
import pandas as pd

data_tw = {"ID": [id_gen.generate_taiwan_id() for _ in range(700)]}
data_for = {"ID": [id_gen.generate_foreigner_id() for _ in range(300)]}

# 建立 DataFrame
df1 = pd.DataFrame(data_tw)
df2 = pd.DataFrame(data_for)

df = pd.concat([df1,df2])
shuffle_df = df.sample(frac=1).reset_index(drop=True)

# 存成 CSV 檔案
shuffle_df.to_csv("id_list.csv", index=False, encoding="utf-8")

#生成 EXCEL 檔案
excel_file = "id_list.xlsx"
with pd.ExcelWriter(excel_file, engine="xlsxwriter") as writer:
    shuffle_df.to_excel(writer, index=False, sheet_name="ID")


print("✅ CSV 檔案已生成：id_list.csv")
print("✅ EXCEL 檔案已生成：id_list.excel")
