import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from datetime import datetime

# --- SETTING KONEKSI ---
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

def koneksi_sheet(sheet_id):
    try:
        # Mengambil dari menu Secrets Streamlit
        info = dict(st.secrets["gcp_service_account"])
        # Membersihkan simbol \n jika ada
        info["private_key"] = info["private_key"].replace("\\n", "\n")
        
        creds = ServiceAccountCredentials.from_json_keyfile_dict(info, SCOPE)
        client = gspread.authorize(creds)
        return client.open_by_key(sheet_id).get_worksheet(0)
    except Exception as e:
        st.error(f"Koneksi Gagal: {e}")
        return None

# ID Link Google Sheets kamu
ID_BARANG = "1qf8KmurJi8CbVmwsbRSDCWxir_Ejw2s9y9vGZTNmxAg"
ID_MEMBER = "1mMbvhMO3uQAjktAPeZ-G_s5IWBVkcuxg8YgPpSQjIgo"
ID_LAPORAN = "1KA5qK57aFiLkPIuFRbZD4g5PU_5nly-19Dup1DtdkqE"

st.set_page_config(page_title="KASIR DWI BANGKIT", layout="wide")
st.title("🏪 Kasir Dwi Bangkit Cloud")

# Ambil Data
sh_barang = koneksi_sheet(ID_BARANG)
sh_member = koneksi_sheet(ID_MEMBER)

if sh_barang and sh_member:
    df_barang = pd.DataFrame(sh_barang.get_all_records())
    df_member = pd.DataFrame(sh_member.get_all_records())
    
    if 'keranjang' not in st.session_state:
        st.session_state.keranjang = []

    col1, col2 = st.columns([1, 1.5])

    with col1:
        st.subheader("🛒 Input Barang")
        member_list = ["Umum"] + df_member['Nama Member'].tolist() if 'Nama Member' in df_member.columns else ["Umum"]
        nama_member = st.selectbox("Pilih Member", member_list)
        barcode = st.text_input("Scan Barcode")
        
        if barcode:
            hasil = df_barang[df_barang['Barcode'].astype(str) == barcode]
            if not hasil.empty:
                item = hasil.iloc[0]
                st.success(f"Produk: {item['Nama']}")
                qty = st.number_input("Qty", min_value=1, value=1)
                if st.button("Tambah"):
                    harga = item['Member'] if nama_member != "Umum" else item['Ecer']
                    st.session_state.keranjang.append({
                        "Nama": item['Nama'], "Harga": harga, "Qty": qty, "Total": harga * qty
                    })
                    st.rerun()
            else:
                st.error("Barang tidak terdaftar")

    with col2:
        st.subheader("📋 Keranjang")
        if st.session_state.keranjang:
            df_k = pd.DataFrame(st.session_state.keranjang)
            st.table(df_k)
            st.header(f"TOTAL: Rp {df_k['Total'].sum():,.0f}")
            
            if st.button("SIMPAN TRANSAKSI"):
                sh_lap = koneksi_sheet(ID_LAPORAN)
                tgl = datetime.now().strftime("%Y-%m-%d %H:%M")
                for r in st.session_state.keranjang:
                    sh_lap.append_row([tgl, nama_member, r['Nama'], r['Qty'], r['Total']])
                st.success("Berhasil Tersimpan!")
                st.session_state.keranjang = []
                st.rerun()
    
    st.divider()
    with st.expander("🔍 Cek Stok Gudang"):
        st.dataframe(df_barang)
else:
    st.warning("Sedang menghubungkan ke Google Sheets... Harap tunggu.")
