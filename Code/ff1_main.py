import pandas as pd
import ff1_lib as ff1
from Crypto.Util.Padding import pad
from Crypto.Random import get_random_bytes

key = get_random_bytes(16)

def main():
    input_csv = "files/all_id_list.csv"
    df = pd.read_csv(input_csv)

    df['numeric'] = ff1.IDN_to_number(df['ID'])
    # df['Q'] = ff1.IDN_to_number(df['ID'])
    for i in df.index:
        index = i
        tweak = index.to_bytes(2, 'big')
        plaintext = df.loc[i, ['numeric']]
        # df.loc[i, 'encrypt_num'] = ff1.FF1(plaintext, 10, key, tweak)
        try:
            df.iloc[i, df.columns.get_loc('encrypt_num')] = ff1.FF1(plaintext, 10, key, tweak)
        except ValueError as e:
            print(f"[錯誤] i={i}, plaintext={plaintext}")
            raise e
    df['adject position'] = ff1.adject_position(df['Q'])
    df['adject value'] = ff1.adject_value(df['adject position'])
    df['Y[1~10]'] = ff1.number_to_IDN(df['adject value'])
    df['Y[1~10]'] = ff1.check_upsidedown(df['Y[1~10]'], df['adject position'])

    df.to_csv("files/ff1_output.csv", index=False, encoding='utf-8-sig')

if __name__ == "__main__":
    main()
