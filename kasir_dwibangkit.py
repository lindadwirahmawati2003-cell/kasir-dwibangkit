import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from datetime import datetime
import time

# --- SETTING KONEKSI ---
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Fungsi koneksi yang lebih stabil
def koneksi_sheet(sheet_id):
    try:
        info = dict(st.secrets["gcp_service_account"])
        info["private_key"] = info["private_key"].replace("\\n", "\n")
        creds = ServiceAccountCredentials.from_json_keyfile_dict(info, SCOPE)
        client = gspread.authorize(creds)
        return client.open_by_key(sheet_id).get_worksheet(0)
    except Exception as e:
        return None

# ID Google Sheets Linda (PASTIKAN ID INI TIDAK TERBALIK)
ID_BARANG = "1qf8KmurJi8CbVmwsbRSDCWxir_Ejw2s9y9vGZTNmxAg"
ID_MEMBER = "1mMbvhMO3uQAjktAPeZ-G_s5IWBVkcuxg8YgPpSQjIgo"
ID_LAPORAN = "1KA5qK57aFiLkPIuFRbZD4g5PU_5nly-19Dup1DtdkqE"

st.set_page_config(page_title="KASIR DWI BANGKIT", layout="wide")
st.title("🏪 Kasir Dwi Bangkit Cloud")

# --- FITUR HEMAT KUOTA (CACHE) ---
# Data hanya akan diambil dari Google setiap 5 menit sekali untuk hemat kuota
@st.cache_data(ttl=300) 
def ambil_data_gspread(sheet_id):
    sh = koneksi_sheet(sheet_id)
    if sh:
        return sh.get_all_records()
    return []

# Load Data dengan fitur hemat kuota
with st.spinner('Mengambil data...'):
    data_b = ambil_data_gspread(ID_BARANG)
    data_m = ambil_data_gspread(ID_MEMBER)
    
    df_barang = pd.DataFrame(data_b)
    df_member = pd.DataFrame(data_m)

if not df_barang.empty:
    if 'keranjang' not in st.session_state:
        st.session_state.keranjang = []

    col1, col2 = st.columns([1, 1.5])

    with col1:
        st.subheader("👤 Pelanggan")
        status = st.radio("Status:", ["Umum", "Member Terdaftar", "Daftar Baru"], horizontal=True)
        
        nama_pelanggan = "Umum"
        
        if status == "Member Terdaftar":
            if not df_member.empty:
                col_nama = df_member.columns[0]
                list_nama = df_member[col_nama].tolist()
                nama_pelanggan = st.selectbox("🔎 Cari Nama Member:", list_nama)
                
                # Konfirmasi No WA (ambil dari baris member yang dipilih)
                idx = list_nama.index(nama_pelanggan)
                st.caption(f"📱 No WA: {df_member.iloc[idx, 1]}")
            else:
                st.warning("File member kosong.")
        
        elif status == "Daftar Baru":
            nama_in = st.text_input("Nama Baru")
            wa_in = st.text_input("No WA")
            if st.button("✅ Daftar"):
                sh_m = koneksi_sheet(ID_MEMBER)
                if sh_m:
                    sh_m.append_row([nama_in, wa_in])
                    st.success("Berhasil! Silakan klik 'Clear Cache' di pojok kanan atas jika nama belum muncul.")
                    st.cache_data.clear() # Paksa update data
                    st.rerun()
            nama_pelanggan = nama_in if nama_in else "Umum"
        
        st.divider()
        st.subheader("🛒 Scan")
        barcode = st.text_input("Barcode", key="scan")
        
        if barcode:
            c_bc = df_barang.columns[0]
            hasil = df_barang[df_barang[c_bc].astype(str) == barcode]
            if not hasil.empty:
                item = hasil.iloc[0]
                st.success(f"✅ {item.iloc[1]}")
                pilih = st.radio("Satuan:", ["Ecer/Pcs", "Grosir", "Dus"], horizontal=True)
                
                # Ambil harga
                if pilih == "Ecer/Pcs": harga = item['Ecer']
                elif pilih == "Grosir": harga = item['Grosir']
                else: harga = item['Dus']
                
                st.write(f"Harga: **Rp {int(harga):,.0f}**")
                qty = st.number_input("Qty", min_value=1, value=1)
                
                if st.button("➕ Tambah"):
                    st.session_state.keranjang.append({
                        "Nama": str(item.iloc[1]), "Satuan": pilih,
                        "Harga": int(harga), "Qty": int(qty), "Total": int(harga * qty)
                    })
                    st.rerun()

    with col2:
        st.subheader("📋 Keranjang")
        if st.session_state.keranjang:
            df_k = pd.DataFrame(st.session_state.keranjang)
            st.table(df_k[["Nama", "Satuan", "Harga", "Qty", "Total"]])
            total = int(df_k['Total'].sum())
            st.header(f"TOTAL: Rp {total:,.0f}")
            
            if st.button("💾 SIMPAN KE LAPORAN"):
                sh_lap = koneksi_sheet(ID_LAPORAN)
                if sh_lap:
                    waktu = datetime.now().strftime("%Y-%m-%d %H:%M")
                    sh_lap.append_row([waktu, nama_pelanggan, float(total)])
                    st.balloons()
                    st.session_state.keranjang = []
                    st.rerun()
            
            if st.button("🗑️ Reset"):
                st.session_state.keranjang = []
                st.rerun()

    st.divider()
    with st.expander("🔍 Stok"):
        st.dataframe(df_barang)
else:
    st.error("Gagal mengambil data. Tunggu 1 menit lalu tekan F5 (Refresh) karena batas kuota Google tercapai.")
