"""
測試性別碼分布用
"""

import pandas as pd

# df = pd.read_csv("files/ff3_files/ff3_encrypted_output_ave.csv")
# df = pd.read_csv("files/ff3_files/ff3_encrypted_output_uneven.csv")
# df = pd.read_csv("files/ff3_files/ff3_encrypted_all_output_ave.csv")
df = pd.read_csv("files/ff3_files/ff3_encrypted_all_output_uneven.csv")

df['Encrypted_Gender_Code'] = df['Encrypted_ID'].astype(str).str[1]
encrypted_gender_counts = df['Encrypted_Gender_Code'].value_counts().sort_index()
encrypted_gender_dist = encrypted_gender_counts.to_frame(name='Encrypted_Count')
encrypted_gender_dist['Encrypted_Percentage'] = (encrypted_gender_dist['Encrypted_Count'] / len(df) * 100).round(2)

print(encrypted_gender_dist)