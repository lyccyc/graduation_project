import pandas as pd
from ff3 import FF3Cipher
import ff3_lib_v2 as ff3

key = "2DE79D232DF5585D68CE47882AE256D6"

def FF3(input_csv, output_csv):
    df = pd.read_csv(input_csv)

    df['Numeric'] = ''
    df['original_plaintext'] = ''
    df['plaintext'] = ''
    df['Encrypted_Numeric'] = ''
    df['Encrypted_ID'] = ''
    df['Decrypted_Numeric'] = ''
    df['Decrypted_ID'] = ''
    df['Status'] = ''
    df['plus50'] = False
    df['Swap_Index'] = -1 # 初始化為 -1

    for idx in df.index:
        df.loc[idx, 'Numeric'] = ff3.IDN_to_number(df.loc[idx, 'ID'])
        df.loc[idx, 'plaintext'] = df.loc[idx, 'Numeric'][:9]
        df.loc[idx, 'original_plaintext'] = df.loc[idx, 'Numeric'][:9]
    
    #===== 加密 =====
    for idx in df.index:
        if df.loc[idx, 'Status'] in ["OK", "FIXED_50", "SWAPPED", "FAILED"]:
            continue # 如果已經處理過，跳過

        plaintext =  df.loc[idx, 'plaintext']
        is_local = int(plaintext[:2]) < 50
        plaintext, encrypted, status, plus50 = ff3.encrypt_with_mod(plaintext, idx, is_local)

        if status == "FAILED":
            # 如果 encrypt_with_mod 失敗，則嘗試交換
            # encrypt_with_swap 會直接修改 df.loc[idx] 的狀態和內容
            swap_successful = ff3.encrypt_with_swap(df, idx)
            # encrypt_with_swap 已經處理了 df.loc[idx] 的更新，包括狀態和加密結果
            # 所以這裡不需要額外的 df.loc[idx] 賦值
            if not swap_successful:
                # 如果交換也失敗了，那麼 df.loc[idx] 應該已經被標記為 FAILED
                pass # 什麼都不做，因為 encrypt_with_swap 已經處理了失敗情況
        else:
            # 如果 encrypt_with_mod 成功，則直接更新 df
            df.loc[idx, 'plaintext'] = plaintext # 更新為處理後的明文（可能是 +/-50 修正後的）
            df.loc[idx, 'Encrypted_Numeric'] = encrypted
            df.loc[idx, 'Status'] = status
            df.loc[idx, 'plus50'] = plus50

        #===== 轉換為加密身分證 =====
        enc_id = ff3.number_to_IDN(df.loc[idx, 'Encrypted_Numeric'])
        df.loc[idx, 'Encrypted_ID'] = enc_id

    #===== 解密 =====
    for idx in df.index:
        tweak = ff3.generate_tweak(idx)
        cipher = FF3Cipher(key, tweak)
        enc_num = df.loc[idx, 'Encrypted_Numeric']
        status = df.loc[idx, 'Status']
        plus50 = df.loc[idx, 'plus50']

        if status in ["FAILED", ""]:
            df.loc[idx, 'Decrypted_Numeric'] = "N/A"
            df.loc[idx, 'Decrypted_ID'] = "N/A"
            continue

        decrypted = cipher.decrypt(enc_num)
        df.loc[idx, 'Decrypted_Numeric'] = decrypted

        if status == "FIXED_50" or ((status == "SWAPPED") and plus50):
            is_local = int(df.loc[idx, 'original_plaintext'][:2]) < 50
            prefix = int(decrypted[:2]) - 50 if is_local else int(decrypted[:2]) + 50
            corrected = str(prefix).zfill(2) + decrypted[2:]
            decrypted_id = ff3.number_to_IDN(corrected)
        else:
            decrypted_id = ff3.number_to_IDN(decrypted)
            
        df.loc[idx, 'Decrypted_ID'] = decrypted_id

# ===== 儲存結果 =====
    df.to_csv(output_csv, index=False)
    print(f"加解密完成，結果寫入 {output_csv}")

if __name__ == "__main__":
    input_csv = "files/all_id_list_v2_uneven.csv"
    output_csv = "files/ff3_encrypted_all_output_uneven.csv"
    # tmp_output = "files/tmp_output_v2.csv"
    FF3(input_csv, output_csv)