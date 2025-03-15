import streamlit as st
import openai

# Nastavení API klíče (musíš mít v Streamlit secrets)
openai.api_key = st.secrets["OPENAI_API_KEY"]

# ID asistenta (nahraď správným ID tvého asistenta!)
ASSISTANT_ID = "asst_HbGXnIsTBiRDtq8YGobiiKUz"  # Nahraď správným ID asistenta

# Inicializace OpenAI klienta
client = openai.OpenAI()

# Titulek aplikace
st.title("Historický asistent – Alternativní dějiny")

# Vysvětlení aplikace
st.write("Zadejte otázku a zjistěte, jak by mohla vypadat historie jinak!")

# Textové pole pro vstup uživatele
user_input = st.text_input("Zadejte svou otázku:")

# Když uživatel zadá otázku a stiskne Enter
if user_input:
    with st.spinner("Asistent přemýšlí..."):
        # Vytvoření nového vlákna pro konverzaci
        thread = client.beta.threads.create()

        # Odeslání zprávy uživatele do konverzace
        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_input
        )

        # Spuštění asistenta
        run = client.beta.threads.runs.create_and_poll(
            thread_id=thread.id,
            assistant_id=ASSISTANT_ID
        )

        # Získání všech zpráv z tohoto vlákna
        messages = client.beta.threads.messages.list(thread_id=thread.id)

        # Zobrazení poslední zprávy asistenta
        if messages.data:
            last_message = messages.data[0].content[0].text.value
            st.write("**Asistent:**", last_message)
        else:
            st.write("❌ Chyba: Asistent neposlal žádnou odpověď.")
