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
        return client.open_by_key(sheet_id).get_worksheet(0)
    except Exception as e:
        st.error(f"Gagal akses Sheet: {e}")
        return None

# ID Google Sheets Linda
ID_BARANG = "1qf8KmurJi8CbVmwsbRSDCWxir_Ejw2s9y9vGZTNmxAg"
ID_MEMBER = "1mMbvhMO3uQAjktAPeZ-G_s5IWBVkcuxg8YgPpSQjIgo"
ID_LAPORAN = "1KA5qK57aFiLkPIuFRbZD4g5PU_5nly-19Dup1DtdkqE"

st.set_page_config(page_title="KASIR DWI BANGKIT", layout="wide")
st.title("🏪 Kasir Dwi Bangkit Cloud")

sh_barang = koneksi_sheet(ID_BARANG)
sh_member = koneksi_sheet(ID_MEMBER)

if sh_barang and sh_member:
    # Membaca data member
    df_member = pd.DataFrame(sh_member.get_all_records())
    df_barang = pd.DataFrame(sh_barang.get_all_records())
    
    if 'keranjang' not in st.session_state:
        st.session_state.keranjang = []

    col1, col2 = st.columns([1, 1.5])

    with col1:
        st.subheader("👤 Identitas Pelanggan")
        status = st.radio("Pilih Status:", ["Umum", "Member Terdaftar", "Daftar Baru"], horizontal=True)
        
        nama_pelanggan = "Umum"
        
        if status == "Member Terdaftar":
            if not df_member.empty:
                # FITUR CARI: Menggunakan Selectbox dengan fitur search bawaan Streamlit
                col_nama = df_member.columns[0]
                list_nama = df_member[col_nama].tolist()
                
                # Linda tinggal ketik nama di kotak ini untuk mencari
                nama_pelanggan = st.selectbox("🔎 Ketik/Cari Nama Member:", list_nama, index=0)
                
                # Menampilkan info No WA di bawahnya sebagai konfirmasi
                info_member = df_member[df_member[col_nama] == nama_pelanggan].iloc[0]
                st.caption(f"📱 No WA: {info_member.iloc[1]}")
            else:
                st.warning("Data member kosong.")
        
        elif status == "Daftar Baru":
            nama_input = st.text_input("Nama Lengkap")
            wa_input = st.text_input("Nomor WA")
            if st.button("💾 Simpan Member Baru"):
                if nama_input and wa_input:
                    sh_member.append_row([nama_input, wa_input])
                    st.success(f"Member {nama_input} Berhasil Terdaftar!")
                    st.rerun()
            nama_pelanggan = nama_input if nama_input else "Umum"
        
        else:
            nama_pelanggan = st.text_input("Nama Pelanggan Umum:", "Umum")

        st.divider()
        st.subheader("🛒 Scan Barang")
        barcode = st.text_input("Scan Barcode", key="scanner")
        
        if barcode:
            col_bc = df_barang.columns[0]
            hasil = df_barang[df_barang[col_bc].astype(str) == barcode]
            
            if not hasil.empty:
                item = hasil.iloc[0]
                st.success(f"✅ {item.iloc[1]}") 
                
                pilih = st.radio("Pilih Satuan:", ["Ecer/Pcs", "Grosir", "Dus"], horizontal=True)
                
                if pilih == "Ecer/Pcs": harga = item['Ecer']
                elif pilih == "Grosir": harga = item['Grosir']
                else: harga = item['Dus']
                
                harga_fix = int(harga)
                st.write(f"Harga: **Rp {harga_fix:,.0f}**")
                qty = st.number_input("Qty", min_value=1, value=1)
                
                if st.button("➕ Tambah"):
                    st.session_state.keranjang.append({
                        "Nama": str(item.iloc[1]), "Satuan": pilih,
                        "Harga": harga_fix, "Qty": int(qty), "Total": harga_fix * qty
                    })
                    st.rerun()

    with col2:
        st.subheader("📋 Daftar Belanja")
        if st.session_state.keranjang:
            df_k = pd.DataFrame(st.session_state.keranjang)
            st.table(df_k[["Nama", "Satuan", "Harga", "Qty", "Total"]])
            total = int(df_k['Total'].sum())
            st.header(f"TOTAL: Rp {total:,.0f}")
            
            if st.button("💾 SELESAI & SIMPAN"):
                try:
                    sh_lap = koneksi_sheet(ID_LAPORAN)
                    waktu = datetime.now().strftime("%Y-%m-%d %H:%M")
                    # Disimpan ke file Laporan: Waktu, Nama Pelanggan, Total
                    sh_lap.append_row([waktu, nama_pelanggan, float(total)])
                    st.balloons()
                    st.success(f"Transaksi {nama_pelanggan} telah tersimpan di Laporan!")
                    st.session_state.keranjang = []
                    st.rerun()
                except Exception as e:
                    st.error(f"Gagal simpan ke Laporan: {e}")
            
            if st.button("🗑️ Reset"):
                st.session_state.keranjang = []
                st.rerun()
        else:
            st.info("Belum ada barang di keranjang.")

    st.divider()
    with st.expander("🔍 Cek Stok Gudang"):
        st.dataframe(df_barang)
else:
    st.info("🔄 Menghubungkan...")
