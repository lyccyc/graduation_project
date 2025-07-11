import pandas as pd
from ff3 import FF3Cipher
import ff3_lib as ff3

key = "2DE79D232DF5585D68CE47882AE256D6"

def FF3(input_csv, output_csv):
    df = pd.read_csv(input_csv)

    df['Numeric'] = ''
    df['plaintext'] = ''
    df['Encrypted_Numeric'] = ''
    df['Encrypted_ID'] = ''
    df['Decrypted_Numeric'] = ''
    df['Decrypted_ID'] = ''

    for idx in df.index:
        df.loc[idx, 'Numeric'] = ff3.IDN_to_number(df.loc[idx, 'ID'])
        df.loc[idx, 'plaintext'] = df.loc[idx, 'Numeric'][:9]
    
    #===== 加密 =====
    for idx in df.index:
        plaintext =  df.loc[idx, 'plaintext']
        encrypted = ff3.encrypt_fun(plaintext,idx)
        enc_id = ff3.number_to_IDN(encrypted)
        df.loc[idx, 'Encrypted_Numeric'] = encrypted
        df.loc[idx, 'Encrypted_ID'] = enc_id

    #===== 解密 =====
    for idx in df.index:
        tweak = ff3.generate_tweak(idx)
        cipher = FF3Cipher(key, tweak)
        enc_num = df.loc[idx, 'Encrypted_Numeric']

        decrypted = cipher.decrypt(enc_num)
        decrypted_id = ff3.number_to_IDN(decrypted)

        df.loc[idx, 'Decrypted_Numeric'] = decrypted   
        df.loc[idx, 'Decrypted_ID'] = decrypted_id

# ===== 儲存結果 =====
    df.to_csv(output_csv, index=False)
    print(f"加解密完成，結果寫入 {output_csv}")

if __name__ == "__main__":
    input_csv = "files/id_files/all_id_list_v2_ave.csv"
    output_csv = "files/ff3_files/ff3_encrypted_all_output_ave.csv"
    FF3(input_csv, output_csv)