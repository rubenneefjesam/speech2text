import streamlit as st

# --- Sidebar navigatie ---
st.sidebar.title("Navigatie")
page = st.sidebar.radio("Ga naar:", ["Home", "Upload", "Over"])

# --- Home pagina ---
if page == "Home":
    st.title("🎤 Speech-to-Text Demo")
    st.write(
        """
        Welkom bij de demo!  
        - Upload een audio-bestand (WAV, MP3, M4A)  
        - Bekijk de transcriptie direct in de app  
        """
    )
    st.info("Gebruik de zijbalk om naar **Upload** of **Over** te gaan.")

# --- Upload pagina ---
elif page == "Upload":
    st.title("📂 Upload je audio")
    st.write("Upload een audiobestand en ontvang de transcriptie terug.")

    audio_file = st.file_uploader("Upload audio", type=["wav", "mp3", "m4a"])

    if audio_file:
        st.audio(audio_file)
        with st.spinner("Bezig met transcriberen..."):
            # Hier komt straks de echte API-call naar Whisper of een ander model
            transcript = "👉 Dit is een test transcriptie van jouw audio."
        st.success(transcript)

        # Extra fancy: toon transcriptie in een expander
        with st.expander("Bekijk transcriptie-tekst"):
            st.write(transcript)

# --- Over pagina ---
elif page == "Over":
    st.title("ℹ️ Over deze app")
    st.write(
        """
        Deze demo is gebouwd met [Streamlit](https://streamlit.io).  
        Je kunt dit project uitbreiden met:
        - Echte integratie met OpenAI Whisper of een ander STT-model  
        - Meerdere talen en accenten  
        - Export van transcripties (txt/pdf)  
        """
    )
    st.success("Klaar voor de volgende stap 🚀")