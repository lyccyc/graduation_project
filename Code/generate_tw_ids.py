import ID_generator as id_gen
import pandas as pd

tw_ids = []
for _ in range(1000):
    tw_ids.append(id_gen.generate_taiwan_id())

df = pd.DataFrame({"ID": tw_ids})
df.to_csv("tw_id_list.csv", index=False, encoding="utf-8")

excel_file = "tw_id_list.xlsx"
with pd.ExcelWriter(excel_file, engine="xlsxwriter") as writer:
    df.to_excel(writer, index=False, sheet_name="ID")

print(" CSV 檔案已生成：tw_id_list.csv")
print(" EXCEL 檔案已生成：tw_id_list.xlsx")
