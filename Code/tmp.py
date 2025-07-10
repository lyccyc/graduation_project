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