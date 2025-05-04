import pandas as pd
from ff3 import FF3Cipher
import hashlib
import ff3_test as ff3

KEY = "2DE79D232DF5585D68CE47882AE256D6"
tweak = "CBD09280979564"

# ====== 工具函數 in ff3_test ======

# ====== 主流程 ======
def process_csv(input_csv, output_csv):
    df = pd.read_csv(input_csv)
    key = "2DE79D232DF5585D68CE47882AE256D6"
    encrypted_ids = []
    decrypted_ids = []
    # ids = []
    plaintexts = []
    ciphertexts = []

    for idx, row in df.iterrows():
        original_id = row['ID']
        plaintext = ff3.id_to_numeric(original_id)
        tweak = ff3.generate_tweak(idx)
    
        cipher = FF3Cipher(key, tweak)
        encrypted_numeric = cipher.encrypt(plaintext) 
        encrypted_id = ff3.adject_value(plaintext,encrypted_numeric)
        if idx == 1 and encrypted_id == "A000000000" :
            # print(df.loc[idx, 'ID'])
            temp = df.loc[idx, 'ID']
            df.loc[idx, 'ID'] = df.loc[idx + 1, 'ID']
            df.loc[idx + 1, 'ID'] = temp


            # 重新加密目前 idx 的資料（交換後）
            original_id = df.loc[idx + 1 , 'ID']
            plaintext = ff3.id_to_numeric(original_id)
            tweak = ff3.generate_tweak(idx)
            cipher = FF3Cipher(key, tweak)
            encrypted_numeric = cipher.encrypt(plaintext)
            encrypted_id = ff3.adject_value(plaintext, encrypted_numeric)

        elif encrypted_id == "A000000000" and idx + 1 < len(df) and idx > 0:
            # print("123")
            # 對調 ID 欄位
            # print(df.loc[idx, 'ID'])
            temp = df.loc[idx, 'ID']
            df.loc[idx, 'ID'] = df.loc[idx - 1, 'ID']
            df.loc[idx - 1, 'ID'] = temp


            # 重新加密目前 idx 的資料（交換後）
            original_id = df.loc[idx - 1 , 'ID']
            plaintext = ff3.id_to_numeric(original_id)
            tweak = ff3.generate_tweak(idx)
            cipher = FF3Cipher(key, tweak)
            encrypted_numeric = cipher.encrypt(plaintext)
            encrypted_id = ff3.adject_value(plaintext, encrypted_numeric)

        
        decrypted_numeric = cipher.decrypt(encrypted_numeric)
        decrypted_id = ff3.decrypted_numeric_to_id(decrypted_numeric)

        # ids.append(original_id)
        plaintexts.append(plaintext)
        ciphertexts.append(encrypted_numeric)
        encrypted_ids.append(encrypted_id)
        decrypted_ids.append(decrypted_id)

    # df['original_id'] = ids
    df['plaintext'] = plaintexts
    df['ciphertext'] = ciphertexts
    df['Encrypted_ID'] = encrypted_ids
    df['Decrypted_ID'] = decrypted_ids
    df.to_csv(output_csv, index=False)
    print(f"加解密完成，結果寫入 {output_csv}")


if __name__ == "__main__":
    input_csv = "files/tw_id_list.csv"
    output_csv = "files/ff3_output.csv"
    process_csv(input_csv, output_csv)
    '''
    key = "2DE79D232DF5585D68CE47882AE256D6"
    tweak = "CBD09280979564"
    original_id = "U173044343"
    plaintext = ff3.id_to_numeric(original_id)
    tweak = tweak
    cipher = FF3Cipher(key, tweak)
    encrypted_numeric = cipher.encrypt(plaintext)
    encrypted_id = ff3.adject_value(plaintext, encrypted_numeric)

    print(f'plaintext: {plaintext}')
    print(f'en_numeric: {encrypted_numeric}')
    print(f'encrypted_id: {encrypted_id}')
    '''


    
