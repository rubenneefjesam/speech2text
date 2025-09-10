import os
import streamlit as st
import pandas as pd
from groq import Groq

# ─── Streamlit Page Config ─────────────────────────────────────────────
st.set_page_config(
    page_title="Speech2Text",
    page_icon="🎤",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─── Groq Client Initialisatie ─────────────────────────────────────────
def init_groq_client():
    """
    Initialiseert de Groq-client.
    1) Check omgevingsvariabele GROQ_API_KEY
    2) Fallback op st.secrets.toml
    """
    key = os.getenv("GROQ_API_KEY", "").strip()
    if not key:
        key = st.secrets.get("groq", {}).get("api_key", "").strip()
    if not key:
        st.warning("⚠️ Geen Groq-key gevonden. Transcriptie en verrijken gaan niet werken.")
        return None
    try:
        client = Groq(api_key=key)
        # lichte test-call
        models = client.models.list()
        st.success(f"API key werkt ✅ – {len(models.data)} modellen beschikbaar")
        return client
    except Exception:
        st.error("❌ Groq API key ongeldig, transcriptie kan mislukken.")
        return None

client = init_groq_client()

# ─── Sidebar Navigatie ─────────────────────────────────────────────────
st.sidebar.title("🎤 Speech2Text Demo")
page = st.sidebar.radio(
    "📑 Pagina",
    ["Home", "Upload & Transcriptie", "Analyse", "Over"]
)

# ─── Pagina: Home ───────────────────────────────────────────────────────
if page == "Home":
    st.title("✨ Welkom bij Speech2Text")
    st.markdown(
        """
        Met deze demo kun je eenvoudig een **audiobestand** uploaden en een **verrijkte transcriptie** terugkrijgen.

        🔹 Upload je bestand via de **Upload & Transcriptie** pagina  
        🔹 Voeg context en definities toe om het transcript slimmer te maken  
        🔹 Bekijk woordfrequenties en statistieken bij **Analyse**  
        🔹 Leer meer bij **Over**
        """
    )
    st.success("Kies links een pagina om te starten!")

# ─── Pagina: Upload & Transcriptie ─────────────────────────────────────
elif page == "Upload & Transcriptie":
    st.title("📂 Upload je audio + context")

    transcript = st.session_state.get("transcript", "")
    context_text = ""

    col1, col2 = st.columns(2)

    # Kolom 1: Audio upload en transcriptie
    with col1:
        st.subheader("🎵 Upload audio (wav/mp3/m4a)")
        audio_file = st.file_uploader(
            label="🎵 Kies je audiobestand",
            type=["wav", "mp3", "m4a"],
            key="audio_uploader"
        )
        if audio_file and client:
            data = audio_file.read()
            st.audio(data)
            st.info("Transcriberen…")
            try:
                res = client.audio.transcriptions.create(
                    model="whisper-large-v3",
                    file=(audio_file.name, data)
                )
                transcript = res.text
                st.session_state["transcript"] = transcript
                st.success("Transcriptie afgerond ✅")
                st.code(transcript, language="text")
                st.download_button(
                    "⬇️ Download (TXT)",
                    transcript,
                    file_name="transcript.txt",
                    mime="text/plain"
                )
            except Exception as e:
                st.error(f"Transcriptie mislukt: {e}")

    # Kolom 2: Context upload en preview
    with col2:
        st.subheader("📑 Upload extra context (TXT/JSON)")
        context_file = st.file_uploader(
            label="📑 Kies context-bestand",
            type=["txt", "json"],
            key="context_uploader"
        )
        if context_file:
            if context_file.type == "application/json":
                import json as _json
                context_text = _json.dumps(
                    _json.load(context_file), ensure_ascii=False, indent=2
                )
            else:
                context_text = context_file.read().decode("utf-8", errors="ignore")
            st.subheader("📄 Toegevoegde context (preview)")
            st.text_area(
                "Preview context",
                context_text,
                height=200
            )

    # Combineer transcriptie en context
    if transcript.strip() and context_text.strip() and client:
        st.divider()
        if st.button("✅ Combineer transcriptie met context"):
            st.info("Bezig met combineren…")
            try:
                enrich = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    temperature=0.3,
                    messages=[
                        {"role": "system", "content": (
                            "Combineer het transcript met de extra context. "
                            "Maak er één vloeiende, verbeterde transcriptie van in het Nederlands."
                        )},
                        {"role": "user", "content": (
                            f"Transcript:\n{transcript}\n\nContext:\n{context_text}\n\n"
                            "Geef de gecombineerde versie als doorlopende tekst."
                        )}
                    ]
                )
                enriched = enrich.choices[0].message.content
                st.subheader("🧠 Verrijkte transcriptie")
                st.write(enriched)
                st.download_button(
                    "⬇️ Download verrijkte transcriptie (TXT)",
                    enriched,
                    file_name="verrijkte_transcriptie.txt",
                    mime="text/plain"
                )
            except Exception as e:
                st.error(f"Verrijken mislukt: {e}")

# ─── Pagina: Analyse ───────────────────────────────────────────────────
elif page == "Analyse":
    st.title("📊 Analyse van transcriptie")

    transcript = st.session_state.get("transcript")
    if not transcript:
        st.info(
            "Nog geen transcriptie beschikbaar. Ga eerst naar **Upload & Transcriptie** en maak een transcriptie."
        )
        st.stop()

    words = [w.lower().strip(".,!?") for w in transcript.split()]
    st.metric("Aantal woorden", len(words))

    # Bereken woordfrequenties
    freq = {}
    for w in words:
        freq[w] = freq.get(w, 0) + 1
    freq_df = pd.DataFrame.from_dict(
        freq, orient="index", columns=["aantal"]
    ).sort_values("aantal", ascending=False)

    with st.expander("📑 Woordfrequentie top-20"):
        st.bar_chart(freq_df["aantal"].head(20))
        st.table(freq_df.head(20))

# ─── Pagina: Over ──────────────────────────────────────────────────────
elif page == "Over":
    st.title("ℹ️ Over deze app")
    st.markdown(
        """
        Deze demo is gebouwd met **Streamlit** en laat zien hoe je
        **spraak → tekst → begrip** kunt maken.

        ### 💡 Waarom deze Speech-to-Text tool zo krachtig
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