import pandas as pd
from ff3 import FF3Cipher
import ff3_lib_v2 as ff3

key = "2DE79D232DF5585D68CE47882AE256D6"

def FF3(input_csv, output_csv):
    df = pd.read_csv(input_csv)

    for idx in df.index:
        df.loc[idx, 'Numeric'] = ff3.IDN_to_number(df.loc[idx, 'ID'])

    for idx in df.index:
        plaintext = df.loc[idx, 'Numeric']
        is_local = int(plaintext[:2]) < 50
        encrypted, status = ff3.encrypt_with_mod(plaintext, idx, is_local)

        df.loc[idx, 'Encrypted_Numeric']= encrypted
        df.loc[idx, 'Status'] = status
        
        if status != "FAILED":
            df.loc[idx, 'Status'] = status
            df.loc[idx, 'Swap_Log'] = f"No Swap"

    print(df)
    """
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
        status = df.loc[idx, 'Status']

        if status == "OK":
            decrypt = cipher.decrypt(enc_num)
            df.loc[idx, 'Decrypted_Numeric'] = decrypt
            decrypt_ID = ff3.decrypt_to_ID(decrypt)
            df.loc[idx, 'Decrypted_ID'] = decrypt_ID
        if status == "FIXED_50":
            decrypt = cipher.decrypt(enc_num)
            df.loc[idx, 'Decrypted_Numeric'] = decrypt
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

"""
if __name__ == "__main__":
    input_csv = "files/all_id_list.csv"
    output_csv = "files/ff3_encrypted_all_output_v2.csv"
    FF3(input_csv, output_csv)