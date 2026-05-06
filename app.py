import streamlit as st
from google import genai

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="Chatbot", page_icon="💬")
st.title("💬 General Chatbot")

# ── Load KB & build system prompt (once) ─────────────────────────────────────
@st.cache_resource
def init_chat():
    with open("general_chatbot_dataset.txt", "r") as f:
        kb = f.read()

    prompt = f"""
you are general chatbot dataset your job is to provide answers to the questions answered by the customers,
you should answer them in polite, if there is any question out of the kb say that you did not have that info, only refer the kb and provide the response

{kb}
"""
    client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])   # ← paste your key
    chat = client.chats.create(
        model="gemini-2.5-flash",
        config={"system_instruction": prompt},
    )
    return client, chat

if "chat" not in st.session_state:
    st.session_state.client, st.session_state.chat = init_chat()

chat = st.session_state.chat

# ── Session state for message history ────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

# ── Render previous messages ──────────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ── Chat input ────────────────────────────────────────────────────────────────
if user_input := st.chat_input("Ask something…"):
    # Show user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    # Get model response
    response = chat.send_message(user_input)
    reply = response.text

    # Show assistant message
    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.write(reply)