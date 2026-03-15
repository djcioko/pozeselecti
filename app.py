import streamlit as st
import cv2
import numpy as np
from PIL import Image
import rawpy
import io
import zipfile
import gc

# 1. Configurare pagină
st.set_page_config(page_title="Pro Selector Foto", layout="wide")

# 2. Funcție procesare imagini (RAW + Standard)
def process_image(uploaded_file):
    try:
        ext = uploaded_file.name.split('.')[-1].lower()
        if ext in ['cr2', 'nef', 'arw', 'dng', 'orf', 'sr2']:
            with rawpy.imread(uploaded_file) as raw:
                # half_size=True consumă de 4 ori mai puțin RAM
                rgb = raw.postprocess(use_camera_wb=True, half_size=True, no_auto_bright=True, bright=1.0)
                return Image.fromarray(rgb)
        else:
            img = Image.open(uploaded_file)
            return img.convert("RGB")
    except Exception as e:
        st.error(f"Nu pot citi fișierul {uploaded_file.name}: {e}")
        return None

# 3. Funcție calcul claritate
def get_blur_score(pil_img):
    try:
        img_array = np.array(pil_img)
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        score = cv2.Laplacian(gray, cv2.CV_64F).var()
        del img_array, gray
        return score
    except:
        return 0

# 4. Interfață Utilizator
st.title("🏗️ Selector Foto Șantier (RAW & JPG)")
st.write("Încarcă pozele pentru a filtra automat cadrele neclare.")

# Setări în sidebar
st.sidebar.header("Setări Analiză")
threshold = st.sidebar.slider("Prag Claritate (mai mare = mai strict)", 0, 500, 100)

uploaded_files = st.file_uploader("Încarcă fotografiile", accept_multiple_files=True, type=['jpg', 'jpeg', 'png', 'cr2', 'nef', 'arw', 'dng'])

if uploaded_files:
    st.info(f"Se procesează {len(uploaded_files)} fișiere...")
    
    clear_photos = []
    cols = st.columns(4) # Afișăm pe 4 coloane
    
    for idx, file in enumerate(uploaded_files):
        img = process_image(file)
        
        if img:
            score = get_blur_score(img)
            is_clear = score >= threshold
            
            with cols[idx % 4]:
                st.image(img, caption=f"{file.name[:10]}... (Scor: {int(score)})", use_container_width=True)
                if is_clear:
                    st.success("✅ CLARĂ")
                    clear_photos.append(file)
                else:
                    st.error("❌ NECLARĂ")
            
            # Curățăm memoria RAM imediat după afișare
            del img
            gc.collect()

    # 5. Buton de descărcare pentru pozele bune
    if clear_photos:
        st.sidebar.markdown("---")
        st.sidebar.subheader(f"Gata! {len(clear_photos)} poze selectate")
        
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "a") as zf:
            for f in clear_photos:
                zf.writestr(f.name, f.getvalue())
        
        st.sidebar.download_button(
            label="⬇️ Descarcă ZIP cu pozele bune",
            data=zip_buffer.getvalue(),
            file_name="poze_clare_santier.zip",
            mime="application/zip"
        )
else:
    st.info("Aștept fișiere pentru procesare.")
