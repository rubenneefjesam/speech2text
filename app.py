import streamlit as st
import time
import json
from io import StringIO

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

    # Upload audio
    audio_file = st.file_uploader("Upload audio", type=["wav", "mp3", "m4a"])

    # Upload context (txt of json)
    context_file = st.file_uploader("Upload extra context (agenda, definities, afkortingen)", type=["txt", "json"])

    context_data = None
    if context_file:
        if context_file.type == "application/json":
            context_data = json.load(context_file)
            st.info("Context geladen uit JSON 📑")
            st.json(context_data)
        else:
            stringio = StringIO(context_file.getvalue().decode("utf-8"))
            context_data = stringio.read()
            st.info("Context geladen uit TXT 📑")
            st.text(context_data)

    if audio_file:
        st.audio(audio_file)

        with st.spinner("Bezig met transcriberen..."):
            time.sleep(2)  # simulatie vertraging
            # Hier komt straks de echte API-call (Whisper of ander STT-model)
            transcript = "👉 Dit is een test transcriptie van jouw audio."

            # Verrijk transcript met context (dummy)
            if context_data:
                transcript += "\n\n💡 Toegevoegde context:\n" + str(context_data)
        
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

# --- Analyse pagina ---
elif page == "Analyse":
    st.title("📊 Analyse van transcriptie")
    st.write("Hier kun je een eenvoudige analyse uitvoeren op de tekst.")

    # Demo tekst (later vervangen door echte transcriptie)
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
           👉 Voorbeeld: als iemand zegt *“project X loopt vertraging op”*, dan weet de tool door de context welke projectnaam daarbij hoort.  

        3. **Definities en afkortingen**  
           Vaak worden in meetings veel afkortingen of jargon gebruikt.  
           Jij kunt een lijst met **definities/afkortingen** uploaden.  
           De tool herkent ze en zet in het transcript meteen de juiste betekenis erbij.  
           👉 Voorbeeld: *“PO” → Product Owner*, *“AIOT” → Artificial Intelligence Operations Team*.  

        4. **Verrijkte transcriptie = bruikbare notulen**  
           In plaats van een platte tekst krijg je een **leesbaar en begrijpelijk document**.  
           Minder tijd kwijt aan corrigeren of puzzelen wat iemand bedoelde.  
           Direct input voor actiepunten, besluitenlijsten of samenvattingen.  

        5. **Schaalbaarheid en consistentie**  
           Iedere meeting of call krijgt dezelfde kwaliteit.  
           Geen verschil meer tussen wie notuleert of hoe gedetailleerd.  

        ---
        👉 Kortom: dit is **niet zomaar speech-to-text**, maar **speech-to-understanding**.  
        """
    )
    st.success("Klaar voor de volgende stap 🚀")
