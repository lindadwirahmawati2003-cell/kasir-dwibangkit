import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from datetime import datetime

# --- KUNCI GOOGLE LANGSUNG DI DALAM KODE (FIXED) ---
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

def koneksi_sheet(sheet_id):
    try:
        # Kunci ini langsung terbaca oleh aplikasi tanpa butuh menu Secrets
        info_kunci = {
            "type": "service_account",
            "project_id": "sapient-tractor-493502-m3",
            "private_key_id": "3ac90cb9cee2792da9fa0686abc8e68ded0474b9",
            "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCxl4x8f7Mw9x1C\nUifHYhPfUIN/OYiCT7ROUTEaSfg6isXcArRvDZNMFYdqh5cgO3+BM0a4JIwQG9ZW\nMmobAnaH+vWdR2juV+kFFZQXvUZdtQwpkeRNScyBNUgZ5PxejoXdI3jKpcH4rGTL\nWHIVEZvV62ndGs+e9kG94qxNGz5U5jN0i/gcYsCIIgnGDNxNmFaVijP/jIZfwxm7\n+7ATTATUxofbzz/xs9EddI7eaomjJazHUj/92lIhDApWsPxmYjiP9DAJHhVqxn27\nBXVjJlO0T5G10WWLW3WPC/tzdQR2j1Qwfv01yOJ9euWJVBLgobcHOpI3uWNvk0wS\vgM6OOqnAgMBAAECggEAAWa/BsNUWF3/Za4BbKMPxjmga3ADpFFQHuvNF/ZMUgDM\nC3fTI4ZXU8intOXHSvAa98BQZx3eI+3UTgHSHs66KwCGPn7m5shJqUpS3x9eqH1+\n9MmXEeLGDTOIJYwpmIDYjG2Zg42RAbOfHtlerRYroKGm7MYDGfjffRL0QRwUNdYj\nQK1qBQdEtI6gRs4KrCHFrzKcY9uh62IFrcO3Ez/Y+tzDkVx6p702km/VRUgomExI\n/zj+evz9GkZUQM9lECfcnmFtyH0vFds4EWS0lgIN7fU78rdXH6mZWFhj/0JmKSYs\nnplHu3Sdk2mFswaEkpMQI4C4hJjecWWfNN+ghs8soQKBgQDaYbOYarvQUJhdlK6f\n8ZWzZAxAME/j4IZnOg3jIjYujew88XnqSyT4pUSZ1Ad4Mv6sax8li6EVmjc8oXUX\n61hzb8cusHrt2NqTK7e3igce6KbhXgrpOgnZECpyMKQ2eNGHfETwNrj2nBO335bC\n4miInZmPxm0bQZs5+B3odHjMbQKBgQDQLxXWI9xkR/4WIKmY6hNGx40mEfvTWw7p\nfY/BAgZyx0Mqv1A8FYJi97Q0IpKCpOWVHLL3qV0dxnnhpvtRm/WV6EjtuiyPAsdS\nWpbf3TB+DbMPaaprRe3S+euM1ChbprvK6C7/DeHeSfJeC8n1N0LeyWFaVFL69w9A\nG8TALbZ+4wKBgQDGQjD0TOIZqzHIs7UdjAwmgswEclf1P9+FU9VLwcGC3mH8qhXO\nnuU3lVtVC+pWVcGZ5Tf9G7M7fd9Rx/Pr7LjRtCKvCHYJc8KTvO59cx7jTPNBUhjZN\nqt1J7T070iEjOuiuoglMM8IUUXotUpXic/4HGV1ShAiF2Df+lt1ALo2EuQKBgAt9\nXcYoyoQaWRKdkN6opJG2d7rPKUfb8bG/RUzQsMxq5PEaB/KY+U4+/4oVEmL1eNpG\n8DWs+j+ncZibn6k8Y0x3unasXMMz0w5fg44tZfy/As/p9AbhoCORuYdXOjb8t8aW\nE+ntuTaMfDzmh6np993V3XKfzsidFBFktvIoU7cjAoGBAL06A5WntLR4faAAH7cc\nU5Fr8APmp7oaBX66OCgZM4ngbFCidPKg1ETGejxQdmesSSsztXTRZdVgaivsthNQ\n/YI4CGYHcxB18AREPmifVV8b0SGAYv9neniFXmH2Z0x9dkamUXJVim6LcAjAG3bi\nQivQghjYJmIpKagrPSrSz3ac\n-----END PRIVATE KEY-----\n",
            "client_email": "kasir-dwibangkit@sapient-tractor-493502-m3.iam.gserviceaccount.com",
            "client_id": "112447339735180598158",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/kasir-dwibangkit%40sapient-tractor-493502-m3.iam.gserviceaccount.com",
            "universe_domain": "googleapis.com"
        }
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

# Ambil data dari Sheets
def ambil_data(sheet_id):
    sh = koneksi_sheet(sheet_id)
    if sh:
        try:
            data = sh.get_all_records()
            return pd.DataFrame(data), sh
        except:
            return pd.DataFrame(), None
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
        # Cek apakah kolom 'Nama Member' ada
        cols_m = [str(c) for c in df_member.columns]
        if 'Nama Member' in cols_m:
            member_list += df_member['Nama Member'].tolist()
    
    nama_member = st.selectbox("Pilih Member", member_list)
    barcode = st.text_input("Scan Barcode")
    
    if barcode:
        if not df_barang.empty:
            # Pastikan kolom 'Barcode' ada
            cols_b = [str(c) for c in df_barang.columns]
            if 'Barcode' in cols_b:
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
            else:
                st.error("Kolom 'Barcode' tidak ditemukan di Sheets Barang")
        else:
            st.error("Data barang di Google Sheets kosong")

with col2:
    st.subheader("📋 Keranjang")
    if st.session_state.keranjang:
        df_k = pd.DataFrame(st.session_state.keranjang)
        st.table(df_k)
        total = df_k['Total'].sum()
        st.header(f"TOTAL: Rp {total:,.0f}")
        
        if st.button("PROSES BAYAR"):
            with st.spinner("Menyimpan..."):
                sh_laporan = koneksi_sheet(ID_LAPORAN)
                tgl = datetime.now().strftime("%Y-%m-%d %H:%M")
                for r in st.session_state.keranjang:
                    sh_laporan.append_row([tgl, nama_member, r['Nama'], r['Qty'], r['Total']])
                st.success("Transaksi Berhasil!")
                st.session_state.keranjang = []
                st.rerun()
    else:
        st.write("Keranjang kosong")

# Panel Stok di bawah
st.divider()
if not df_barang.empty:
    with st.expander("🔍 Lihat Stok Barang"):
        st.dataframe(df_barang)
