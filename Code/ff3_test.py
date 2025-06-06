# === ff3_test.py (修改版) ===

import hashlib
from ff3 import FF3Cipher

# ====== 工具對照表 ======
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
    "U2": "45", "V2": "46", "W2": "47", "X2": "48", "Z2": "49"
}
translate_map = {
    "A": "10", "B": "11", "C": "12", "D": "13", "E": "14", "F": "15", "G": "16", "H": "17",
    "I": "34", "J": "18", "K": "19", "L": "20", "M": "21", "N": "22", "O": "35", "P": "23",
    "Q": "24", "R": "25", "S": "26", "T": "27", "U": "28", "V": "29", "W": "32", "X": "30", "Z": "33"
}
reverse_map = {v: k for k, v in letter_map.items()}

def calculate_check_digit(id9):
    weights = [1, 9, 8, 7, 6, 5, 4, 3, 2, 1]
    return str((10 - sum(int(n)*w for n, w in zip(id9, weights)) % 10) % 10)

def id_to_numeric(id_number):
    prefix = id_number[0:2]
    if prefix not in letter_map:
        raise ValueError(f"\u8eab\u5206\u8b49\u5b57\u9996\u4e0d\u5408\u6cd5: {prefix}")
    numeric_prefix = int(letter_map[prefix])
    if numeric_prefix >= 50:
        raise ValueError(f"\u975e\u672c\u570b\u8eab\u5206\u8b49\u5b57\u9996: {prefix} → {numeric_prefix} ≥ 50")
    return str(numeric_prefix).zfill(2) + id_number[2:10]

def encrypted_numeric_to_id(numeric):
    letter = reverse_map[numeric[:2]]
    translate_letter = translate_map[letter[0]]
    rest = numeric[2:9]
    check = calculate_check_digit(translate_letter + rest)
    return letter + rest + check

def decrypted_numeric_to_id(numeric):
    letter = reverse_map[numeric[:2]]
    rest = numeric[2:]
    return letter + rest

def generate_tweak(index):
    return hashlib.sha256(str(index).encode()).hexdigest()[:14].upper()

def generate_fallback_tweak(index):
    return hashlib.sha256(f"{index}_retry".encode()).hexdigest()[:14].upper()

def encrypt_with_fallback_and_swap(df, idx, key):
    def encrypt_id(id_str, tweak, key):
        plaintext = id_to_numeric(id_str)
        cipher = FF3Cipher(key, tweak)
        encrypted_numeric = cipher.encrypt(plaintext)
        return plaintext, encrypted_numeric, cipher

    def attempt_adjustment(plaintext, encrypted_numeric, idx):
        judge = int(encrypted_numeric[:2])
        if judge < 50:
            return encrypted_numeric_to_id(encrypted_numeric), encrypted_numeric, False

        adjusted_prefix = int(plaintext[:2]) + 50
        if adjusted_prefix >= 100:
            return "A000000000", encrypted_numeric, False

        new_plaintext = str(adjusted_prefix).zfill(2) + plaintext[2:]
        fallback_tweak = generate_fallback_tweak(idx)
        fallback_cipher = FF3Cipher(key, fallback_tweak)
        try:
            re_encrypted = fallback_cipher.encrypt(new_plaintext)
            if int(re_encrypted[:2]) < 50:
                return encrypted_numeric_to_id(re_encrypted), re_encrypted, True
        except:
            pass
        return "A000000000", encrypted_numeric, False

    # 第一次嘗試
    original_id = df.at[idx, 'ID']
    tweak = generate_tweak(idx)
    plaintext, encrypted_numeric, cipher = encrypt_id(original_id, tweak, key)
    encrypted_id, final_numeric, used_fallback = attempt_adjustment(plaintext, encrypted_numeric, idx)

    if encrypted_id != "A000000000":
        return {
            'Original_ID': original_id,
            'Plaintext': plaintext,
            'Encrypted_Numeric': final_numeric,
            'Encrypted_ID': encrypted_id,
            'Used_Fallback': used_fallback
        }

    if idx + 1 >= len(df):
        return {
            'Original_ID': original_id,
            'Plaintext': plaintext,
            'Encrypted_Numeric': final_numeric,
            'Encrypted_ID': "A000000000",
            'Used_Fallback': used_fallback
        }

    # 對調並遞迴處理兩筆
    df.at[idx, 'ID'], df.at[idx + 1, 'ID'] = df.at[idx + 1, 'ID'], df.at[idx, 'ID']
    result1 = encrypt_with_fallback_and_swap(df, idx, key)
    result2 = encrypt_with_fallback_and_swap(df, idx + 1, key)
    return [result1, result2]
