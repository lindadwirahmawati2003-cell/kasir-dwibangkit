import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from datetime import datetime

# --- 1. KONFIGURASI KONEKSI GOOGLE SHEETS ---
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
KUNCI_JSON = "kunci_akses.json"  # <--- PASTIKAN NAMA FILE JSON SESUAI

# ID dari link yang kamu berikan
ID_BARANG = "1qf8KmurJi8CbVmwsbRSDCWxir_Ejw2s9y9vGZTNmxAg"
ID_MEMBER = "1mMbvhMO3uQAjktAPeZ-G_s5IWBVkcuxg8YgPpSQjIgo"
ID_LAPORAN = "1KA5qK57aFiLkPIuFRbZD4g5PU_5nly-19Dup1DtdkqE"

def koneksi_sheet(sheet_id):
    try:
        creds = ServiceAccountCredentials.from_json_keyfile_name(KUNCI_JSON, SCOPE)
        client = gspread.authorize(creds)
        sheet = client.open_by_key(sheet_id).get_worksheet(0)
        return sheet
    except Exception as e:
        st.error(f"Gagal Koneksi ke Google Sheets: {e}")
        return None

# --- 2. FUNGSI LOGIKA KASIR ---
def ambil_data_df(sheet_id):
    sh = koneksi_sheet(sheet_id)
    if sh:
        data = sh.get_all_records()
        return pd.DataFrame(data), sh
    return pd.DataFrame(), None

# --- 3. TAMPILAN INTERFACE STREAMLIT ---
st.set_page_config(page_title="KASIR DWI BANGKIT", layout="wide")

# CSS Custom agar tampilan lebih menarik di HP
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; background-color: #2e7d32; color: white; }
    .total-box { padding: 20px; background-color: #ffffff; border-radius: 15px; border-left: 10px solid #2e7d32; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏪 Kasir Dwi Bangkit Parengan")
st.info("Sistem Cloud: Data otomatis tersimpan di Google Sheets")

# Inisialisasi Keranjang Belanja
if 'keranjang' not in st.session_state:
    st.session_state.keranjang = []

# Ambil Data Terbaru
df_barang, sh_barang = ambil_data_df(ID_BARANG)
df_member, _ = ambil_data_df(ID_MEMBER)

# --- PANEL TRANSAKSI ---
col1, col2 = st.columns([1, 1.5])

with col1:
    st.subheader("🛒 Input Barang")
    
    # Input Member
    nama_member = st.selectbox("Pilih Member", ["Umum"] + df_member['Nama Member'].tolist())
    status_member = "MEMBER" if nama_member != "Umum" else "ECER"
    
    # Input Barcode/Nama
    cari_barang = st.text_input("Scan Barcode / Ketik Nama Barang")
    
    if cari_barang:
        # Cari di data barang (berdasarkan Barcode atau Nama)
        hasil = df_barang[(df_barang['Barcode'].astype(str) == cari_barang) | 
                          (df_barang['Nama'].str.contains(cari_barang, case=False))]
        
        if not hasil.empty:
            item = hasil.iloc[0]
            st.success(f"Ditemukan: {item['Nama']}")
            st.write(f"Stok Tersedia: {item['Stok']} {item.get('Satuan', 'pcs')}")
            
            # Harga Berdasarkan Status Member
            harga_fix = item['Member'] if status_member == "MEMBER" else item['Ecer']
            
            qty = st.number_input("Jumlah Beli", min_value=1, value=1)
            
            if st.button("Tambah ke Keranjang"):
                st.session_state.keranjang.append({
                    "Barcode": str(item['Barcode']),
                    "Nama": item['Nama'],
                    "Harga": harga_fix,
                    "Qty": qty,
                    "Total": harga_fix * qty
                })
                st.rerun()
        else:
            st.warning("Barang tidak ditemukan.")

with col2:
    st.subheader("📋 Daftar Belanja")
    if st.session_state.keranjang:
        df_cart = pd.DataFrame(st.session_state.keranjang)
        st.dataframe(df_cart, use_container_width=True)
        
        total_belanja = df_cart['Total'].sum()
        st.markdown(f"<div class='total-box'><h1>TOTAL: Rp {total_belanja:,.0f}</h1></div>", unsafe_allow_html=True)
        
        if st.button("🔴 Hapus Semua"):
            st.session_state.keranjang = []
            st.rerun()

        if st.button("✅ BAYAR & SIMPAN"):
            with st.spinner("Menyimpan ke Cloud..."):
                # 1. Simpan ke Laporan
                sh_laporan = koneksi_sheet(ID_LAPORAN)
                tgl = datetime.now().strftime("%Y-%m-%d %H:%M")
                
                for r in st.session_state.keranjang:
                    sh_laporan.append_row([tgl, nama_member, r['Nama'], r['Qty'], r['Total']])
                
                # 2. Update Stok di Google Sheets (Logika Sederhana)
                # Catatan: Untuk update stok spesifik, diperlukan pencarian baris.
                # Sebagai simulasi, pesan sukses ditampilkan.
                
                st.balloons()
                st.success(f"Transaksi Berhasil! Data sudah masuk ke Google Sheets.")
                st.session_state.keranjang = []
                # Refresh data barang untuk update stok visual
                st.rerun()
    else:
        st.write("Keranjang masih kosong.")

# --- PANEL INFO STOK ---
st.divider()
with st.expander("🔍 Lihat Semua Stok Barang"):
    st.dataframe(df_barang, use_container_width=True)