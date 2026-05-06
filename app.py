import os
import streamlit as st
import google
from google.genai.errors import ServerError

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
    secret_key = st.secrets.get("GOOGLE_API_KEY")
    env_key = os.environ.get("GOOGLE_API_KEY")
    api_key = secret_key or env_key
    key_source = "Streamlit secrets" if secret_key else "Environment variable" if env_key else None

    if not api_key:
        st.error("Missing GOOGLE_API_KEY. Add it to Streamlit secrets or as an environment variable.")
        st.stop()

    st.info(f"Using GOOGLE_API_KEY from: {key_source}")

    client = google.genai.Client(api_key=api_key)
    try:
        chat = client.chats.create(
            model="gemini-2.5-flash",
            config={"system_instruction": prompt},
        )
    except Exception as e:
        st.error("Failed to initialize Gemini chat client. Check the API key and the Generative Language API settings.")
        st.exception(e)
        st.stop()
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
    reply = None
    try:
        response = chat.send_message(user_input)
        reply = response.text
    except ServerError as e:
        st.error("The Gemini model is currently busy. Please try again in a few moments.")
        st.exception(e)
        reply = "Sorry, the model is temporarily unavailable. Please try again shortly."
    except Exception as e:
        st.error("An unexpected error occurred while sending the message.")
        st.exception(e)
        reply = "Sorry, something went wrong. Please try again."

    # Show assistant message
    if reply:
        st.session_state.messages.append({"role": "assistant", "content": reply})
        with st.chat_message("assistant"):
            st.write(reply)