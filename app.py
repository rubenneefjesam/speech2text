import os
import json
import tempfile
from io import StringIO

import streamlit as st
from groq import Groq


# --- Groq client init (Cloud secrets of ENV fallback) ---
def get_groq_client():
    key = (st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY") or "").strip()
    if not (key and key.startswith("gsk_")):
        st.error("Geen geldige GROQ_API_KEY gevonden (verwacht prefix gsk_).")
        return None
    return Groq(api_key=key)


client = get_groq_client()
st.caption(f"Groq client actief: {bool(client)}")


# --- Helperfunctie: transcribe ---
def transcribe_file(audio_file, model="whisper-large-v3"):
    """
    Verwacht een Streamlit-uploaded file.
    Schrijft dit tijdelijk weg en stuurt naar Groq Whisper model.
    Retourneert transcriptie als tekst.
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix="." + audio_file.name.split(".")[-1]) as tmp:
        tmp.write(audio_file.getvalue())
        tmp_path = tmp.name

    with open(tmp_path, "rb") as f:
        resp = client.audio.transcriptions.create(
            model=model,
            file=f,
            response_format="json",
            temperature=0.0,
            language="nl"
        )
    return resp.text

# --- Sidebar / Router ---
st.sidebar.image(
    "https://streamlit.io/images/brand/streamlit-logo-secondary-colormark-darktext.png",
    width=160
)
st.sidebar.title("🎤 Speech2Text Demo")
page = st.sidebar.radio("📑 Pagina", ["Home", "Upload & Transcriptie", "Analyse", "Over"])

# --- Diagnose (optioneel) ---
with st.expander("🔧 Diagnose API", expanded=False):
    st.write("Client init:", bool(client))
    if client and st.button("Test Groq models.list()"):
        try:
            models = client.models.list()
            st.success(f"OK. Models: {[m.id for m in models.data][:5]}")
        except Exception as e:
            st.error(f"API test failed: {e}")

# --- Home ---
if page == "Home":
    st.title("✨ Welkom bij Speech2Text")
    st.markdown(
        """
        Met deze demo kun je eenvoudig een **audiobestand** uploaden en 
        een **verrijkte transcriptie** terugkrijgen.
        """
    )
    st.success("Kies links een pagina om te starten!")

# --- Upload & Transcriptie ---
elif page == "Upload & Transcriptie":
    st.title("📂 Upload je audio + context")
    st.write("Upload een audiobestand en (optioneel) extra context of definities.")

    # Uploads
    audio_file = st.file_uploader("Upload audio", type=["wav", "mp3", "m4a"])
    context_file = st.file_uploader(
        "Upload extra context (agenda, definities, afkortingen)", type=["txt", "json"]
    )

    # Wis-knop (reset sessie)
    if st.button("🗑️ Wis transcriptie"):
        st.session_state.pop("transcript", None)
        st.success("Transcriptie gewist.")

    # Context verwerken
    context_data = None
    if context_file:
        try:
            if context_file.type == "application/json":
                context_data = json.load(context_file)
                st.info("Context geladen uit JSON 📑")
                st.json(context_data)
            else:
                stringio = StringIO(context_file.getvalue().decode("utf-8"))
                context_data = stringio.read()
                st.info("Context geladen uit TXT 📑")
                st.text(context_data[:2000] + ("…" if len(context_data) > 2000 else ""))
        except Exception as e:
            st.warning(f"Kon context niet lezen: {e}")

    # Helper: transcriptie met simpele retry
    def transcribe_with_retry(path, model="whisper-large-v3", retries=3, backoff=2.0):
        for i in range(retries):
            try:
                with open(path, "rb") as f:
                    tr = client.audio.transcriptions.create(model=model, file=f)
                return tr.text
            except Exception as e:
                msg = str(e)
                if ("429" in msg or "rate" in msg.lower()) and i < retries - 1:
                    time.sleep(backoff * (2 ** i))
                    continue
                raise

    # Transcriptie uitvoeren
    if audio_file and client:
        size_mb = len(audio_file.getvalue()) / (1024 * 1024)
        if size_mb > 25:
            st.error(f"Bestand is {size_mb:.1f} MB — splits het in < 25 MB chunks aub.")
            st.stop()

        st.audio(audio_file)

        # veilig opslaan
        with tempfile.NamedTemporaryFile(delete=False, suffix="." + audio_file.name.split(".")[-1]) as tmp:
            tmp.write(audio_file.getvalue())
            tmp_path = tmp.name

        # download origineel
        st.download_button(
            "⬇️ Download originele opname",
            data=audio_file.getvalue(),
            file_name=audio_file.name or "opname.wav",
            mime=audio_file.type or "audio/wav"
        )

        # echte transcriptie (Groq)
        with st.spinner("Bezig met transcriberen via Groq..."):
            try:
                transcript = transcribe_with_retry(tmp_path)
            except Exception as e:
                st.error(f"Transcriptie mislukt: {e}")
                st.stop()

        # verrijking met context (simpel)
        if context_data:
            transcript += "\n\n---\n💡 Toegevoegde context:\n" + (
                context_data if isinstance(context_data, str) else str(context_data)
            )

        # bewaren voor Analyse-pagina
        st.session_state["transcript"] = transcript

        st.success("Transcriptie afgerond ✅")

        # tonen + downloaden
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

        st.progress(100)

    elif not client:
        st.error("Geen Groq-client actief. Controleer je API key.")
    else:
        st.info("⤴️ Upload eerst een audio-bestand (WAV, MP3, M4A).")

# --- Analyse ---
elif page == "Analyse":
    st.title("📊 Analyse van transcriptie")

    transcript = st.session_state.get("transcript")
    if not transcript:
        st.info("Nog geen transcriptie beschikbaar. Ga eerst naar **Upload & Transcriptie** en maak een transcriptie.")
        st.stop()

    words = transcript.split()
    word_count = len(words)
    st.metric("Aantal woorden", word_count)

    with st.expander("Woordfrequentie tabel"):
        freq = {}
        for w in words:
            w = w.lower().strip(".,!?")
            freq[w] = freq.get(w, 0) + 1
        st.write(freq)

    st.bar_chart([len(w) for w in words])

# --- Over ---
elif page == "Over":
    st.title("ℹ️ Over deze app")
    st.markdown(
        """
        Deze demo is gebouwd met **Streamlit** en laat zien hoe je 
        **spraak → tekst → begrip** kunt maken.  

        **Waarom waardevol**
        - Meer dan alleen *wat is er gezegd* → ook *begrip en context*.
        - Voeg **context/definities/afkortingen** toe voor scherpere transcripties.
        - Sneller naar bruikbare notulen, besluiten en actiepunten.
        - Consistente kwaliteit bij elke meeting.
        """
    )
    st.success("Klaar voor de volgende stap 🚀")
