import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from datetime import datetime
import streamlit.components.v1 as components

# --- SETTING KONEKSI ---
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

def koneksi_sheet(sheet_id):
    try:
        info = dict(st.secrets["gcp_service_account"])
        info["private_key"] = info["private_key"].replace("\\n", "\n")
        creds = ServiceAccountCredentials.from_json_keyfile_dict(info, SCOPE)
        client = gspread.authorize(creds)
        return client.open_by_key(sheet_id).get_worksheet(0)
    except:
        return None

ID_BARANG = "1qf8KmurJi8CbVmwsbRSDCWxir_Ejw2s9y9vGZTNmxAg"
ID_MEMBER = "1mMbvhMO3uQAjktAPeZ-G_s5IWBVkcuxg8YgPpSQjIgo"
ID_LAPORAN = "1KA5qK57aFiLkPIuFRbZD4g5PU_5nly-19Dup1DtdkqE"

st.set_page_config(page_title="KASIR DWI BANGKIT", layout="wide")

def cetak_halaman():
    components.html("<script>window.print();</script>", height=0)

st.title("🏪 Kasir Dwi Bangkit Cloud")

@st.cache_data(ttl=60)
def ambil_data(sheet_id):
    sh = koneksi_sheet(sheet_id)
    return sh.get_all_records() if sh else []

data_b = ambil_data(ID_BARANG)
data_m = ambil_data(ID_MEMBER)
df_barang = pd.DataFrame(data_b)
df_member = pd.DataFrame(data_m)

if 'keranjang' not in st.session_state:
    st.session_state.keranjang = []
if 'nota_siap' not in st.session_state:
    st.session_state.nota_siap = False

col1, col2 = st.columns([1, 1.2])

with col1:
    st.subheader("👤 Pelanggan")
    status = st.radio("Status:", ["Umum", "Member Terdaftar", "Daftar Baru"], horizontal=True)
    nama_p = "Umum"
    tipe_harga_otomatis = "Ecer" # Default untuk Umum
    
    if status == "Member Terdaftar" and not df_member.empty:
        col_nm = df_member.columns[0]
        nama_p = st.selectbox("Cari Member:", df_member[col_nm].tolist())
        tipe_harga_otomatis = "Member" # Otomatis Member
    elif status == "Daftar Baru":
        n_in = st.text_input("Nama")
        w_in = st.text_input("WA")
        if st.button("Daftar"):
            koneksi_sheet(ID_MEMBER).append_row([n_in, w_in])
            st.success("Berhasil!")
            st.cache_data.clear()
            st.rerun()
        nama_p = n_in if n_in else "Umum"

    st.divider()
    st.subheader("🛒 Scan Barang")
    bc = st.text_input("Scan Barcode", key="scan")
    if bc:
        col_bc = df_barang.columns[0]
        hasil = df_barang[df_barang[col_bc].astype(str) == bc]
        if not hasil.empty:
            item = hasil.iloc[0]
            st.success(f"✅ {item['Nama']}")
            
            # Pilihan Satuan: Jika Dus diklik, harga dus berlaku untuk semua.
            # Jika tidak, maka mengikuti tipe_harga_otomatis (Member/Ecer)
            opsi_satuan = [tipe_harga_otomatis, "Dus"]
            sat = st.radio("Pilih Satuan:", opsi_satuan, horizontal=True)
            
            # Ambil Nilai Harga dari Sheet
            hrg = item[sat]
            
            # Bersihkan format Rp jika ada
            if isinstance(hrg, str):
                hrg_fix = int(hrg.replace('Rp', '').replace(',', '').split('.')[0])
            else:
                hrg_fix = int(hrg)

            st.info(f"Harga {sat}: **Rp {hrg_fix:,.0f}**")
            qty = st.number_input("Qty", min_value=1, value=1)
            
            if st.button("➕ Tambah ke Keranjang"):
                st.session_state.keranjang.append({
                    "Nama": item['Nama'], 
                    "Satuan": sat, 
                    "Harga": hrg_fix, 
                    "Qty": int(qty), 
                    "Total": int(hrg_fix * qty)
                })
                st.rerun()
        else:
            st.error("Barcode tidak ditemukan!")

with col2:
    st.subheader("📋 Keranjang")
    if st.session_state.keranjang:
        df_k = pd.DataFrame(st.session_state.keranjang)
        st.table(df_k[["Nama", "Satuan", "Harga", "Qty", "Total"]])
        total_akhir = int(df_k['Total'].sum())
        st.header(f"TOTAL: Rp {total_akhir:,.0f}")
        
        if st.button("💾 SIMPAN & CETAK"):
            sh_lap = koneksi_sheet(ID_LAPORAN)
            if sh_lap:
                waktu = datetime.now().strftime("%Y-%m-%d %H:%M")
                sh_lap.append_row([waktu, nama_p, float(total_akhir)])
                st.session_state.nota_siap = {
                    "waktu": waktu, "pelanggan": nama_p, "item": st.session_state.keranjang, "total": total_akhir
                }
                st.session_state.keranjang = []
                st.rerun()
    
    if st.button("🗑️ Kosongkan"):
        st.session_state.keranjang = []
        st.rerun()

# --- MODAL NOTA ---
if st.session_state.nota_siap:
    st.divider()
    nota = st.session_state.nota_siap
    nota_html = f"""
    <div style="font-family: monospace; width: 280px; padding: 10px; border: 1px solid #ddd; background: #fff; color: #000;">
        <center><strong>DWI BANGKIT</strong><br>---</center>
        Tgl: {nota['waktu']}<br>Plg: {nota['pelanggan']}<br>---<br>
    """
    for i in nota['item']:
        nota_html += f"{i['Nama']} ({i['Satuan']})<br>{i['Qty']} x {i['Harga']:,} = {i['Total']:,}<br>"
    
    nota_html += f"---<br><strong>TOTAL: Rp {nota['total']:,}</strong><br>---<br><center>Terima Kasih</center></div>"
    
    st.markdown(nota_html, unsafe_allow_html=True)
    if st.button("🖨️ Cetak Nota"): cetak_halaman()
    if st.button("❌ Tutup"): 
        st.session_state.nota_siap = False
        st.rerun()
