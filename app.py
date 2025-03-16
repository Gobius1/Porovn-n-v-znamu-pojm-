import streamlit as st
import openai

# Načtení API klíče a ID asistenta ze Streamlit Secrets
ASSISTANT_ID = st.secrets["ASSISTANT_ID"]
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Inicializace OpenAI klienta
client = openai.OpenAI()

# Stav pro sledování první odpovědi a konverzace
if "first_response" not in st.session_state:
    st.session_state.first_response = True
if "conversation" not in st.session_state:
    st.session_state.conversation = []

# Titulek aplikace
st.title("Porovnání významu pojmů")

# Zobrazení úvodní věty pouze při prvním spuštění
if st.session_state.first_response:
    st.write("Ahoj! Dnes budeme pracovat na porovnávání významů pojmů. Předložím ti krátké texty a otázky, na které budeš odpovídat. Začneme s prvním textem a otázkou.")
    st.session_state.first_response = False

# Kontejner pro výstup asistenta
response_container = st.container()

# Zobrazení celé konverzace
with response_container:
    for message in st.session_state.conversation:
        role, text = message
        if role == "assistant":
            st.markdown(f"> **Asistent:** {text}")
        else:
            st.markdown(f"**Vy:** {text}")

# Textové pole pro vstup uživatele - nyní vždy dole
user_input = st.text_input("Zadejte svou otázku:", key="user_input")

# Odeslání dotazu po zadání vstupu
if user_input:
    with st.spinner("Asistent přemýšlí..."):
        try:
            # Uložení uživatelského vstupu do konverzace
            st.session_state.conversation.append(("user", user_input))
            
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
            
            # Získání odpovědi asistenta
            messages = client.beta.threads.messages.list(thread_id=thread.id)
            
            # Vyhledání poslední odpovědi asistenta
            assistant_response = None
            for msg in reversed(messages.data):  # Projdeme zprávy od nejnovější
                if msg.role == "assistant" and msg.content:
                    assistant_response = "\n".join([
                        block.text.value.strip() for block in msg.content 
                        if hasattr(block, 'text') and hasattr(block.text, 'value')
                    ])
                    break
            
            # Uložení odpovědi asistenta do konverzace a zobrazení
            if assistant_response:
                st.session_state.conversation.append(("assistant", assistant_response))
                st.experimental_rerun()
            else:
                st.error("❌ Chyba: Nepodařilo se najít odpověď asistenta.")
        except openai.OpenAIError as e:
            st.error(f"❌ Chyba při komunikaci s OpenAI API: {e}")
        except Exception as e:
            st.error(f"❌ Neočekávaná chyba: {e}")
