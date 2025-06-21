import pandas as pd
from ff3 import FF3Cipher
import ff3_lib_v2 as ff3

key = "2DE79D232DF5585D68CE47882AE256D6"

def FF3(input_csv, output_csv):
    df = pd.read_csv(input_csv)
    df['Numeric'] = ""
    df['Encrypted_Numeric'] = ""
    df['Encrypted_ID'] = ""
    df['Status'] = ""
    df['Swap_Index'] = -1
    df['Plus50'] = False
    df['decrypt_Numeric'] = ""
    df['decrypt_ID'] = ""
    for idx in df.index:
        numeric = ff3.IDN_to_number(df.loc[idx,'ID'])
        df.loc[idx, 'Numeric'] = numeric
    for idx in df.index:
        numeric = df.loc[idx, 'Numeric']
        tweak = ff3.generate_tweak(idx)
        cipher = FF3Cipher(key, tweak)
        plaintext = numeric
        encrypted = cipher.encrypt(plaintext)
        is_local = int(plaintext[:2]) < 50

        if(is_local and int(encrypted[:2]) < 50) or (not is_local and int(encrypted[:2]) >= 50):
            df.loc[idx, 'Encrypted_Numeric'] = encrypted
            df.loc[idx, 'Encrypted_ID'] = ff3.number_to_IDN(encrypted)
            df.loc[idx, 'Status'] = "OK"
            continue

        modified_prefix = int(plaintext[:2]) + (50 if is_local else -50)
        modified_plain = str(modified_prefix).zfill(2) + plaintext[2:]

        df.loc[idx, 'Plus50'] = True
        encrypted2 = cipher.encrypt(modified_plain)

        if (is_local and int(encrypted2[:2]) < 50) or (not is_local and int(encrypted2[:2]) >= 50):
            # 重算成功
            df.loc[idx, 'Encrypted_Numeric'] = encrypted2
            df.loc[idx, 'Encrypted_ID'] = ff3.number_to_IDN(encrypted2)
            df.loc[idx, 'Status'] = "FIXED_50"
            continue

            # 無法成功 → 對調處理
        swap_success = False
        for j in range(idx + 1, len(df)):
            # 先處理 index j 的資料（被調上來者）
            plaintext_j = df.loc[j, 'Numeric']
            tweak_j = ff3.generate_tweak(idx)  # 被調上來處理的資料，對應 idx 的 tweak
            cipher_j = FF3Cipher(key, tweak_j)
            encrypted_j = cipher_j.encrypt(plaintext_j)

            is_local_j = int(plaintext_j[:2]) < 50
            if (is_local_j and int(encrypted_j[:2]) < 50) or (not is_local_j and int(encrypted_j[:2]) >= 50):
                df.loc[idx, 'Encrypted_Numeric'] = encrypted_j
                df.loc[idx, 'Encrypted_ID'] = ff3.number_to_IDN(encrypted_j)
                df.loc[idx, 'Status'] = "SWAPPED"
                df.loc[idx, 'Swap_Index'] = j

                # 下一輪從 index j 繼續處理原本那筆資料
                df.loc[j+1, 'Numeric'] = plaintext  # 把 idx 的原資料往下移
                break

        if not swap_success:
            df.loc[idx, 'Encrypted_Numeric'] = "XXXXXXXXXX"
            df.loc[idx, 'Encrypted_ID'] = "A000000000"
            df.loc[idx, 'Status'] = "FAILED"

        # print(df)
        
#===== 解密 =====
    for idx in df.index:
        tweak = ff3.generate_tweak(idx)
        cipher = FF3Cipher(key, tweak)
        enc_num = df.loc[idx, 'Encrypted_Numeric']
        

        if enc_num == "XXXXXXXXXX":
            continue

        if "status" == "OK":
            decrypt = cipher.decrypt(enc_num)
            df.loc[idx, 'Decrypt_Numeric'] = decrypt
            decrypt_ID = ff3.decrypt_to_ID(decrypt)
            df.loc[idx, 'Decrypted_ID'] = decrypt_ID
        if "status" == "FIXED_50":
            decrypt = cipher.decrypt(enc_num)
            df.loc[idx, 'Decrypt_Numeric'] = decrypt
            if is_local:
                prefix = int(decrypt[:2]) - 50 
            else:
                prefix = int(decrypt[:2]) + 50 
            decrypt_num = str(prefix) + decrypt[2:]
            decrypt_ID = ff3.decrypt_to_ID(decrypt_num)
            df.loc[idx, 'Decrypted_ID'] = decrypt_ID
        
# ===== 儲存結果 =====
    df.to_csv(output_csv, index=False)
    print(f"加解密完成，結果寫入 {output_csv}")

if __name__ == "__main__":
    input_csv = "files/all_id_list.csv"
    output_csv = "files/ff3_encrypted_all_output.csv"
    FF3(input_csv, output_csv)