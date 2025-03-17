import streamlit as st
import openai

# Načtení API klíče a ID asistenta ze Streamlit Secrets
ASSISTANT_ID = st.secrets["ASSISTANT_ID"]
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Inicializace OpenAI klienta
client = openai.OpenAI()

# Inicializace stavu aplikace
if "conversation" not in st.session_state:
    st.session_state.conversation = []
if "first_message" not in st.session_state:
    st.session_state.first_message = True

# Titulek aplikace
st.title("Porovnání významu pojmů")

# Zobrazení úvodní zprávy pouze při prvním spuštění
if st.session_state.first_message:
    st.write("Pro spuštění konverzace napište jakoukoli zprávu nebo pozdrav.")

# Kontejner pro výstup asistenta
response_container = st.container()

# Zobrazení celé konverzace
with response_container:
    for role, text in st.session_state.conversation:
        if role == "assistant":
            st.markdown(f'🟡 **Asistent:** {text}')
        else:
            st.markdown(f'🔴 **Vy:** {text}')

# Vstupní pole pro uživatele, vždy umístěné dole
user_input = st.text_input("Napište svoji zprávu:", key="user_input")

# Odeslání zprávy uživatele
if user_input.strip():
    with st.spinner("Asistent přemýšlí..."):
        try:
            # Uložení uživatelského vstupu do konverzace
            st.session_state.conversation.append(("user", user_input))
            st.session_state.first_message = False  # Úvodní zpráva už zmizí
            
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
            for msg in reversed(messages.data):
                if msg.role == "assistant" and msg.content:
                    assistant_response = "\n".join([
                        block.text.value.strip() for block in msg.content
                        if hasattr(block, 'text') and hasattr(block.text, 'value')
                    ])
                    break
            
            # Hodnocení odpovědi
            if "správně" in assistant_response.lower():
                feedback = "🟢 Správná odpověď!"
            else:
                feedback = "🔵 Můžeš to ještě upřesnit?"
            
            # Uložení odpovědi asistenta do konverzace
            if assistant_response:
                st.session_state.conversation.append(("assistant", assistant_response))
                st.session_state.conversation.append(("assistant", feedback))
                st.session_state["user_input"] = ""  # Vymazání vstupu po zpracování
                st.rerun()
            else:
                st.error("❌ Chyba: Nepodařilo se najít odpověď asistenta.")
        except openai.OpenAIError as e:
            st.error(f"❌ Chyba při komunikaci s OpenAI API: {e}")
        except Exception as e:
            st.error(f"❌ Neočekávaná chyba: {e}")
