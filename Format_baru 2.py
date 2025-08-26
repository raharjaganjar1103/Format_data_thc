import pandas as pd
import numpy as np

# --- FUNGSI PERHITUNGAN ---
def ambil_3_digit_akhir(val):
    try:
        if pd.isna(val):
            return 0
        return int(str(int(val))[-3:])
    except Exception:
        return 0

def estimasi_nominal_kecil_menabung(val):
    return ambil_3_digit_akhir(val)

def estimasi_nominal_kecil_penarikan(val):
    return ambil_3_digit_akhir(val)

def estimasi_uang(val):
    try:
        if pd.isna(val):
            return 0
        return int(np.ceil(val / 1000.0) * 1000)
    except Exception:
        return 0

def estimasi_nabung_2(x):
    return x - 500 if x > 500 else 0

def estimasi_nabung_3(x):
    return x + 500 if x < 500 else 0

def tf_1(row):
    if row["Estimasi Nabung 1"] < 500:
        return (
            (row["Estimasi Nabung 1"] == row["Estimasi Nominal Kecil Menabung"])
            or (row["Estimasi Nabung 3"] == row["Estimasi Nominal Kecil Menabung"])
        )
    else:
        return (
            (row["Estimasi Nominal Kecil Menabung"] == row["Estimasi Nabung 1"])
            or (row["Estimasi Nominal Kecil Menabung"] == row["Estimasi Nabung 2"])
        )

def estimasi_penarikan_1(val):
    return ambil_3_digit_akhir(val)

def estimasi_penarikan_2(x):
    return x - 500 if x > 500 else 0

def tf2(row):
    if row["Estimasi Penarikan 1"] < 500:
        return row["Estimasi Penarikan 1"] == row["Estimasi Nominal Kecil Penarikan"]
    else:
        return (
            (row["Estimasi Nominal Kecil Penarikan"] == row["Estimasi Penarikan 1"])
            or (row["Estimasi Nominal Kecil Penarikan"] == row["Estimasi Penarikan 2"])
        )

def final_filter(row):
    return bool(row["T/F 1"] or row["T/F2"])

# --- PROSES TAMBAHAN KOLUMN ---
def tambah_kolom_estimasi(df):
    df["Estimasi Nominal Kecil Menabung"] = df["Db Total"].apply(estimasi_nominal_kecil_menabung)
    df["Estimasi Nominal Kecil Penarikan"] = df["Cr Total"].apply(estimasi_nominal_kecil_penarikan)
    df["Estimasi Uang"] = df["Db Total2"].apply(estimasi_uang)
    df["Estimasi Nabung 1"] = df["Estimasi Uang"] - df["Db Total2"]
    df["Estimasi Nabung 2"] = df["Estimasi Nabung 1"].apply(estimasi_nabung_2)
    df["Estimasi Nabung 3"] = df["Estimasi Nabung 1"].apply(estimasi_nabung_3)
    df["Estimasi Penarikan 1"] = df["Db Total2"].apply(estimasi_penarikan_1)
    df["Estimasi Penarikan 2"] = df["Estimasi Penarikan 1"].apply(estimasi_penarikan_2)
    df["T/F 1"] = df.apply(tf_1, axis=1)
    df["T/F2"] = df.apply(tf2, axis=1)
    df["Final Filter"] = df.apply(final_filter, axis=1)
    return df

def main():
    input_file = "THC Final.csv"
    output_file = "THC Final Gabungan.xlsx"
    delimiter = ';'  # Ganti jika file Anda pakai koma

    df = pd.read_csv(input_file, delimiter=delimiter)
    df = tambah_kolom_estimasi(df)
    df.to_excel(output_file, index=False)
    print(f"File dengan kolom tambahan berhasil disimpan ke {output_file}")

if __name__ == "__main__":
    main()