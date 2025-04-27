import pandas as pd
from ff3 import FF3Cipher
import os

# ====== 設定固定Key ======
KEY = "2DE79D232DF5585D68CE47882AE256D6"

# ====== 英文字母對應數值表 ======
id_prefix_map = {
    "A": 10, "B": 11, "C": 12, "D": 13, "E": 14, "F": 15, "G": 16, "H": 17, "I": 34,
    "J": 18, "K": 19, "M": 21, "N": 22, "O": 35, "P": 23, "Q": 24, "T": 27, "U": 28,
    "V": 29, "W": 32, "X": 30, "Z": 33
}
number_prefix_map = {v: k for k, v in id_prefix_map.items()}

# ====== 工具函數 ======
def generate_random_tweak():
    return os.urandom(7).hex().upper()

def idn_to_number(idn):
    head = idn[0]
    sex = idn[1]
    if head not in id_prefix_map:
        raise ValueError(f"無效的身分證字母: {head}")
    if sex not in ['1', '2', '8', '9']:
        raise ValueError(f"無效的性別碼: {sex}")
    head_value = id_prefix_map[head]
    return f"{head_value:02d}" + sex + idn[2:]

def number_to_idn(number):
    head_value = int(number[:2])
    sex = number[2]
    rest = number[3:]
    if head_value not in number_prefix_map:
        raise ValueError(f"無法反推的數值: {head_value}")
    if sex not in ['1', '2', '8', '9']:
        raise ValueError(f"無法反推的性別碼: {sex}")
    head_char = number_prefix_map[head_value]
    return head_char + sex + rest

# ====== 主流程 ======
def encrypt_id_numbers(input_csv, output_csv):
    df = pd.read_csv(input_csv)
    key = KEY
    encrypted_ids = []
    tweaks = []

    for idx, row in df.iterrows():
        plaintext_id = row['ID']
        plaintext_number = idn_to_number(plaintext_id)
        tweak = generate_random_tweak()
        tweaks.append(tweak)
        c = FF3Cipher(key, tweak)
        ciphertext_number = c.encrypt(plaintext_number)
        ciphertext_id = number_to_idn(ciphertext_number)
        encrypted_ids.append(ciphertext_id)

    df['Encrypted_ID'] = encrypted_ids
    df['Tweak'] = tweaks
    df.to_csv(output_csv, index=False)

# ====== 主解密流程 ======
def decrypt_id_numbers(input_csv, output_csv):
    df = pd.read_csv(input_csv)
    key = KEY
    decrypted_ids = []
    match_results = []

    for idx, row in df.iterrows():
        encrypted_id = row['Encrypted_ID']
        tweak = row['Tweak']
        encrypted_number = idn_to_number(encrypted_id)
        c = FF3Cipher(key, tweak)
        decrypted_number = c.decrypt(encrypted_number)
        decrypted_id = number_to_idn(decrypted_number)
        decrypted_ids.append(decrypted_id)
        original_id = row['ID'] if 'ID' in row else None
        match_results.append(decrypted_id == original_id)

    df['Decrypted_ID'] = decrypted_ids
    df['Match'] = match_results
    df.to_csv(output_csv, index=False)

if __name__ == "__main__":
    input_csv = "files/id_list.csv"
    encrypted_csv = "files/Encrypted_ID_number.csv"
    decrypted_csv = "files/Decrypted_ID_number.csv"

    encrypt_id_numbers(input_csv, encrypted_csv)
    print(f"加密完成，輸出到 {encrypted_csv}")

    decrypt_id_numbers(encrypted_csv, decrypted_csv)
    print(f"解密完成，輸出到 {decrypted_csv}")
