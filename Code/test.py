"""
統一處理本國和外籍
對應主程式: ff3_main.py
"""

import hashlib
from ff3 import FF3Cipher
import pandas as pd

KEY = "2DE79D232DF5585D68CE47882AE256D6"

letter_map = {
    "A1": "00", "B1": "01", "C1": "02", "D1": "03", "E1": "04",
    "F1": "05", "G1": "06", "H1": "07", "I1": "08", "J1": "09",
    "K1": "10", "L1": "11", "M1": "12", "N1": "13", "O1": "14",
    "P1": "15", "Q1": "16", "R1": "17", "S1": "18", "T1": "19",
    "U1": "20", "V1": "21", "W1": "22", "X1": "23", "Z1": "24",

    "A2": "25", "B2": "26", "C2": "27", "D2": "28", "E2": "29",
    "F2": "30", "G2": "31", "H2": "32", "I2": "33", "J2": "34",
    "K2": "35", "L2": "36", "M2": "37", "N2": "38", "O2": "39",
    "P2": "40", "Q2": "41", "R2": "42", "S2": "43", "T2": "44",
    "U2": "45", "V2": "46", "W2": "47", "X2": "48", "Z2": "49",

    "A8": "50", "B8": "51", "C8": "52", "D8": "53", "E8": "54",
    "F8": "55", "G8": "56", "H8": "57", "I8": "58", "J8": "59",
    "K8": "60", "L8": "61", "M8": "62", "N8": "63", "O8": "64",
    "P8": "65", "Q8": "66", "R8": "67", "S8": "68", "T8": "69",
    "U8": "70", "V8": "71", "W8": "72", "X8": "73", "Z8": "74",

    "A9": "75", "B9": "76", "C9": "77", "D9": "78", "E9": "79",
    "F9": "80", "G9": "81", "H9": "82", "I9": "83", "J9": "84",
    "K9": "85", "L9": "86", "M9": "87", "N9": "88", "O9": "89",
    "P9": "90", "Q9": "91", "R9": "92", "S9": "93", "T9": "94",
    "U9": "95", "V9": "96", "W9": "97", "X9": "98", "Z9": "99"
}
translate_map = {
    "A": "10", "B": "11", "C": "12", "D": "13", "E": "14", "F": "15", "G": "16", "H": "17",
    "I": "34", "J": "18", "K": "19", "L": "20", "M": "21", "N": "22", "O": "35", "P": "23",
    "Q": "24", "R": "25", "S": "26", "T": "27", "U": "28", "V": "29", "W": "32", "X": "30", "Z": "33"
}

reverse_map = {v: k for k, v in letter_map.items()}
df = pd.DataFrame()
df['Numeric'] = ""
df['Encrypted_Numeric'] = ""
df['Encrypted_ID'] = ""
df['Status'] = ""
df['Decrypted_Numeric'] = ""
df['Decrypted_ID'] = ""

def calculate_check_digit(id9):
    weights = [1, 9, 8, 7, 6, 5, 4, 3, 2, 1]
    n0 = int(translate_map[id9[0]])
    nums = [n0 // 10, n0 % 10] + [int(ch) for ch in id9[1:]]
    weights = [1, 9, 8, 7, 6, 5, 4, 3, 2, 1]
    total = sum([a * b for a, b in zip(nums, weights)])
    check_digit = (10 - total % 10) % 10

    return str(check_digit)

def number_to_IDN(id_number):
    letter = reverse_map[id_number[:2]][0]
    gender = reverse_map[id_number[:2]][1]
    rest = id_number[2:9]
    id9 = letter + gender + rest
    check = calculate_check_digit(id9)
    return  letter + gender + rest + check

def IDN_to_number(id_number):
    prefix = id_number[0:2]
    numeric_prefix = int(letter_map[prefix])
    return str(numeric_prefix).zfill(2) + id_number[2:10]

def generate_tweak(index):
    return hashlib.sha256(str(index).encode()).hexdigest()[:14].upper()

def decrypt_to_ID(decrypt):
    prefix = decrypt[:2]
    letter = reverse_map[prefix]
    rest = decrypt[2:]
    return letter + rest

def encrypt_fun(plaintext,idx):
    try:
        tweak = generate_tweak(idx)
        cipher = FF3Cipher(KEY, tweak)
        ciphertext = cipher.encrypt(plaintext)
        return ciphertext
    except Exception as e:
        print(f"[加密錯誤] idx={idx}, plaintext={plaintext}, 錯誤: {e}")
        return None

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
    input_csv = "files/id_files/all_id_list_v2_uneven.csv"
    output_csv = "files/ff3_files/ff3_encrypted_all_output_uneven.csv"
    FF3(input_csv, output_csv)
