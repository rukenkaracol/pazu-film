import streamlit as st
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
import os

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Pazu - Film Günlüğümüz", page_icon="🐾")

# --- FONKSİYONLAR ---
def watchlist_cek(kullanici_adi):
    url = f"https://letterboxd.com/{kullanici_adi}/watchlist/"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            filmler = soup.find_all('img', class_='image')
            return set([film['alt'] for film in filmler if 'alt' in film.attrs])
        return set()
    except:
        return set()

def izlenenleri_yukle():
    if os.path.exists("pazu_gecmis.csv"):
        return pd.read_csv("pazu_gecmis.csv")
    return pd.DataFrame(columns=["Film Adı", "İzlenme Tarihi"])

# --- ARAYÜZ ---
st.title("🐾 Pazu")

tab1, tab2 = st.tabs(["🍿 Film Eşleştir", "📜 İzleme Geçmişimiz"])

with tab1:
    st.subheader("Ortak Listeyi Bul")
    col1, col2 = st.columns(2)
    with col1:
        u1 = st.text_input("Senin Kullanıcı Adın", "rukenk")
    with col2:
        u2 = st.text_input("Onun Kullanıcı Adı", "ciban_salata")

    if st.button("Filmleri Eşleştir"):
        with st.spinner("Pazu listeleri kokluyor..."):
            l1 = watchlist_cek(u1)
            l2 = watchlist_cek(u2)
            gecmis_df = izlenenleri_yukle()
            izlenen_isimler = set(gecmis_df["Film Adı"].tolist())
            
            ortak = l1.intersection(l2)
            izlenmemis_ortak = sorted([f for f in ortak if f not in izlenen_isimler])
        
        if izlenmemis_ortak:
            st.success(f"{len(izlenmemis_ortak)} ortak film bulundu!")
            for film in izlenmemis_ortak:
                c1, c2 = st.columns([3, 1])
                c1.write(f"🎬 {film}")
                # Her buton için eşsiz bir anahtar (key) şart
                if c2.button("İzledik ✅", key=f"btn_{film}"):
                    yeni_kayit = pd.DataFrame({
                        "Film Adı": [film], 
                        "İzlenme Tarihi": [datetime.now().strftime("%d.%m.%Y %H:%M")]
                    })
                    gecmis_df = pd.concat([gecmis_df, yeni_kayit], ignore_index=True)
                    gecmis_df.to_csv("pazu_gecmis.csv", index=False, encoding="utf-8-sig")
                    st.rerun()
        else:
            st.info("İzlenecek yeni bir ortak film bulunamadı.")

with tab2:
    st.subheader("Birlikte Neler İzledik?")
    # Sekmeye tıklandığında dosyayı tazeleyerek oku
    gecmis_goster = izlenenleri_yukle()
    if not gecmis_goster.empty:
        # En son izleneni en başa alarak tabloyu göster
        st.dataframe(gecmis_goster.iloc[::-1], use_container_width=True, hide_index=True)
    else:
        st.write("Henüz bir film kaydı yok. 🎥")