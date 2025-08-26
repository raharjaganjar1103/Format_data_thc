import streamlit as st
import pandas as pd
import numpy as np
import pyarrow as pa
import io

st.title('Anomali transaksi harian Format THC Gabungan')
st.write("""1. File yang dibutuhkan THC Final.csv""")
st.write("""2. Rapihkan data tersebut jadi seperti contoh ini: https://drive.google.com/file/d/14Ofz53dSVRFzlFrrc8snZmmkHq7CO-R2/view?usp=drive_link""")
st.write("""3. Hapus karakter spesial terlebih dahulu pada file excel nya, lengkapnya ada disini tutorialnya : https://drive.google.com/file/d/1xABUwrMatieKFsNeUbOWl2KuDh6BVLwy/view?usp=drive_link """)

## SESI UPLOAD FILE   
uploaded_files = st.file_uploader("Upload files", accept_multiple_files=True, type=['csv'])

df_PDR = None
df_S = None

@st.cache_data
def load_excel(file):
    return pd.read_excel(file, engine='openpyxl')

if uploaded_files:
    for file in uploaded_files:
        if file.name.lower().endswith('.csv') and file.name == 'THC Final.csv':
            # Asumsi delimiter ;, bisa diubah jika perlu
            try:
                df_PDR = pd.read_csv(file, delimiter=';')
            except Exception:
                df_PDR = pd.read_csv(file)  # fallback delimiter default koma

    if df_PDR is None:
        st.error("File 'THC Final.csv' tidak ditemukan. Mohon upload file yang benar.")
    else:
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
            
        # Proses data dan tampilkan hasil
        df_hasil = tambah_kolom_estimasi(df_PDR)
        st.success("File berhasil diproses!")
        st.dataframe(df_hasil)

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

# Download hasil sebagai Excel
        import io
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_hasil.to_excel(writer, index=False)
        st.download_button(
            label="Download hasil sebagai Excel",
            data=output.getvalue(),
            file_name="THC Final Gabungan.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )


## Bagian main() dihapus karena tidak relevan untuk Streamlit
