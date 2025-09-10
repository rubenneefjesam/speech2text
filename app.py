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

def get_groq_client():
    # Eerst proberen via ENV (Codespaces / lokaal)
    key = (os.getenv("GROQ_API_KEY") or "").strip()

    # Daarna proberen via Streamlit secrets (Cloud)
    if not key:
        try:
            key = (st.secrets["GROQ_API_KEY"] or "").strip()
        except Exception:
            key = ""

    if not (key and key.startswith("gsk_")):
        st.error("❌ Geen geldige GROQ_API_KEY gevonden. Zet hem in ENV of Streamlit Secrets.")
        return None

    return Groq(api_key=key)

client = get_groq_client()
st.caption(f"🔑 Groq client actief: {bool(client)}")

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

# ======================================
# Upload & Transcriptie pagina
# ======================================
elif page == "Upload & Transcriptie":
    st.title("📂 Upload je audio + context")

    audio_file = st.file_uploader("🎵 Upload audio", type=["wav", "mp3", "m4a"])
    context_file = st.file_uploader("📑 Upload extra context (agenda, definities, afkortingen)", type=["txt", "json"])

    # Wis oude transcriptie
    if st.button("🗑️ Wis transcriptie"):
        st.session_state.pop("transcript", None)
        st.success("Transcriptie gewist.")

    # Context verwerken
    context_data = None
    if context_file:
        try:
            if context_file.type == "application/json":
                context_data = json.load(context_file)
                st.json(context_data)
            else:
                stringio = StringIO(context_file.getvalue().decode("utf-8"))
                context_data = stringio.read()
                st.text(context_data[:500] + ("…" if len(context_data) > 500 else ""))
        except Exception as e:
            st.warning(f"Kon context niet lezen: {e}")

    # Transcriptie functie
    def transcribe(path, model="distil-whisper-large-v3"):
        with open(path, "rb") as f:
            resp = client.audio.transcriptions.create(
                model=model,
                file=f,
                language="nl"
            )
        return resp.text

    if audio_file and client:
        st.audio(audio_file)

        with tempfile.NamedTemporaryFile(delete=False, suffix="." + audio_file.name.split(".")[-1]) as tmp:
            tmp.write(audio_file.getvalue())
            tmp_path = tmp.name

        with st.spinner("Bezig met transcriberen via Groq..."):
            try:
                transcript = transcribe(tmp_path)
            except Exception as e:
                st.error(f"Transcriptie mislukt: {e}")
                st.stop()

        if context_data:
            transcript += "\n\n---\n💡 Toegevoegde context:\n" + (
                context_data if isinstance(context_data, str) else str(context_data)
            )

        st.session_state["transcript"] = transcript

        st.success("Transcriptie afgerond ✅")

        tab1, tab2 = st.tabs(["📝 Transcriptie", "⬇️ Download"])
        with tab1:
            with st.expander("Klik om transcriptie te tonen", expanded=True):
                st.write(transcript)
        with tab2:
            st.download_button(
                "Download transcriptie als TXT",
                data=transcript,
                file_name="transcript.txt",
                mime="text/plain"
            )

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
