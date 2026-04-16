import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from datetime import datetime

# --- SETTING KONEKSI ---
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

def koneksi_sheet(sheet_id):
    try:
        info = dict(st.secrets["gcp_service_account"])
        info["private_key"] = info["private_key"].replace("\\n", "\n")
        creds = ServiceAccountCredentials.from_json_keyfile_dict(info, SCOPE)
        client = gspread.authorize(creds)
        # Ambil sheet pertama
        return client.open_by_key(sheet_id).get_worksheet(0)
    except Exception as e:
        # Menampilkan pesan error yang lebih jelas di aplikasi
        st.error(f"Gagal akses Sheet ID {sheet_id[:5]}... : {e}")
        return None

# ID Link Google Sheets Linda
ID_BARANG = "1qf8KmurJi8CbVmwsbRSDCWxir_Ejw2s9y9vGZTNmxAg"
ID_MEMBER = "1mMbvhMO3uQAjktAPeZ-G_s5IWBVkcuxg8YgPpSQjIgo"
ID_LAPORAN = "1KA5qK57aFiLkPIuFRbZD4g5PU_5nly-19Dup1DtdkqE"

st.set_page_config(page_title="KASIR DWI BANGKIT", layout="wide")
st.title("🏪 Kasir Dwi Bangkit Cloud")

# Koneksi Sheets
sh_barang = koneksi_sheet(ID_BARANG)
sh_member = koneksi_sheet(ID_MEMBER)

if sh_barang and sh_member:
    # Ambil data member terbaru
    data_member = sh_member.get_all_records()
    df_member = pd.DataFrame(data_member)
    df_barang = pd.DataFrame(sh_barang.get_all_records())
    
    if 'keranjang' not in st.session_state:
        st.session_state.keranjang = []

    col1, col2 = st.columns([1, 1.5])

    with col1:
        st.subheader("👤 Identitas Pelanggan")
        
        # Pilihan tipe pelanggan
        tipe_p = st.radio("Tipe Pelanggan:", ["Member Terdaftar", "Umum / Daftar Baru"], horizontal=True)
        
        nama_pelanggan = "Umum"
        is_member = False

        if tipe_p == "Member Terdaftar":
            if not df_member.empty and 'Nama Member' in df_member.columns:
                list_m = df_member['Nama Member'].tolist()
                nama_pelanggan = st.selectbox("Pilih Nama Member:", list_m)
                is_member = True
            else:
                st.warning("Data member belum ada di Sheets.")
        else:
            nama_pelanggan = st.text_input("Nama Pelanggan Baru / Umum:", "Umum")
            daftar_baru = st.checkbox("Daftarkan sebagai member baru?")
            if daftar_baru:
                no_hp = st.text_input("Masukkan Nomor HP:")
                if st.button("✅ Simpan Member Baru"):
                    if nama_pelanggan != "Umum" and no_hp:
                        sh_member.append_row([nama_pelanggan, no_hp])
                        st.success(f"Member {nama_pelanggan} berhasil didaftarkan!")
                        st.rerun()
                    else:
                        st.error("Nama dan No HP harus diisi!")

        st.divider()
        st.subheader("🛒 Input Barang")
        barcode = st.text_input("Scan Barcode", key="barcode_scan")
        
        if barcode:
            hasil = df_barang[df_barang['Barcode'].astype(str) == barcode]
            if not hasil.empty:
                item = hasil.iloc[0]
                st.success(f"📦 {item['Nama']}")
                
                opsi_s = ["Ecer/Pcs", "Grosir", "Dus"]
                pilih_s = st.radio("Pilih Jenis:", opsi_s, horizontal=True)
                
                # Penentuan Harga
                if pilih_s == "Ecer/Pcs":
                    harga_raw = item['Member'] if is_member else item['Ecer']
                elif pilih_s == "Grosir":
                    harga_raw = item['Grosir']
                else:
                    harga_raw = item['Dus']
                
                harga_f = int(harga_raw)
                st.info(f"Harga: **Rp {harga_f:,.0f}**")
                qty = st.number_input("Jumlah", min_value=1, value=1)
                
                if st.button("➕ Tambah"):
                    st.session_state.keranjang.append({
                        "Nama": str(item['Nama']), "Satuan": pilih_s,
                        "Harga": harga_f, "Qty": int(qty), "Total": int(harga_f * qty)
                    })
                    st.rerun()

    with col2:
        st.subheader("📋 Keranjang Belanja")
        if st.session_state.keranjang:
            df_k = pd.DataFrame(st.session_state.keranjang)
            st.table(df_k[["Nama", "Satuan", "Harga", "Qty", "Total"]])
            total_t = int(df_k['Total'].sum())
            st.header(f"TOTAL AKHIR: Rp {total_t:,.0f}")
            
            if st.button("💾 SIMPAN TRANSAKSI"):
                try:
                    sh_lap = koneksi_sheet(ID_LAPORAN)
                    waktu = datetime.now().strftime("%Y-%m-%d %H:%M")
                    # Simpan ke Laporan: Tanggal, Nama, Total
                    sh_lap.append_row([waktu, nama_pelanggan, float(total_t)])
                    st.balloons()
                    st.success("Tersimpan!")
                    st.session_state.keranjang = []
                    st.rerun()
                except Exception as e:
                    st.error(f"Gagal Simpan: {e}")

            if st.button("🗑️ Kosongkan"):
                st.session_state.keranjang = []
                st.rerun()
else:
    st.warning("⚠️ Periksa koneksi atau izin Share pada Google Sheets kamu.")
