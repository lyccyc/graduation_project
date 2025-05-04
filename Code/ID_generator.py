import random

# 設定英文字母對應的數值
id_prefix_map = { 
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

# 權重 (依照台灣身分證字號驗證碼計算方式)
weights = [1, 9, 8, 7, 6, 5, 4, 3, 2, 1]

def generate_taiwan_id():
    # 隨機選擇一個英文字母
    letter = random.choice(list(id_prefix_map.keys()))
    letter_value = int(id_prefix_map[letter])

    # 英文字母的數字拆開處理（個位數 *9，加上十位數 *1）
    first_num = (letter_value // 10) * weights[0] + (letter_value % 10) * weights[1]

    # 性別 (1: 男, 2: 女)
    gender = random.choice([1, 2])

    # 產生隨機的 7 個數字
    random_numbers = [random.randint(0, 9) for _ in range(7)]

    # 計算檢查碼
    total = (
        first_num
        + gender * weights[2]
        + sum(n * w for n, w in zip(random_numbers, weights[3:]))
    )
    check_digit = (10 - (total % 10)) % 10  # 避免餘數為 0 產生 10

    # 組合完整身分證字號
    taiwan_id = f"{letter}{gender}{''.join(map(str, random_numbers))}{check_digit}"
    return taiwan_id

def generate_foreigner_id():
    # 隨機選擇一個英文字母
    letter = random.choice(list(id_prefix_map.keys()))
    letter_value = id_prefix_map[letter]

    # 英文字母的數字拆開處理（個位數 *9，加上十位數 *1）
    first_num = (letter_value // 10) * weights[0] + (letter_value % 10) * weights[1]

    # 性別 (8: 男, 9: 女)
    gender = random.choice([8, 9])

    # 產生隨機的 7 個數字
    random_numbers = [random.randint(0, 9) for _ in range(7)]

    # 計算檢查碼
    total = (
        first_num
        + gender * weights[2]
        + sum(n * w for n, w in zip(random_numbers, weights[3:]))
    )
    check_digit = (10 - (total % 10)) % 10  # 避免餘數為 0 產生 10

    # 組合完整身分證字號
    taiwan_id = f"{letter}{gender}{''.join(map(str, random_numbers))}{check_digit}"
    return taiwan_id
