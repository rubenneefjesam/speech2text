import streamlit as st
import time
import json
from io import StringIO
import tempfile
from groq import Groq

# --- Client initialiseren ---
if "GROQ_API_KEY" not in st.secrets:
    st.warning("⚠️ Geen GROQ_API_KEY gevonden. Voeg die toe in .streamlit/secrets.toml (lokaal) of in Streamlit Cloud Secrets.")
    client = None
else:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- Sidebar ---
st.sidebar.image(
    "https://streamlit.io/images/brand/streamlit-logo-secondary-colormark-darktext.png",
    width=160
)
st.sidebar.title("🎤 Speech2Text Demo")
page = st.sidebar.radio("📑 Pagina", ["Home", "Upload & Transcriptie", "Analyse", "Over"])

# --- Home pagina ---
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

# --- Upload & Transcriptie pagina ---
elif page == "Upload & Transcriptie":
    st.title("📂 Upload je audio + context")
    st.write("Upload een audiobestand en (optioneel) extra context of definities.")

    audio_file = st.file_uploader("Upload audio", type=["wav", "mp3", "m4a"])
    context_file = st.file_uploader(
        "Upload extra context (agenda, definities, afkortingen)", 
        type=["txt", "json"]
    )

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

    # Functie voor transcriptie
    def transcribe_with_retry(path, model="whisper-large-v3", retries=3, backoff=2.0):
        for i in range(retries):
            try:
                with open(path, "rb") as f:
                    tr = client.audio.transcriptions.create(
                        model=model,
                        file=f
                    )
                return tr.text
            except Exception as e:
                msg = str(e)
                if "429" in msg or "rate" in msg.lower():
                    if i < retries - 1:
                        time.sleep(backoff * (2 ** i))
                        continue
                raise

    # Transcriptie uitvoeren
    if audio_file and client:
        size_mb = len(audio_file.getvalue()) / (1024 * 1024)
        if size_mb > 25:
            st.error(f"Bestand is {size_mb:.1f} MB — splits het in <25 MB chunks aub.")
            st.stop()

        st.audio(audio_file)

        with tempfile.NamedTemporaryFile(delete=False, suffix="." + audio_file.name.split(".")[-1]) as tmp:
            tmp.write(audio_file.getvalue())
            tmp_path = tmp.name

        st.download_button(
            "⬇️ Download originele opname",
            data=audio_file.getvalue(),
            file_name=audio_file.name or "opname.wav",
            mime=audio_file.type or "audio/wav"
        )

        with st.spinner("Bezig met transcriberen via Groq..."):
            try:
                transcript = transcribe_with_retry(tmp_path)
            except Exception as e:
                st.error(f"Transcriptie mislukt: {e}")
                st.stop()

        if context_data:
            transcript += "\n\n---\n💡 Toegevoegde context:\n" + (
                context_data if isinstance(context_data, str) else str(context_data)
            )

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

        st.progress(100)
    elif not client:
        st.error("Geen Groq-client actief. Controleer je API key.")
    else:
        st.info("⤴️ Upload eerst een audio-bestand (WAV, MP3, M4A).")

# --- Analyse pagina ---
elif page == "Analyse":
    st.title("📊 Analyse van transcriptie")
    st.write("Hier kun je een eenvoudige analyse uitvoeren op de tekst.")

    transcript = "Dit is een test transcriptie van jouw audio. Audio is geweldig en transcriptie werkt goed."
    if transcript:
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

# --- Over pagina ---
elif page == "Over":
    st.title("ℹ️ Over deze app")
    st.markdown(
        """
        Deze demo is gebouwd met **Streamlit** en laat zien hoe je 
        **spraak → tekst → begrip** kunt maken.  

        ### 💡 Waarom deze Speech-to-Text tool zo krachtig is
        1. **Meer dan alleen een transcript**  
           Niet enkel *“wat is er gezegd”*, maar ook *hoe je het beter begrijpt*.  
           Het transcript wordt slim aangevuld met extra informatie en structuur.  

        2. **Context toevoegen**  
           Je kunt vooraf notities of agendapunten van de vergadering toevoegen.  
           De tool gebruikt die context om uitspraken beter te plaatsen.  

        3. **Definities en afkortingen**  
           Vaak worden in meetings veel afkortingen of jargon gebruikt.  
           Jij kunt een lijst met **definities/afkortingen** uploaden.  
           De tool herkent ze en zet in het transcript meteen de juiste betekenis erbij.  

        4. **Verrijkte transcriptie = bruikbare notulen**  
           In plaats van een platte tekst krijg je een **leesbaar en begrijpelijk document**.  
           Minder tijd kwijt aan corrigeren of puzzelen wat iemand bedoelde.  

        5. **Schaalbaarheid en consistentie**  
           Iedere meeting of call krijgt dezelfde kwaliteit.  

        ---
        👉 Kortom: dit is **niet zomaar speech-to-text**, maar **speech-to-understanding**.  
        """
    )
    st.success("Klaar voor de volgende stap 🚀")
