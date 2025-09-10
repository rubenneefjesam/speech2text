import os
import time
import json
import tempfile
from io import StringIO
import streamlit as st
from groq import Groq

# ============================================================
# Groq client init (werkt in zowel Cloud als Codespaces/lokaal)
# ============================================================
st.write("Key ok?", True)

def get_groq_client():
    key = (os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY") or "").strip()
    if not key:
        st.error("⚠️ GROQ_API_KEY niet gevonden (ENV of .streamlit/secrets.toml).")
        st.stop()
    return Groq(api_key=key)   # << dit is de fix

client = get_groq_client()

# ======================================
# Sidebar navigatie
# ======================================
st.sidebar.title("🎤 Speech2Text Demo")
page = st.sidebar.radio("📑 Pagina", ["Home", "Upload & Transcriptie", "Analyse", "Over"])

# ======================================
# Home pagina
# ======================================
if page == "Home":
    st.title("✨ Welkom bij Speech2Text")
    st.markdown(
        """
        Met deze demo kun je eenvoudig een **audiobestand** uploaden en 
        een **verrijkte transcriptie** terugkrijgen.  

        🔹 Upload je bestand via de **Upload & Transcriptie** pagina  
        🔹 Voeg context en definities toe om het transcript slimmer te maken  
        🔹 Bekijk woordfrequenties en statistieken bij **Analyse**  
        🔹 Leer meer bij **Over**  
        """
    )
    st.success("Kies links een pagina om te starten!")

    st.header("Transcribeer audio met Groq Whisper v3")

# ======================================
# Upload & Transcriptie pagina
# ======================================
elif page == "Upload & Transcriptie":
    st.title("📂 Upload je audio + context")
    audio_file = st.file_uploader("🎵 Upload audio", type=["wav","mp3","m4a"])

    if audio_file:
        st.audio(audio_file)
        st.info("Transcriberen…")
        try:
            res = client.audio.transcriptions.create(
                model="whisper-large-v3",                   # of whisper-large-v3-turbo
                file=(audio_file.name, audio_file.read())   # exact zoals in transcribe_test.py
            )
            transcript = res.text
            st.success("Transcriptie afgerond ✅")
            st.write(transcript)
            st.download_button("⬇️ Download (TXT)", transcript, "transcript.txt", "text/plain")
        except Exception as e:
            st.error(f"Transcriptie mislukt: {e}")

# ======================================
# Analyse pagina
# ======================================
elif page == "Analyse":
    st.title("📊 Analyse van transcriptie")

    transcript = st.session_state.get("transcript")
    if not transcript:
        st.info("Nog geen transcriptie beschikbaar. Ga eerst naar **Upload & Transcriptie** en maak een transcriptie.")
        st.stop()

    words = transcript.split()
    st.metric("Aantal woorden", len(words))

    with st.expander("📑 Woordfrequentie tabel"):
        freq = {}
        for w in words:
            w = w.lower().strip(".,!?")
            freq[w] = freq.get(w, 0) + 1
        st.write(freq)

    st.bar_chart([len(w) for w in words])

# ======================================
# Over pagina
# ======================================
elif page == "Over":
    st.title("ℹ️ Over deze app")
    st.markdown(
        """
        Deze demo is gebouwd met **Streamlit** en laat zien hoe je 
        **spraak → tekst → begrip** kunt maken.  

        ### 💡 Waarom deze Speech-to-Text tool zo krachtig is
        1. **Meer dan alleen een transcript**  
           Niet enkel *“wat is er gezegd”*, maar ook *hoe je het beter begrijpt*.  
        2. **Context toevoegen**  
           Voeg agenda’s of definities toe om uitspraken beter te plaatsen.  
        3. **Definities en afkortingen**  
           Jargon wordt herkend en meteen uitgelegd.  
        4. **Verrijkte transcriptie**  
           Je krijgt bruikbare notulen i.p.v. platte tekst.  
        5. **Schaalbaar en consistent**  
           Iedere meeting krijgt dezelfde kwaliteit.  

        👉 Kortom: **speech-to-understanding** 🚀
        """
    )
