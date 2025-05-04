import pandas as pd
from ff3 import FF3Cipher
import ff3_test as ff3  # 需包含 id_to_numeric, adject_value, decrypted_numeric_to_id 等方法

KEY = "2DE79D232DF5585D68CE47882AE256D6"

def process_csv(input_csv, output_csv):
    df = pd.read_csv(input_csv)
    results = []

    for idx in range(len(df)):
        original_id = df.at[idx, 'ID']
        plaintext = ff3.id_to_numeric(original_id)
        tweak = ff3.generate_tweak(idx)
        cipher = FF3Cipher(KEY, tweak)
        encrypted_numeric = cipher.encrypt(plaintext)
        encrypted_id = ff3.adject_value(plaintext, encrypted_numeric)

        # 如果出現不合法加密值，與前一筆對調
        if encrypted_id == "A000000000" and idx > 0:
            # 對調 df 的 ID 欄位
            df.at[idx, 'ID'], df.at[idx - 1, 'ID'] = df.at[idx - 1, 'ID'], df.at[idx, 'ID']

            # 重新處理這筆（對調後的新資料）
            original_id = df.at[idx, 'ID']
            plaintext = ff3.id_to_numeric(original_id)
            tweak = ff3.generate_tweak(idx)
            cipher = FF3Cipher(KEY, tweak)
            encrypted_numeric = cipher.encrypt(plaintext)
            encrypted_id = ff3.adject_value(plaintext, encrypted_numeric)

        # 解密
        decrypted_numeric = cipher.decrypt(encrypted_numeric)
        decrypted_id = ff3.decrypted_numeric_to_id(decrypted_numeric)

        # 加入結果
        results.append({
            'Original_ID': original_id,
            'Plaintext': plaintext,
            'Encrypted_Numeric': encrypted_numeric,
            'Encrypted_ID': encrypted_id,
            'Decrypted_ID': decrypted_id
        })

    # 輸出結果
    output_df = pd.DataFrame(results)
    output_df.to_csv(output_csv, index=False)
    print(f"✅ 加解密完成，結果寫入 {output_csv}")

# ===== 主程式入口 =====
if __name__ == "__main__":
    input_csv = "files/tw_id_list.csv"
    output_csv = "files/ff3_output.csv"
    process_csv(input_csv, output_csv)
