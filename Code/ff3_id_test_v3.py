import pandas as pd
import ff3_lib as ff3

KEY = "2DE79D232DF5585D68CE47882AE256D6"

def main():
    input_csv = "files/tw_id_list.csv"
    output_csv = "files/ff3_v3_output.csv"
    df = pd.read_csv(input_csv)

    # 加密與記錄
    results = ff3.encrypt_with_swap_if_needed(df, 0, KEY)
    output_df = pd.DataFrame(results)
    output_df.to_csv(output_csv, index=False)
    print(f"加密完成，結果儲存於 {output_csv}")

if __name__ == "__main__":
    main()
