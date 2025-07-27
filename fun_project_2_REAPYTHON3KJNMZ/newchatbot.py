import streamlit as st
import requests
import json
import os

# --- Konfigurasi dasar halaman ---
st.set_page_config(page_title="Salsa AI Chatbot", page_icon="🤖", layout="centered")

# --- Penjelasan Demo ---
with st.expander("📌 About this Demo & How to Use", expanded=True):
    st.markdown("""
**Salsa's AI Chatbot Demo** is:

🆓 Free to use  
⚡ Fast & Simple  
🎯 Text-input ready

**Steps to Use:**

👉 Choose your **AI Model** in the sidebar  
🔑 Enter your **OpenRouter API Key** *(optional)*  
💬 Start **chatting using text**, you can also download your chat history with AI!

> ⚠️ *This demo only supports **text-based** input.*
""")

# --- Model list ---
model_options = {
    "Mistral 7B (Free)": "mistralai/mistral-7b-instruct:free",
    "Deepseek V3 0324 (Free)": "deepseek/deepseek-chat-v3-0324",
    #"Llama 3 8B (Free)": "meta-llama/llama-3-8b-instruct:free",
    #"Claude 3.5 Sonnet": "anthropic/claude-3.5-sonnet",
    "Google Gemini 2.5 Pro Experimental (Free)": "google/gemini-2.5-pro-exp:free"
}

# --- Sidebar ---
st.sidebar.title("⚙️ Settings")
selected_model = st.sidebar.selectbox("Choose AI Model", list(model_options.keys()))
user_input_api_key = st.sidebar.text_input(
    "🔑 OpenRouter API Key",
    type="password",
    placeholder="Enter API Key (optional)"
)

# --- Gunakan API Key dari input atau default ---
api_key = user_input_api_key or os.getenv("OPENROUTER_API_KEY") or "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"

# --- Inisialisasi sesi pesan ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Tampilkan percakapan sebelumnya ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- Input pengguna baru ---
prompt = st.chat_input("Say something...")

if prompt:
    # Tampilkan pesan pengguna
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.spinner("🤖 AI is thinking..."):
        # Siapkan payload ke API
        payload = {
            "model": model_options[selected_model],
            "messages": st.session_state.messages,
            "temperature": 0.7,
        }

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost",
            "X-Title": "Salsa AI Chatbot",
        }

        try:
            res = requests.post("https://openrouter.ai/api/v1/chat/completions", json=payload, headers=headers)
            res.raise_for_status()
            assistant_reply = res.json()["choices"][0]["message"]["content"]

            # Tampilkan balasan AI
            st.chat_message("assistant").markdown(assistant_reply)
            st.session_state.messages.append({"role": "assistant", "content": assistant_reply})

        except requests.exceptions.RequestException as e:
            st.error(f"Error: {e}")
            st.session_state.messages.append({"role": "assistant", "content": "Sorry, something went wrong."})

# --- Tombol Unduh Riwayat Chat ---
if st.session_state.messages:
    chat_log = ""
    for msg in st.session_state.messages:
        role = "You" if msg["role"] == "user" else "AI"
        chat_log += f"{role}: {msg['content']}\n\n"

    st.download_button(
        label="📄 Download Chat History (.txt)",
        data=chat_log,
        file_name="salsa_chat_history.txt",
        mime="text/plain"
    )
