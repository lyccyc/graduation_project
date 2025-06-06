# === ff3_id_test_v2.py (整合新版) ===

import pandas as pd
from ff3 import FF3Cipher
import ff3_test as ff3

KEY = "2DE79D232DF5585D68CE47882AE256D6"

def process_csv(input_csv, output_csv):
    df = pd.read_csv(input_csv)
    results = []
    idx = 0

    while idx < len(df):
        result = ff3.encrypt_with_fallback_and_swap(df, idx, KEY)

        if isinstance(result, list):
            results.extend(result)
            idx += 2  # 處理了兩筆資料
        else:
            results.append(result)
            idx += 1

    # 補上解密欄位
    for r in results:
        if r['Encrypted_ID'] != "A000000000":
            # 需要用正確的 tweak 來解密
            i = results.index(r)
            tweak = ff3.generate_tweak(i)
            cipher = FF3Cipher(KEY, tweak)
            try:
                decrypted = cipher.decrypt(r['Encrypted_Numeric'])
            except:
                fallback_tweak = ff3.generate_fallback_tweak(i)
                cipher = FF3Cipher(KEY, fallback_tweak)
                decrypted = cipher.decrypt(r['Encrypted_Numeric'])
            r['Decrypted_ID'] = ff3.decrypted_numeric_to_id(decrypted)
        else:
            r['Decrypted_ID'] = ""

    output_df = pd.DataFrame(results)
    output_df.to_csv(output_csv, index=False)
    print(f"加解密完成，結果寫入 {output_csv}")

if __name__ == "__main__":
    input_csv = "files/tw_id_list.csv"
    output_csv = "files/ff3_v2_output.csv"
    process_csv(input_csv, output_csv)
