import ID_generator as id_gen
import pandas as pd

ids = []
for _ in range(12):
    ids.append(id_gen.generate_id())

df = pd.DataFrame({"ID": ids})
df.to_csv("12_test_ids.csv", index=False, encoding="utf-8")

excel_file = "12_test_ids.xlsx"
with pd.ExcelWriter(excel_file, engine="xlsxwriter") as writer:
    df.to_excel(writer, index=False, sheet_name="ID")

print(" CSV 檔案已生成：files/id_files/12_test_ids.csv")
print(" EXCEL 檔案已生成：files/id_files/12_test_ids.xlsx")
