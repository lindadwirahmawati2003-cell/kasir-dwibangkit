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
        st.error(f"Koneksi Gagal: {e}")
        return None

# ID Link Google Sheets Linda
ID_BARANG = "1qf8KmurJi8CbVmwsbRSDCWxir_Ejw2s9y9vGZTNmxAg"
ID_MEMBER = "1mMbvhMO3uQAjktAPeZ-G_s5IWBVkcuxg8YgPpSQjIgo"
ID_LAPORAN = "1KA5qK57aFiLkPIuFRbZD4g5PU_5nly-19Dup1DtdkqE"

st.set_page_config(page_title="KASIR DWI BANGKIT", layout="wide")
st.title("🏪 Kasir Dwi Bangkit Cloud")

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
        member_list = ["Umum"]
        if not df_member.empty and 'Nama Member' in df_member.columns:
            member_list += df_member['Nama Member'].tolist()
        
        nama_member = st.selectbox("Pilih Member", member_list)
        barcode = st.text_input("Scan Barcode", key="barcode_input")
        
        if barcode:
            # Cari barang berdasarkan Barcode
            hasil = df_barang[df_barang['Barcode'].astype(str) == barcode]
            
            if not hasil.empty:
                item = hasil.iloc[0]
                st.success(f"📦 {item['Nama']}")
                
                # --- FITUR PILIH SATUAN & HARGA ---
                opsi_satuan = ["Ecer/Pcs", "Grosir", "Dus"]
                pilihan_satuan = st.radio("Pilih Jenis Pembelian:", opsi_satuan, horizontal=True)
                
                # Logika Penentuan Harga
                if pilihan_satuan == "Ecer/Pcs":
                    # Jika member, pakai harga Member, jika tidak pakai Ecer
                    harga_final = item['Member'] if nama_member != "Umum" else item['Ecer']
                elif pilihan_satuan == "Grosir":
                    harga_final = item['Grosir']
                else: # Dus
                    harga_final = item['Dus']
                
                st.info(f"Harga per {pilihan_satuan}: **Rp {harga_final:,.0f}**")
                
                qty = st.number_input("Jumlah yang dibeli", min_value=1, value=1)
                
                if st.button("➕ Tambahkan"):
                    st.session_state.keranjang.append({
                        "Nama": item['Nama'],
                        "Satuan": pilihan_satuan,
                        "Harga": harga_final,
                        "Qty": qty,
                        "Total": harga_final * qty
                    })
                    st.rerun()
            else:
                st.error("Barcode tidak terdaftar!")

    with col2:
        st.subheader("📋 Keranjang")
        if st.session_state.keranjang:
            df_k = pd.DataFrame(st.session_state.keranjang)
            st.table(df_k[["Nama", "Satuan", "Harga", "Qty", "Total"]])
            
            total_akhir = df_k['Total'].sum()
            st.header(f"TOTAL: Rp {total_akhir:,.0f}")
            
            if st.button("💾 SIMPAN TRANSAKSI"):
                try:
                    sh_lap = koneksi_sheet(ID_LAPORAN)
                    waktu = datetime.now().strftime("%d/%m/%Y %H:%M")
                    for r in st.session_state.keranjang:
                        # Mengirim data ke laporan: Tgl, Member, Nama, Satuan, Qty, Harga, Total
                        sh_lap.append_row([waktu, nama_member, r['Nama'], r['Satuan'], r['Qty'], r['Harga'], r['Total']])
                    
                    st.balloons()
                    st.success("Berhasil disimpan ke Google Sheets!")
                    st.session_state.keranjang = []
                    st.rerun()
                except Exception as e:
                    st.error(f"Gagal menyimpan: {e}")

            if st.button("🗑️ Hapus Semua"):
                st.session_state.keranjang = []
                st.rerun()
        else:
            st.info("Belum ada barang di keranjang.")

    st.divider()
    with st.expander("🔍 Lihat Stok Gudang"):
        st.dataframe(df_barang)
