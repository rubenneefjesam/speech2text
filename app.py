import os
import time
import json
import tempfile
from io import StringIO
import streamlit as st
from groq import Groq

st.set_page_config(
    page_title="Speech2Text",
    page_icon="🎤",
    layout="wide",          # meer ruimte
    initial_sidebar_state="collapsed"  # sidebar standaard dicht
)

import streamlit as st

# Toon wat er in secrets binnenkomt
raw = st.secrets.get("groq", {}).get("api_key", None)
st.write("Raw secret:", repr(raw))

# ============================================================
# Groq client init (werkt in zowel Cloud als Codespaces/lokaal)
# ============================================================
import os
import streamlit as st
from groq import Groq

def get_groq_client():
    # eerst: omgevingsvariabele
    key = os.getenv("GROQ_API_KEY", "").strip()
    # daarna: secrets.toml [groq].api_key
    if not key:
        key = st.secrets.get("groq", {}).get("api_key", "").strip()
    return key

# 1) Haal key op
API_KEY = get_groq_client()

# 2) Maak client (zonder te stopen bij missende key)
client = None
if API_KEY:
    client = Groq(api_key=API_KEY)
else:
    st.warning("⚠️ Geen Groq-key gevonden. Transcriptie en verrijken gaan niet werken.")

# 3) Lichte test-call, maar alleen een warning (niet st.stop())
if client:
    try:
        models = client.models.list()
        st.success(f"API key werkt ✅ – {len(models.data)} modellen beschikbaar")
    except Exception as e:
        st.warning("Groq API key ongeldig, transcriptie kan mislukken.")
        # optioneel: st.write(e)  om de dev-melding even te zien, maar kun je weglaten

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
    st.markdown("""
    Met deze demo kun je eenvoudig een **audiobestand** uploaden en 
    een **verrijkte transcriptie** terugkrijgen.  

    🔹 Upload je bestand via de **Upload & Transcriptie** pagina  
    🔹 Voeg context en definities toe om het transcript slimmer te maken  
    🔹 Bekijk woordfrequenties en statistieken bij **Analyse**  
    🔹 Leer meer bij **Over**  
    """)
    st.success("Kies links een pagina om te starten!")

# ======================================
# Upload & Transcriptie pagina
# ======================================
elif page == "Upload & Transcriptie":
    st.title("📂 Upload je audio + context")

    # transcript & context altijd initialiseren
    transcript = st.session_state.get("transcript", "")
    context_text = ""

    # Maak 2 kolommen naast elkaar
    col1, col2 = st.columns(2)

    # ------------------------
    # Kolom 1: Audio upload + transcript
    # ------------------------
    with col1:
        st.subheader("🎵 Upload audio")
        audio_file = st.file_uploader("🎵 Upload audio", type=["wav", "mp3", "m4a"])
        if audio_file:
            st.audio(audio_file)
            st.info("Transcriberen…")
            try:
                res = client.audio.transcriptions.create(
                    model="whisper-large-v3",
                    file=(audio_file.name, audio_file.read())
                )
                transcript = res.text
                st.session_state["transcript"] = transcript

                st.success("Transcriptie afgerond ✅")
                st.write(transcript)
                st.download_button(
                    "⬇️ Download (TXT)",
                    transcript,
                    "transcript.txt",
                    "text/plain"
                )
            except Exception as e:
                st.error(f"Transcriptie mislukt: {e}")

    # ------------------------
    # Kolom 2: Context upload + preview
    # ------------------------
    with col2:
        st.subheader("📑 Upload extra context (TXT/JSON)")
        context_file = st.file_uploader("📑 Upload extra context", type=["txt", "json"])
        if context_file:
            if context_file.type == "application/json":
                import json as _json
                context_text = _json.dumps(_json.load(context_file), ensure_ascii=False, indent=2)
            else:
                context_text = context_file.read().decode("utf-8", errors="ignore")

            st.subheader("📄 Toegevoegde context (zoals geüpload)")
            st.text(context_text[:800] + ("…" if len(context_text) > 800 else ""))

    # ------------------------
    # Combineer pas na klik (volledige breedte onder kolommen)
    # ------------------------
    if transcript.strip() and context_text.strip():
        st.divider()
        if st.button("✅ Combine record with context to a new transcript"):
            st.info("Bezig met combineren…")
            enrich = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                temperature=0.3,
                messages=[
                    {"role": "system", "content":
                     "Combineer het transcript met de extra context. "
                     "Maak er één vloeiende, verbeterde transcriptie van in het Nederlands."},
                    {"role": "user", "content":
                     f"Transcript:\n{transcript}\n\nContext:\n{context_text}\n\n"
                     "Geef de gecombineerde versie als doorlopende tekst."}
                ]
            )
            enriched = enrich.choices[0].message.content
            st.subheader("🧠 Verrijkte transcriptie")
            st.write(enriched)
            st.download_button(
                "⬇️ Download verrijkte transcriptie (TXT)",
                enriched,
                "verrijkte_transcriptie.txt",
                "text/plain"
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
