from ff3 import FF3Cipher
import pandas as pd
import hashlib

# ====== 工具函數 ======
letter_map = {
    "A1": "00",  "B1": "01",  "C1": "02",  "D1": "03",  "E1": "04",
    "F1": "05",  "G1": "06",  "H1": "07",  "I1": "08",  "J1": "09",
    "K1": "10", "L1": "11", "M1": "12", "N1": "13", "O1": "14",
    "P1": "15", "Q1": "16", "R1": "17", "S1": "18", "T1": "19",
    "U1": "20", "V1": "21", "W1": "22", "X1": "23", "Y1": "24",
    "Z1": "25",
    "A2": "26", "B2": "27", "C2": "28", "D2": "29", "E2": "30",
    "F2": "31", "G2": "32", "H2": "33", "I2": "34", "J2": "35",
    "K2": "36", "L2": "37", "M2": "38", "N2": "39", "O2": "40",
    "P2": "41", "Q2": "42", "R2": "43", "S2": "44", "T2": "45",
    "U2": "46", "V2": "47", "W2": "48", "X2": "49", "Y2": "50",
    "Z2": "51"
}


# 字母對照表 A→10, B→11, ..., Z→35
translate_map = { 
    "A": "10",
    "B": "11",
    "C": "12",
    "D": "13",
    "E": "14",
    "F": "15",
    "G": "16",
    "H": "17",
    "I": "34",
    "J": "18",
    "K": "19",
    "L": "20",
    "M": "21",
    "N": "22",
    "O": "35",
    "P": "23",
    "Q": "24",
    "R": "25",
    "S": "26",
    "T": "27",
    "U": "28",
    "V": "29",
    "W": "32",
    "X": "30",
    "Y": "31",
    "Z": "33",}

reverse_map = {v: k for k, v in letter_map.items()}

def calculate_check_digit(id9):
    weights = [1, 9, 8, 7, 6, 5, 4, 3, 2, 1]
    return str((10 - sum(int(n)*w for n, w in zip(id9, weights)) % 10) % 10)

def id_to_numeric(id_number):
    return str(letter_map[id_number[0:2]]) + id_number[2:10]

#%%
#加密成另一種身分證
def encrypted_numeric_to_id(numeric):
    letter = reverse_map[numeric[:2]]
    #取letter第一個值轉成兌換表(translate_map)
    translate_letter = translate_map[letter[0]]
    rest = numeric[2:9]
    combined = translate_letter + rest
    #轉換後數串接上rest，傳入calculate fun
    check = calculate_check_digit(combined)
    return letter + rest + check

#%%
def adject_value(plaintext,numeric):  
    judge = int(numeric[:2])
    if judge < 50:
        return encrypted_numeric_to_id(numeric)
    else:
        adject_value = int(plaintext[:2]) + 50
        p = str(adject_value) + plaintext[2:]
        encrypted_numeric = cipher.encrypt(p)
        if int(encrypted_numeric[:2]) < 50 :
            return encrypted_numeric_to_id(encrypted_numeric)
        else :
            return "A000000000"
        
#%%
def decrypted_numeric_to_id(numeric):
    letter = reverse_map[numeric[:2]]
    rest = numeric[2:]
    return letter + rest

def generate_tweak(index):
    # 使用 row index 作為 deterministic tweak 來源
    return hashlib.sha256(str(index).encode()).hexdigest()[:14].upper()

key = "2DE79D232DF5585D68CE47882AE256D6"
tweak = "CBD09280979564"
cipher = FF3Cipher(key, tweak)

#%%
'''
key = "2DE79D232DF5585D68CE47882AE256D6"
tweak = "CBD09280979564"

original_id = "U173044343"
plaintext = id_to_numeric(original_id)
print(f'plaintext: {plaintext}')
tweak = tweak

cipher = FF3Cipher(key, tweak)
encrypted_numeric = cipher.encrypt(plaintext) 
print(f'en_numeric: {encrypted_numeric}')
encrypted_id = adject_value(plaintext,encrypted_numeric)
print(f'encrypted_id: {encrypted_id}')
# %%
'''