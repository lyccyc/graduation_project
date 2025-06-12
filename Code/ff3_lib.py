import hashlib
from ff3 import FF3Cipher

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
    "U2": "45", "V2": "46", "W2": "47", "X2": "48", "Z2": "49"
}

translate_map = {
    "A": "10", "B": "11", "C": "12", "D": "13", "E": "14", "F": "15", "G": "16", "H": "17",
    "I": "34", "J": "18", "K": "19", "L": "20", "M": "21", "N": "22", "O": "35", "P": "23",
    "Q": "24", "R": "25", "S": "26", "T": "27", "U": "28", "V": "29", "W": "32", "X": "30", "Z": "33"
}

reverse_map = {v: k for k, v in letter_map.items()}

def id_to_numeric(id_number):
    prefix = id_number[0:2]
    numeric_prefix = int(letter_map[prefix])
    return str(numeric_prefix).zfill(2) + id_number[2:10]

def encrypted_numeric_to_id(numeric):
    letter = reverse_map[numeric[:2]]
    translate_letter = translate_map[letter[0]]
    rest = numeric[2:9]
    check = calculate_check_digit(translate_letter + rest)
    return letter + rest + check

def decrypted_numeric_to_id(numeric):
    prefix = numeric[:2]
    if prefix not in reverse_map:
        return f"INVALID_PREFIX_{prefix}"
    letter = reverse_map[prefix]
    rest = numeric[2:]
    return letter + rest

def calculate_check_digit(id9):
    weights = [1, 9, 8, 7, 6, 5, 4, 3, 2, 1]
    return str((10 - sum(int(n)*w for n, w in zip(id9, weights)) % 10) % 10)

def generate_tweak(index):
    return hashlib.sha256(str(index).encode()).hexdigest()[:14].upper()

def create_cipher_and_encrypt(id_str, index, key, plus50=False):
    plaintext = id_to_numeric(id_str)
    if plus50:
        plaintext = str(int(plaintext[:2]) + 50).zfill(2) + plaintext[2:]
    tweak = generate_tweak(index)
    cipher = FF3Cipher(key, tweak)
    encrypted = cipher.encrypt(plaintext)
    return plaintext, encrypted, cipher

def decrypt_to_id(encrypted, cipher, plus50):
    decrypted = cipher.decrypt(encrypted)
    if plus50:
        prefix = str(int(decrypted[:2]) - 50).zfill(2)
        decrypted = prefix + decrypted[2:]
    return decrypted_numeric_to_id(decrypted)

def decrypt_with_tweak(encrypted_numeric, plus50, encrypt_index):
    tweak = generate_tweak(encrypt_index)
    cipher = FF3Cipher(KEY, tweak)
    decrypted = cipher.decrypt(encrypted_numeric)
    if plus50:
        prefix = str(int(decrypted[:2]) - 50).zfill(2)
        decrypted = prefix + decrypted[2:]
    return decrypted_numeric_to_id(decrypted)

def try_encrypt_record(df, idx, key, results, actual_index, plus50=False):
    id_str = df.at[idx, 'ID']
    plaintext, encrypted, cipher = create_cipher_and_encrypt(id_str, actual_index, key, plus50=plus50)
    if int(encrypted[:2]) < 50:
        decrypted_id = decrypt_to_id(encrypted, cipher, plus50=plus50)
        results.append({
            "Original_ID": id_str,
            "Plaintext": plaintext,
            "Encrypted_Numeric": encrypted,
            "Encrypted_ID": encrypted_numeric_to_id(encrypted),
            "Decrypted_ID": decrypted_id,
            "Plus50": plus50,
            "Original_Index": idx,
            "Encrypt_Index": actual_index
        })
        return True
    return False

def encrypt_with_swap_if_needed(df, idx, key):
    results = []

    while idx < len(df):
        # 嘗試原始明文
        if try_encrypt_record(df, idx, key, results, idx, plus50=False):
            idx += 1
            continue

        # 嘗試原始明文 +50
        success_plus50 = try_encrypt_record(df, idx, key, results, idx, plus50=True)
        if success_plus50:
            idx += 1
            continue

        # 回復原始明文，開始進行 swap
        if idx + 1 < len(df):
            df.at[idx, 'ID'], df.at[idx + 1, 'ID'] = df.at[idx + 1, 'ID'], df.at[idx, 'ID']
            if try_encrypt_record(df, idx, key, results, idx, plus50=False):
                idx += 1
                continue
            if try_encrypt_record(df, idx, key, results, idx, plus50=True):
                idx += 1
                continue

        if idx + 2 < len(df):
            df.at[idx, 'ID'], df.at[idx + 2, 'ID'] = df.at[idx + 2, 'ID'], df.at[idx, 'ID']
            if try_encrypt_record(df, idx, key, results, idx, plus50=False):
                idx += 1
                continue
            if try_encrypt_record(df, idx, key, results, idx, plus50=True):
                idx += 1
                continue

        # 無法加密成功
        id_str = df.at[idx, 'ID']
        plaintext = id_to_numeric(id_str)
        results.append({
            "Original_ID": id_str,
            "Plaintext": plaintext,
            "Encrypted_Numeric": "XXXXXXXXXX",
            "Encrypted_ID": "A000000000",
            "Decrypted_ID": "",
            "Plus50": False,
            "Original_Index": idx,
            "Encrypt_Index": -1
        })
        idx += 1

    return results
