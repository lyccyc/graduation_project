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
df['Swap_Index'] = -1
df['Plus50'] = False
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
    return  letter + rest + check

def IDN_to_number(id_number):
    prefix = id_number[0:2]
    numeric_prefix = int(letter_map[prefix])
    return str(numeric_prefix).zfill(2) + id_number[2:10]

def check_upsidedown(arr, check):
    n = len(arr)
    result = [None] * n

    for i in arr.index:
        if (int(check[i][0:2]) >= 50) and (i%2 == 0):
            result[i] = arr[i][1] + arr[i][0] + arr[i][2:]
        elif (int(check[i][0:2]) < 50) and (i%2 == 1):
            result[i] = arr[i][1] + arr[i][0] + arr[i][2:]
        else:
            result[i] = arr[i]
    return result

def adject_position(arr):
    n = len(arr)
    even_index = 1
    odd_index = 0
    result = [None] * n

    for i in arr:
        num = int(i[0:2])
        if even_index >= n:
            result[odd_index] = i
            odd_index += 2
            continue
        elif odd_index >= n:
            result[even_index] = i
            even_index += 2
            continue
        else:
            if num >= 50:
                if even_index < n:
                    result[even_index] = i
                    even_index += 2
            else:
                if odd_index < n:
                    result[odd_index] = i
                    odd_index += 2
    return result

def adject_value(num_arr, en_arr):
    n = len(num_arr)
    result = [None] * n

    for i in num_arr.index:
        tmp = int(en_arr[i][0:2])       #加密後字串
        judge = int(num_arr[i][0:2])    #對照表轉換後字串
        if judge < 50:                  #本國
            if tmp >= 50:
                judge += 50
            judge = str(judge)

        else:                           #外來
            if tmp < 50:
                judge -= 50
            judge = str(judge)
        result[i] = judge + num_arr[i][2:]
    return result

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

def encrypt_with_mod(plaintext,idx,is_local):
    tweak = generate_tweak(idx)
    cipher = FF3Cipher(KEY, tweak)
    ciphertext = cipher.encrypt(plaintext)

    prefix = int(plaintext[:2])
    cipher_prefix = int(ciphertext[:2])

    if is_local and cipher_prefix < 50:
        return plaintext, ciphertext, "OK"
    elif not is_local and cipher_prefix >= 50:
        return plaintext, ciphertext, "OK"
    else:
        # === 嘗試 +/-50 修正後再次加密 ===
        if is_local:
            adjusted_plaintext = str(prefix + 50) + plaintext[2:]
        else:
            adjusted_plaintext = str(prefix - 50).zfill(2) + plaintext[2:]

        adjusted_ciphertext = encrypt_fun(adjusted_plaintext, idx)

        adjusted_cipher_prefix = int(adjusted_ciphertext[:2])
        if is_local and adjusted_cipher_prefix < 50:
            return adjusted_plaintext, adjusted_ciphertext, "FIXED_50"
        elif not is_local and adjusted_cipher_prefix >= 50:
            return adjusted_plaintext, adjusted_ciphertext, "FIXED_50"
        else:
            return adjusted_plaintext, None, "FAILED"
        
def encrypt_with_swap(df, start_index):
    current_index = start_index
    max_index = len(df) - 1

    while current_index + 1 <= max_index:
        # 對調 current_index 和 current_index + 1
        df.iloc[[current_index, current_index + 1]] = df.iloc[[current_index + 1, current_index]]

        # 先處理對調後上來的資料（即 current_index）
        row = df.iloc[current_index]
        # tweak = generate_tweak(current_index)
        plaintext = row['Numeric'][:9]
        is_local = int(plaintext[:2]) < 50
        plaintext, encrypted, status= encrypt_with_mod(plaintext,current_index, is_local)

        if status in ["OK", "FIXED_50"]:
            df.at[df.index[current_index], 'plaintext'] = plaintext
            df.at[df.index[current_index], 'Encrypted_Numeric'] = encrypted
            df.at[df.index[current_index], 'Status'] = status
            return plaintext, encrypted, status, current_index 

        # 對調無效，還原（但不是退回上一個，而是繼續對調更後面的）
        plaintext = df.loc[current_index , 'original_plaintext']
        # 對調回來後再對調到下一筆（往後兩筆）
        current_index += 1  # 對調往後滑動，直到成功為止
        encrypt_with_mod(plaintext,current_index, is_local)
    
    # 若到了最後都還不成功，也不設為 FAILED，視為極限應該不會發生
    return None, None, "UNRESOLVED", None
