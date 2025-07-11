"""
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
"""


"""
FF3_main.py

def encrypt_with_mod(plaintext, idx, is_local):

    嘗試加密，如果失敗則嘗試 +/-50 修正。
    返回處理後的明文、密文和狀態。

    ciphertext = encrypt_fun(plaintext, idx)

    if ciphertext is not None:
        return plaintext, ciphertext, "OK", False
    
    # 第一次加密失敗或不符合條件，嘗試 +/-50 修正
    prefix = int(plaintext[:2]) # 再次獲取原始明文前綴

    if is_local:
        adjusted_plaintext = str(prefix + 50) + plaintext[2:]
    else:
        adjusted_plaintext = str(prefix - 50).zfill(2) + plaintext[2:]
    
    adjusted_ciphertext = encrypt_fun(adjusted_plaintext, idx)

    if adjusted_ciphertext is not None:
        return adjusted_plaintext, adjusted_ciphertext, "FIXED_50",True
    
    # 兩種方式都失敗
    return plaintext, None, "FAILED",False # 返回原始明文和 FAILED 狀態
        
def encrypt_with_swap(df, start_index):

    當 df.loc[start_index] 無法成功加密時，嘗試透過交換找到一個解決方案。
    這個函數直接修改 df。

    max_index = len(df) - 1

    # 遍歷從 start_index + 1 開始的後續索引，尋找可以交換的目標
    for j in range(start_index + 1, max_index + 1):
        # 進行交換：將 df.loc[start_index] 的內容與 df.loc[j] 的內容對調
        # 使用 .copy() 避免 SettingWithCopyWarning
        df.iloc[[start_index, j]] = df.iloc[[j, start_index]].copy()

        # 現在 df.loc[start_index] 包含了原 df.loc[j] 的資料
        # 嘗試對這筆新到位的資料進行加密
        plaintext_current = df.loc[df.index[start_index], 'Numeric'][:9]
        is_local_current = int(plaintext_current[:2]) < 50

        # 調用 encrypt_with_mod 進行加密嘗試 (包含 +/-50 修正)
        plaintext_processed, encrypted, status, plus50 = encrypt_with_mod(plaintext_current, start_index, is_local_current)

        if status in ["OK", "FIXED_50"]:
            # 如果成功加密了 df.loc[start_index] (原 df.loc[j] 的資料)
            df.loc[df.index[start_index], 'plaintext'] = plaintext_processed # 更新明文為處理後的
            df.loc[df.index[start_index], 'Encrypted_Numeric'] = encrypted
            df.loc[df.index[start_index], 'Status'] = "SWAPPED" # 因為發生了交換
            df.loc[df.index[start_index], 'Swap_Index'] = j # 記錄和哪一筆交換了
            df.loc[df.index[start_index], 'plus50'] = plus50
            # 這裡的關鍵是：原始 start_index 的資料現在在 j 位置，它會在主迴圈中被處理到
            # 由於我們已經處理了 start_index，可以立即返回，表示這個位置的加密已完成
            return True # 表示成功處理了 start_index
        else:
            # 如果交換後加密仍失敗，則還原本次交換，繼續嘗試與下一筆資料交換
            df.iloc[[start_index, j]] = df.iloc[[j, start_index]].copy() # 還原
            # 如果還原後，你想要將原始的 start_index 的資料標記為 FAILED，則在循環結束後處理
            
    # === 若是最後一筆，嘗試與 index 0 對調 ===
    if start_index == max_index:
        df.iloc[[start_index, 0]] = df.iloc[[0, start_index]].copy()

        plaintext_current = df.loc[df.index[start_index], 'Numeric'][:9]
        is_local_current = int(plaintext_current[:2]) < 50

        plaintext_processed, encrypted, status, plus50 = encrypt_with_mod(plaintext_current, start_index, is_local_current)

        if status in ["OK", "FIXED_50"]:
            df.loc[df.index[start_index], 'plaintext'] = plaintext_processed
            df.loc[df.index[start_index], 'Encrypted_Numeric'] = encrypted
            df.loc[df.index[start_index], 'Status'] = "SWAPPED"
            df.loc[df.index[start_index], 'Swap_Index'] = 0
            return True
        else:
            # 還原
            df.iloc[[start_index, 0]] = df.iloc[[0, start_index]].copy()
            
    df.loc[df.index[start_index], 'Encrypted_Numeric'] = "XXXXXXXXXX"
    df.loc[df.index[start_index], 'Encrypted_ID'] = "A000000000" # 確保有預設值
    df.loc[df.index[start_index], 'Status'] = "FAILED"
    df.loc[df.index[start_index], 'Swap_Index'] = -1
    return False # 表示未能成功處理 start_index
"""
