import streamlit as st
import cv2
import numpy as np
from PIL import Image
import rawpy
import io
import zipfile

# Configurare pagină
st.set_page_config(page_title="RAW Photo Selector Pro", layout="wide", page_icon="🏗️")

# --- FUNCȚII TEHNICE ---

def process_image(uploaded_file):
    """Procesează fișiere RAW și formate standard."""
    extension = uploaded_file.name.split('.')[-1].lower()
    raw_extensions = ['cr2', 'nef', 'arw', 'dng', 'orf', 'sr2']
    
    try:
        if extension in raw_extensions:
            with rawpy.imread(uploaded_file) as raw:
                # Folosim un 'half_size' pentru viteză mai mare la previzualizare
                rgb = raw.postprocess(use_camera_wb=True, no_auto_bright=True, bright=1.0, half_size=True)
                return Image.fromarray(rgb)
        else:
            return Image.open(uploaded_file)
    except Exception as e:
        st.error(f"Eroare la procesarea {uploaded_file.name}: {e}")
        return None

def get_blur_score(pil_image):
    """Calculează claritatea folosind algoritmul Laplacian."""
    img_array = np.array(pil_image)
    gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    return cv2.Laplacian(gray, cv2.CV_64F).var()

# --- LOGICA DE SESIUNE (PENTRU RESTART/MEMORARE) ---
if 'selected_photos' not in st.session_state:
    st.session_state.selected_photos = {}
if 'threshold' not in st.session_state:
    st.session_state.threshold = 100

# --- INTERFAȚĂ SIDEBAR ---
st.sidebar.title("⚙️ Setări Control")
st.session_state.threshold = st.sidebar.slider("Prag Claritate (Threshold)", 0, 1000, st.session_state.threshold)

st.sidebar.markdown("---")
st.sidebar.subheader("📋 Status Selecție")

# --- INTERFAȚĂ PRINCIPALĂ ---
st.title("📷 Photo Selector - Construcții & RAW")
st.info("Încarcă fișierele tale (JPG sau RAW). Aplicația le va filtra automat pe cele neclare.")

uploaded_files = st.file_uploader(
    "Alege pozele de pe șantier...", 
    accept_multiple_files=True, 
    type=['jpg', 'jpeg', 'png', 'cr2', 'nef', 'arw', 'dng']
)

if uploaded_files:
    # Resetăm dicționarul de selecție la un nou upload dacă e cazul, 
    # sau păstrăm ce e deja încărcat
    
    cols = st.columns(3)
    processed_count = 0
    clear_files = []

    for idx, file in enumerate(uploaded_files):
        img = process_image(file)
        
        if img:
            score = get_blur_score(img)
            is_clear = score >= st.session_state.threshold
            
            # Salvăm starea în session_state
            st.session_state.selected_photos[file.name] = is_clear

            with cols[idx % 3]:
                # Afișare imagine cu ramă colorată în funcție de status
                st.image(img, caption=f"{file.name} | Scor: {int(score)}", use_container_width=True)
                
                if is_clear:
                    st.success(f"✅ OK")
                    clear_files.append(file)
                else:
                    st.error(f"❌ NECLARĂ")
            processed_count += 1

    # --- BUTON DOWNLOAD ZIP (PENTRU SALVARE) ---
    st.sidebar.write(f"Fișiere clare detectate: **{len(clear_files)}**")
    
    if len(clear_files) > 0:
        # Generăm arhiva ZIP în memorie
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
            for f in clear_files:
                zip_file.writestr(f.name, f.getvalue())
        
        st.sidebar.download_button(
            label="⬇️ Descarcă pozele CLARE (.zip)",
            data=zip_buffer.getvalue(),
            file_name="poze_selectate_constructii.zip",
            mime="application/zip"
        )

else:
    st.write("Aștept încărcarea fișierelor...")

# Instrucțiuni sub formă de footer
st.markdown("---")
st.caption("Aplicație creată pentru filtrarea rapidă a fotografiilor de șantier. Suportă formate RAW (Canon, Nikon, Sony, DNG).")
