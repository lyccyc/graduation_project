import hashlib
from ff3 import FF3Cipher

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
    letter = reverse_map.get(numeric[:2], "??")
    translate_letter = translate_map.get(letter[0], "00")
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

def generate_fallback_tweak(index):
    return hashlib.sha256(f"{index}_retry".encode()).hexdigest()[:14].upper()

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

def try_encrypt_record(df, idx, key, swap_count_map, results):
    id_str = df.at[idx, 'ID']
    plaintext, encrypted, cipher = create_cipher_and_encrypt(id_str, idx, key, plus50=False)
    if int(encrypted[:2]) < 50:
        decrypted_id = decrypt_to_id(encrypted, cipher, plus50=False)
        results.append({
            "Original_ID": id_str,
            "Plaintext": plaintext,
            "Encrypted_Numeric": encrypted,
            "Encrypted_ID": encrypted_numeric_to_id(encrypted),
            "Decrypted_ID": decrypted_id,
            "Plus50": False,
            "swap_count": swap_count_map.get(idx, 0)
        })
        return True
    else:
        plaintext, encrypted, cipher = create_cipher_and_encrypt(id_str, idx, key, plus50=True)
        if int(encrypted[:2]) < 50:
            decrypted_id = decrypt_to_id(encrypted, cipher, plus50=True)
            results.append({
                "Original_ID": id_str,
                "Plaintext": plaintext,
                "Encrypted_Numeric": encrypted,
                "Encrypted_ID": encrypted_numeric_to_id(encrypted),
                "Decrypted_ID": decrypted_id,
                "Plus50": True,
                "swap_count": swap_count_map.get(idx, 0)
            })
            return True
    return False

def decrypt_with_swap_logic(encrypted_numeric, plus50, original_index, encrypt_index, key):
    distance = abs(original_index - encrypt_index)
    if original_index > encrypt_index:
        final_index = original_index - distance
    else:
        final_index = original_index + distance

    tweak = generate_tweak(final_index)
    cipher = FF3Cipher(key, tweak)

    try:
        decrypted_numeric = cipher.decrypt(encrypted_numeric)
        if plus50:
            prefix = str(int(decrypted_numeric[:2]) - 50).zfill(2)
            decrypted_numeric = prefix + decrypted_numeric[2:]
        return decrypted_numeric_to_id(decrypted_numeric)
    except Exception as e:
        return f"DECRYPTION_FAILED: {str(e)}"
        
def encrypt_with_swap_if_needed(df, idx, key):
    results = []
    swap_count_map = {i: 0 for i in range(len(df))}

    while idx < len(df):
        # 嘗試原始順序加密
        if try_encrypt_record(df, idx, key, swap_count_map, results):
            idx += 1
            continue

        # 嘗試與下一筆交換
        if idx + 1 < len(df):
            df.at[idx, 'ID'], df.at[idx + 1, 'ID'] = df.at[idx + 1, 'ID'], df.at[idx, 'ID']
            swap_count_map[idx + 1] = swap_count_map.get(idx, 0) + 1
            swap_count_map[idx] = swap_count_map.get(idx + 1, 0)

            if try_encrypt_record(df, idx, key, swap_count_map, results):
                idx += 1
                continue

        # 嘗試與下下筆交換
        if idx + 2 < len(df):
            df.at[idx, 'ID'], df.at[idx + 2, 'ID'] = df.at[idx + 2, 'ID'], df.at[idx, 'ID']
            swap_count_map[idx + 2] = swap_count_map.get(idx, 0) + 2
            swap_count_map[idx] = swap_count_map.get(idx + 2, 0)

            if try_encrypt_record(df, idx, key, swap_count_map, results):
                idx += 1
                continue

        # 最終失敗：三次都無法滿足條件，放棄該筆
        id_str = df.at[idx, 'ID']
        plaintext = id_to_numeric(id_str)
        results.append({
            "Original_ID": id_str,
            "Plaintext": plaintext,
            "Encrypted_Numeric": "XXXXXXXXXX",
            "Encrypted_ID": "A000000000",
            "Decrypted_ID": "",
            "Plus50": False,
            "swap_count": swap_count_map.get(idx, 0)
        })
        idx += 1

    return results
