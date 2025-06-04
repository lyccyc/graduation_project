import pandas as pd
from ff3 import FF3Cipher
import ff3_test as ff3  # 需包含 id_to_numeric, adject_value, decrypted_numeric_to_id 等方法

KEY = "2DE79D232DF5585D68CE47882AE256D6"

def process_row(df, idx, key):
    original_id = df.at[idx, 'ID']
    plaintext = ff3.id_to_numeric(original_id)
    tweak = ff3.generate_tweak(idx)
    cipher = FF3Cipher(key, tweak)
    encrypted_numeric = cipher.encrypt(plaintext)
    encrypted_id = ff3.adject_value(plaintext, encrypted_numeric, cipher)
    decrypted_numeric = cipher.decrypt(encrypted_numeric)
    decrypted_id = ff3.decrypted_numeric_to_id(decrypted_numeric)
    return {
        'Original_ID': original_id,
        'Plaintext': plaintext,
        'Encrypted_Numeric': encrypted_numeric,
        'Encrypted_ID': encrypted_id,
        'Decrypted_ID': decrypted_id
    }

def process_csv(input_csv, output_csv):
    df = pd.read_csv(input_csv)
    results = []
    idx = 0

    while idx < len(df):
        result = process_row(df, idx, KEY)

        if result['Encrypted_ID'] == "A000000000" and idx > 0:
            # 對調前一筆與當前筆
            df.at[idx, 'ID'], df.at[idx - 1, 'ID'] = df.at[idx - 1, 'ID'], df.at[idx, 'ID']

            # 重新處理對調後的兩筆
            result_prev = process_row(df, idx - 1, KEY)
            result = process_row(df, idx, KEY)

            results[-1] = result_prev  # 覆蓋上一筆
        else:
            results.append(result)

        idx += 1

    output_df = pd.DataFrame(results)
    output_df.to_csv(output_csv, index=False)
    print(f"✅ 加解密完成，結果寫入 {output_csv}")

if __name__ == "__main__":
    input_csv = "files/tw_id_list.csv"
    output_csv = "files/ff3_v2_output.csv"
    process_csv(input_csv, output_csv)