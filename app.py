import streamlit as st
import openai

# Načtení API klíče a ID asistenta ze Streamlit Secrets
ASSISTANT_ID = st.secrets["ASSISTANT_ID"]
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Inicializace OpenAI klienta
client = openai.OpenAI()

# Stav pro sledování první odpovědi
if "first_response" not in st.session_state:
    st.session_state.first_response = True

# Titulek aplikace
st.title("Porovnání významu pojmů")

# Vysvětlení aplikace (zobrazí se pouze jednou)
if st.session_state.first_response:
    st.write("Ahoj! Dnes budeme pracovat na porovnávání významů pojmů. Předložím ti krátké texty a otázky, na které budeš odpovídat. Začneme s prvním textem a otázkou.")

# Textové pole pro vstup uživatele - přesunuto dolů
user_input = st.text_input("Zadejte svou otázku:")

# Odeslání dotazu po zadání vstupu
if user_input:
    with st.spinner("Asistent přemýšlí..."):
        try:
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
            
            # Skrytí debugovacích výpisů a zobrazení pouze odpovědi
            st.empty()  # Vymaže předchozí obsah výstupu
            
            if assistant_response:
                st.write("**Asistent:**")
                st.markdown(f"> {assistant_response}")  # Formátování odpovědi
                st.session_state.first_response = False  # Po první odpovědi už nezobrazovat úvod
            else:
                st.error("❌ Chyba: Nepodařilo se najít odpověď asistenta.")
        except openai.OpenAIError as e:
            st.error(f"❌ Chyba při komunikaci s OpenAI API: {e}")
        except Exception as e:
            st.error(f"❌ Neočekávaná chyba: {e}")
