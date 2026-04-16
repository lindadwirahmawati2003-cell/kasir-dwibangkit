import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from datetime import datetime

# --- KONEKSI GOOGLE SHEETS (VERSI FIX 100%) ---
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

def koneksi_sheet(sheet_id):
    try:
        # Kunci ini sudah dibersihkan total dari karakter yang bikin error padding
        key_raw = "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCxl4x8f7Mw9x1CUifHYhPfUIN/OYiCT7ROUTEaSfg6isXcArRvDZNMFYdqh5cgO3+BM0a4JIwQG9ZWMmobAnaH+vWdR2juV+kFFZQXvUZdtQwpkeRNScyBNUgZ5PxejoXdI3jKpcH4rGTLWHIVEZvV62ndGs+e9kG94qxNGz5U5jN0i/gcYsCIIgnGDNxNmFaVijP/jIZfwxm7+7ATTATUxofbzz/xs9EddI7eaomjJazHUj/92lIhDApWsPxmYjiP9DAJHhVqxn27BXVjJlO0T5G10WWLW3WPC/tzdQR2j1Qwfv01yOJ9euWJVBLgobcHOpI3uWNvk0wSvgM6OOqnAgMBAAECggEAAWa/BsNUWF3/Za4BbKMPxjmga3ADpFFQHuvNF/ZMUgDMC3fTI4ZXU8intOXHSvAa98BQZx3eI+3UTgHSHs66KwCGPn7m5shJqUpS3x9eqH1+9MmXEeLGDTOIJYwpmIDYjG2Zg42RAbOfHtlerRYroKGm7MYDGfjffRL0QRwUNdYjQK1qBQdEtI6gRs4KrCHFrzKcY9uh62IFrcO3Ez/Y+tzDkVx6p702km/VRUgomExI/zj+evz9GkZUQM9lECfcnmFtyH0vFds4EWS0lgIN7fU78rdXH6mZWFhj/0JmKSYsnplHu3Sdk2mFswaEkpMQI4C4hJjecWWfNN+ghs8soQKBgQDaYbOYarvQUJhdlK6f8ZWzZAxAME/j4IZnOg3jIjYujew88XnqSyT4pUSZ1Ad4Mv6sax8li6EVmjc8oXUX61hzb8cusHrt2NqTK7e3igce6KbhXgrpOgnZECpyMKQ2eNGHfETwNrj2nBO335bC4miInZmPxm0bQZs5+B3odHjMbQKBgQDQLxXWI9xkR/4WIKmY6hNGx40mEfvTWw7pfY/BAgZyx0Mqv1A8FYJi97Q0IpKCpOWVHLL3qV0dxnnhpvtRm/WV6EjtuiyPAsdSWpbf3TB+DbMPaaprRe3S+euM1ChbprvK6C7/DeHeSfJeC8n1N0LeyWFaVFL69w9AG8TALbZ+4wKBgQDGQjD0TOIZqzHIs7UdjAwmgswEclf1P9+FU9VLwcGC3mH8qhXOuU3lVtVC+pWVcGZ5Tf9G7M7fd9Rx/Pr7LjRtCKvCHYJc8KTvO59cx7jTPNBUhjZNqt1J7T070iEjOuiuoglMM8IUUXotUpXic/4HGV1ShAiF2Df+lt1ALo2EuQKBgAt9XcYoyoQaWRKdkN6opJG2d7rPKUfb8bG/RUzQsMxq5PEaB/KY+U4+/4oVEmL1eNpG8DWs+j+ncZibn6k8Y0x3unasXMMz0w5fg44tZfy/As/p9AbhoCORuYdXOjb8t8aWE+ntuTaMfDzmh6np993V3XKfzsidFBFktvIoU7cjAoGBAL06A5WntLR4faAAH7ccU5Fr8APmp7oaBX66OCgZM4ngbFCidPKg1ETGejxQdmesSSsztXTRZdVgaivsthNQ/YI4CGYHcxB18AREPmifVV8b0SGAYv9neniFXmH2Z0x9dkamUXJVim6LcAjAG3biQivQghjYJmIpKagrPSrSz3ac\n-----END PRIVATE KEY-----\n"
        
        info_kunci = {
            "type": "service_account",
            "project_id": "sapient-tractor-493502-m3",
            "private_key_id": "3ac90cb9cee2792da9fa0686abc8e68ded0474b9",
            "private_key": key_raw,
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
        st.error(f"Koneksi Gagal: {e}")
        return None

# ID Sheets (Ganti jika ID-nya berbeda)
ID_BARANG = "1qf8KmurJi8CbVmwsbRSDCWxir_Ejw2s9y9vGZTNmxAg"
ID_MEMBER = "1mMbvhMO3uQAjktAPeZ-G_s5IWBVkcuxg8YgPpSQjIgo"
ID_LAPORAN = "1KA5qK57aFiLkPIuFRbZD4g5PU_5nly-19Dup1DtdkqE"

st.set_page_config(page_title="KASIR DWI BANGKIT", layout="wide")
st.title("🏪 Kasir Dwi Bangkit Cloud")

def ambil_data(sheet_id):
    sh = koneksi_sheet(sheet_id)
    if sh:
        try:
            data = sh.get_all_records()
            return pd.DataFrame(data)
        except: return pd.DataFrame()
    return pd.DataFrame()

# Load Data
df_barang = ambil_data(ID_BARANG)
df_member = ambil_data(ID_MEMBER)

if 'keranjang' not in st.session_state:
    st.session_state.keranjang = []

# --- Tampilan Utama ---
col1, col2 = st.columns([1, 1.5])

with col1:
    st.subheader("🛒 Input Barang")
    member_list = ["Umum"]
    if not df_member.empty and 'Nama Member' in df_member.columns:
        member_list += df_member['Nama Member'].tolist()
    
    nama_member = st.selectbox("Pilih Member", member_list)
    barcode = st.text_input("Scan Barcode")
    
    if barcode:
        if not df_barang.empty:
            # Pastikan kolom 'Barcode' ada (huruf B besar sesuai foto Sheets)
            if 'Barcode' in df_barang.columns:
                hasil = df_barang[df_barang['Barcode'].astype(str) == barcode]
                if not hasil.empty:
                    item = hasil.iloc[0]
                    st.success(f"Ditemukan: {item['Nama']}")
                    qty = st.number_input("Jumlah Beli", min_value=1, value=1)
                    if st.button("Tambah"):
                        harga = item['Member'] if nama_member != "Umum" else item['Ecer']
                        st.session_state.keranjang.append({
                            "Nama": item['Nama'], "Harga": harga, "Qty": qty, "Total": harga * qty
                        })
                        st.rerun()
                else: st.error("Barang tidak terdaftar")
            else: st.error("Kolom 'Barcode' tidak ditemukan di Sheets")
        else: st.error("Tabel Barang tidak terbaca")

with col2:
    st.subheader("📋 Keranjang")
    if st.session_state.keranjang:
        df_k = pd.DataFrame(st.session_state.keranjang)
        st.table(df_k)
        total = df_k['Total'].sum()
        st.header(f"TOTAL: Rp {total:,.0f}")
        if st.button("PROSES SIMPAN"):
            sh_lap = koneksi_sheet(ID_LAPORAN)
            if sh_lap:
                tgl = datetime.now().strftime("%Y-%m-%d %H:%M")
                for r in st.session_state.keranjang:
                    sh_lap.append_row([tgl, nama_member, r['Nama'], r['Qty'], r['Total']])
                st.success("Tersimpan!")
                st.session_state.keranjang = []
                st.rerun()
    else: st.info("Keranjang kosong")

# Tabel Stok di bawah
st.divider()
if not df_barang.empty:
    with st.expander("🔍 Lihat Semua Stok"):
        st.dataframe(df_barang)
