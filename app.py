import streamlit as st
import cv2
import numpy as np
from PIL import Image
import os

# Setări Pagină
st.set_page_config(page_title="Photo Selector Pro", layout="wide")

# Funcție pentru calcularea clarității (Laplacian Variance)
def get_blur_score(image):
    img_array = np.array(image)
    gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    return cv2.Laplacian(gray, cv2.CV_64F).var()

# --- PERSISTENȚĂ (MEMORARE SETĂRI) ---
if 'selected_files' not in st.session_state:
    st.session_state.selected_files = []
if 'threshold' not in st.session_state:
    st.session_state.threshold = 100.0

# --- INTERFAȚĂ ---
st.title("🏗️ Șantier Photo Selector")
st.sidebar.header("Setări Analiză")

# Slider pentru pragul de claritate
st.session_state.threshold = st.sidebar.slider(
    "Prag Claritate (mai mare = mai strict)", 
    0.0, 500.0, st.session_state.threshold
)

uploaded_files = st.file_uploader(
    "Încarcă fotografiile de pe șantier", 
    accept_multiple_files=True, 
    type=['jpg', 'jpeg', 'png']
)

if uploaded_files:
    cols = st.columns(3)
    idx = 0
    
    for uploaded_file in uploaded_files:
        # Procesare imagine
        image = Image.open(uploaded_file)
        score = get_blur_score(image)
        
        is_clear = score >= st.session_state.threshold
        
        # Afișare în coloane
        with cols[idx % 3]:
            st.image(image, caption=f"Scor: {int(score)}", use_container_width=True)
            
            if is_clear:
                st.success("✅ Clară")
                if uploaded_file.name not in st.session_state.selected_files:
                    st.session_state.selected_files.append(uploaded_file.name)
            else:
                st.error("❌ Mișcată")
                if uploaded_file.name in st.session_state.selected_files:
                    st.session_state.selected_files.remove(uploaded_file.name)
        idx += 1

# --- REZUMAT ȘI SALVARE ---
st.sidebar.markdown("---")
st.sidebar.write(f"📂 Fișiere selectate: **{len(st.session_state.selected_files)}**")

if st.sidebar.button("Salvează Selecția"):
    # Aici poți adăuga logica de export (ex: creare folder sau listă text)
    st.sidebar.toast("Selecția a fost salvată în memorie!")

st.sidebar.info("Aplicația va ține minte fișierele selectate pe durata sesiunii deschise.")
