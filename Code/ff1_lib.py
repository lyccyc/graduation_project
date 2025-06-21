import math
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Random import get_random_bytes
import pandas as pd

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

def CIPH(key, X):
    """
    輸入:
    key: 加密密鑰，類型為bytes，長度應為16位元組。
    X: 要加密的資料，類型為bytes，長度應為16位元組。
    """
    # 使用 PyCtyptodome 程式庫實作
    # 選擇 Cipher-block chaining (CBC)模態
    cipher = AES.new(key, AES.MODE_CBC, iv=bytes(16))
    iv = cipher.iv
    # 加密 X
    ciphertext = cipher.encrypt(X)
    return ciphertext

def PRF(key, X):
    """
    輸入:
    key: 加密密鑰，類型為bytes，長度應為16位元組。
    X: 要進行處理的數據，類型為bytes，長度應為16位元組的整數倍。
    """
    # 計算X可以分成多少個16位元組的塊
    m = int(len(X) / 16)
    zero = 0
    # 初始化Y為16位元組的0值
    Y_0 = zero.to_bytes(16, 'big')
    # 將X分解為多個16位元組的塊
    X_list = [X[i*16 : (i+1)*16] for i in range(m)]
    for i in range(m):
        if i == 0:
            # 將Y從 bytes 轉換為整數
            Y_0 = int.from_bytes(Y_0, 'big')
            # 將當前塊X從 bytes 轉換為整數
            X = int.from_bytes(X_list[i], 'big')
            data = Y_0 ^ X  # 對Y和X進行XOR運算
            # 將結果由整數轉換回 bytes
            data = data.to_bytes(16, 'big')
            # 使用密鑰對數據進行加密
            Y = CIPH(key, data)
        # 將Y從 bytes 轉換為整數
        Y = int.from_bytes(Y, 'big')
        # 將當前塊X從 bytes 轉換為整數
        X = int.from_bytes(X_list[i], 'big')
        # 與前一密文塊進行XOR運算
        data = Y ^ X
        # 將結果轉換回 bytes
        data = data.to_bytes(16, 'big')
        Y = CIPH(key, data)
    return Y

def NUM_radix(n, radix):
    """
    將數字n轉換成給定基數radix的字串表示形式。
    """

    if n == 0:
        return 0
    a = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 'A', 'B', 'C', 'D', 'E', 'F']
    b = []
    while n > 0:
        b.append(a[n % radix])
        n = n // radix
    # 反轉列表以得到正確的順序
    b.reverse()
    return int(''.join(map(str, b)))

def str_radix_m(n, m, radix):
    """
    給定一個數字n和長度m，將數字轉換為基數radix的字串表示，確保字串長度為m。
    """
    X = [0] * m
    for i in range(m - 1, -1, -1):
        # 獲取當前基數的餘數
        X[i] = n % radix
        # 更新數字為商
        n = n // radix
    return ''.join(map(str, X))

def FF1(plaintext, radix, key, tweak):
    """
    輸入:
    plaintext: 待加密的文本字串。
    radix: 基數，用於確定加密的基數系統。
    key: 加密密鑰，類型為bytes，長度應為16位元組。
    tweak: 用於加密調整的數據，類型為bytes。
    """
    # n為plaintext字串的字元長度
    n = len(plaintext)
    # 回傳小於等於x的最大整數
    u = math.floor(n / 2)
    v = n - u
    A = plaintext[:u]
    B = plaintext[u:]

    # math.ceil(x)回傳小於等於x的最大整數
    b = math.ceil((math.ceil(math.log2(radix) * v)) / 8)
    d = 4 * math.ceil(b / 4) + 4
    t = len(tweak)

    # || 表示 concatenation
    # P = [1]^1 || [2]^1 || [1]^1 ||[radix]^3 || [10]^1 || [u mod 256]^1 || [n]^4 || [t]^4
    P = bytes([1, 2, 1]) + radix.to_bytes(3, 'big') + bytes([10, u%256]) + n.to_bytes(4, 'big') + t.to_bytes(4, 'big')

    for i in range(10):
        # Q = tweak || [0]^(-t-b-1) mod 16 || [i]^1 ||[NUM_radix(B)]^b
        Q = tweak + (0).to_bytes((-t - b - 1) % 16, 'big') + i.to_bytes(1, 'big') + NUM_radix(int(B), radix).to_bytes(b, 'big')
        R = PRF(key, P + Q)
        y = int.from_bytes(R[1], 'big')
        y = NUM_radix(y, 2)

        if i % 2 == 0:
            m = u
        else:
            m = v

        c = (NUM_radix(int(A), radix) + y) % radix ** m
        # 將整數 c 轉換為長度為m的字串
        C = str_radix_m(c, m, radix)
        A = B
        B = C

    return str(A) + str(B)

def FF1_decrypt(ciphertext, radix, key, tweak):
    """
    輸入:
    ciphertext: 待解密的文本字串。
    radix: 基數，用於確定解密的基數系統。
    key: 解密密鑰，類型為bytes，長度應為16位元組。
    tweak: 用於解密調整的數據，類型為bytes。
    輸出:
    返回解密和處理後的文本。
    """
    n = len(ciphertext)
    u = math.floor(n / 2)
    v = n - u
    A = ciphertext[:u]
    B = ciphertext[u:]

    b = math.ceil((math.ceil(math.log2(radix) * v)) / 8)
    d = 4 * math.ceil(b / 4) + 4
    tweak = tweak.to_bytes(2, 'big')
    t = len(tweak)

    P = bytes([1, 2, 1]) + radix.to_bytes(3, 'big') + bytes([10, u%256]) + n.to_bytes(4, 'big') + t.to_bytes(2, 'big')

    for i in range(9, -1, -1):
        if i % 2 == 0:
            m = u
        else:
            m = v

        C = A
        A = B
        B = C

        Q = tweak + (0).to_bytes((-t - b - 1) % 16, 'big') + i.to_bytes(1, 'big') + NUM_radix(int(B), radix).to_bytes(b, 'big')
        R = PRF(key, P + Q)
        y = int.from_bytes(R, 'big')
        y = NUM_radix(y, 2)

        c = (NUM_radix(int(A), radix) - y) % radix ** m
        A = str_radix_m(c, m, radix)

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
            else:
                judge = str(judge)

        else:                           #外來
            if tmp < 50:
                judge -= 50
            else:
                judge = str(judge)
        result[i] = tmp + num_arr[i][2:]
    return result

def calculate_check_digit(id9):
    weights = [1, 9, 8, 7, 6, 5, 4, 3, 2, 1]
    return str((10 - sum(int(n)*w for n, w in zip(id9, weights)) % 10) % 10)

def number_to_IDN(arr):
    n = len(arr)
    result = [None] * n

    for i in arr.index:
        result_ = ''
        letter = reverse_map[arr[i][:2]]
        translate_letter = translate_map[letter[0]]
        rest = arr[i][2:9]
        check = calculate_check_digit(translate_letter + rest)
        result_ = letter + rest + check
        result[i] = result_
    return result

def IDN_to_number(arr):
    n = len(arr)
    result = [None] * n

    for i in arr.index:
        C =''
        prefix = arr[i][0:2]
        numeric_prefix = int(letter_map[prefix])
        C = str(numeric_prefix) + arr[i][2:10]
    result[i] = C
    return result

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