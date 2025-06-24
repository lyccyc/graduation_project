import pandas as pd
from ff3 import FF3Cipher
import ff3_lib_v2 as ff3

key = "2DE79D232DF5585D68CE47882AE256D6"

def FF3(input_csv, output_csv):
    df = pd.read_csv(input_csv)

    # 初始化 DataFrame 的新欄位
    df['Numeric'] = ''
    df['plaintext'] = ''
    df['original_plaintext'] = ''
    df['Encrypted_Numeric'] = ''
    df['Encrypted_ID'] = ''
    df['Status'] = ''
    df['Swap_Index'] = -1 # 初始化為 -1
    df['Plus50'] = False # 這個欄位在你的流程中似乎沒有明確使用，可以移除或確認用途
    df['Decrypted_Numeric'] = ''
    df['Decrypted_ID'] = ''


    for idx in df.index:
        df.loc[idx, 'Numeric'] = ff3.IDN_to_number(df.loc[idx, 'ID'])
        df.loc[idx, 'plaintext'] = df.loc[idx, 'Numeric'][:9]
        df.loc[idx, 'original_plaintext'] = df.loc[idx, 'Numeric'][:9] # 儲存原始明文，以防交換後還原

    # print("初始化後的 DataFrame:\n", df.head()) # 檢查初始化狀態

    # 加密階段
    for idx in df.index:
        # 如果該筆資料已經被其他交換操作處理過 (例如，它被交換到當前位置，或者它的狀態已經是 SWAPPED/FAILED)
        # 則跳過，避免重複處理或處理不該處理的資料。
        # 這裡需要一個策略來避免無限循環或重複處理。
        # 一個簡單的方法是檢查 Status 欄位。
        if df.loc[idx, 'Status'] in ["OK", "FIXED_50", "SWAPPED", "FAILED"]:
            continue # 如果已經處理過，跳過

        current_plaintext = df.loc[idx, 'plaintext'] # 獲取當前位置的明文（可能是原始的，也可能是交換上來的）
        is_local = int(current_plaintext[:2]) < 50
        
        plaintext_processed, encrypted, status = ff3.encrypt_with_mod(current_plaintext, idx, is_local)

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
            df.loc[idx, 'plaintext'] = plaintext_processed # 更新為處理後的明文（可能是 +/-50 修正後的）
            df.loc[idx, 'Encrypted_Numeric'] = encrypted
            df.loc[idx, 'Status'] = status

    df.to_csv(tmp_output, index=False)
    print(f"加密完成，結果寫入 {tmp_output}")

    # ===== 解密階段 =====
    for idx in df.index:
        status = df.loc[idx, 'Status']
        enc_num = df.loc[idx, 'Encrypted_Numeric']

        if status in ["OK", "FIXED_50", "SWAPPED"]: # 只有成功加密的才進行解密
            tweak = ff3.generate_tweak(idx) # Tweak 應該和加密時的 idx 一致
            cipher = FF3Cipher(key, tweak)

            decrypt = None
            try:
                decrypt = cipher.decrypt(enc_num)
            except Exception as e:
                print(f"[解密錯誤] idx={idx}, Encrypted_Numeric={enc_num}, 錯誤: {e}")
                df.loc[idx, 'Decrypted_Numeric'] = "ERROR"
                df.loc[idx, 'Decrypted_ID'] = "ERROR"
                continue # 跳過此條，處理下一條

            df.loc[idx, 'Decrypted_Numeric'] = decrypt

            # 處理 FIXED_50 情況下的解密前綴還原
            if status == "FIXED_50":
                original_plaintext_prefix = int(df.loc[idx, 'original_plaintext'][:2])
                decrypted_prefix = int(decrypt[:2])
                
                # 判斷原始明文是否為本地 (因為 FIXED_50 修正邏輯是根據原始明文判斷)
                is_original_local = original_plaintext_prefix < 50

                if is_original_local: # 原始是本地，加密時加了50，解密時要減回50
                    prefix = decrypted_prefix - 50
                else: # 原始是外來，加密時減了50，解密時要加回50
                    prefix = decrypted_prefix + 50
                
                # 重新組合解密後的數字
                decrypt_num = str(prefix).zfill(2) + decrypt[2:]
            else: # OK 或 SWAPPED 的情況，直接使用解密結果
                decrypt_num = decrypt
            
            # 將解密後的數字轉換回身分證 ID
            decrypt_ID = ff3.decrypt_to_ID(decrypt_num)
            df.loc[idx, 'Decrypted_ID'] = decrypt_ID
        else: # FAILED 的資料不進行解密
            df.loc[idx, 'Decrypted_Numeric'] = "N/A"
            df.loc[idx, 'Decrypted_ID'] = "N/A"

    # ===== 儲存結果 =====
    df.to_csv(output_csv, index=False)
    print(f"加解密完成，結果寫入 {output_csv}")

if __name__ == "__main__":
    input_csv = "files/all_id_list.csv"
    output_csv = "files/ff3_encrypted_all_output_v2.csv"
    tmp_output = "files/tmp_output_v2.csv"
    FF3(input_csv, output_csv)