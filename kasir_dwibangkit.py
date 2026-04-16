import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from datetime import datetime

# --- KONEKSI GOOGLE SHEETS VIA SECRETS ---
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

def koneksi_sheet(sheet_id):
    try:
        # MEMBACA DARI MENU SECRETS STREAMLIT
        info_kunci = dict(st.secrets["gcp_service_account"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(info_kunci, SCOPE)
        client = gspread.authorize(creds)
        sheet = client.open_by_key(sheet_id).get_worksheet(0)
        return sheet
    except Exception as e:
        st.error(f"Gagal Koneksi: {e}")
        return None

# ID Google Sheets kamu
ID_BARANG = "1qf8KmurJi8CbVmwsbRSDCWxir_Ejw2s9y9vGZTNmxAg"
ID_MEMBER = "1mMbvhMO3uQAjktAPeZ-G_s5IWBVkcuxg8YgPpSQjIgo"
ID_LAPORAN = "1KA5qK57aFiLkPIuFRbZD4g5PU_5nly-19Dup1DtdkqE"

st.set_page_config(page_title="KASIR DWI BANGKIT", layout="wide")
st.title("🏪 Kasir Dwi Bangkit Cloud")

def ambil_data(sheet_id):
    sh = koneksi_sheet(sheet_id)
    if sh:
        return pd.DataFrame(sh.get_all_records()), sh
    return pd.DataFrame(), None

df_barang, sh_barang = ambil_data(ID_BARANG)
df_member, _ = ambil_data(ID_MEMBER)

if 'keranjang' not in st.session_state:
    st.session_state.keranjang = []

col1, col2 = st.columns([1, 1.5])

with col1:
    st.subheader("🛒 Input Barang")
    member_list = ["Umum"]
    if not df_member.empty:
        member_list += df_member['Nama Member'].tolist()
    
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
        total = df_k['Total'].sum()
        st.header(f"TOTAL: Rp {total:,.0f}")
        
        if st.button("PROSES BAYAR"):
            with st.spinner("Menyimpan ke Google Sheets..."):
                sh_laporan = koneksi_sheet(ID_LAPORAN)
                tgl = datetime.now().strftime("%Y-%m-%d %H:%M")
                for r in st.session_state.keranjang:
                    sh_laporan.append_row([tgl, nama_member, r['Nama'], r['Qty'], r['Total']])
                st.success("Transaksi Berhasil!")
                st.session_state.keranjang = []
                st.rerun()
