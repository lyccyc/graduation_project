import ID_generator as id_gen
import pandas as pd

ids = []
for _ in range(1000):
    ids.append(id_gen.generate_id())

df = pd.DataFrame({"ID": ids})
df.to_csv("all_id_list_v2_uneven.csv", index=False, encoding="utf-8")

excel_file = "all_id_list_v2_uneven.xlsx"
with pd.ExcelWriter(excel_file, engine="xlsxwriter") as writer:
    df.to_excel(writer, index=False, sheet_name="ID")

print(" CSV 檔案已生成：/files/all_id_list_uneven.csv")
print(" EXCEL 檔案已生成：/files/all_id_lis_uneven.xlsx")
