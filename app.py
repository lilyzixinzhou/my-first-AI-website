import streamlit as st
import os
from dotenv import load_dotenv
from openai import OpenAI

st.set_page_config(page_title="super smart AI", page_icon="😛", layout="wide")

st.title("lily's super smart AI")

with st.sidebar:
    st.header("settings")
    name = st.text_input("what is your name?")
    if st.button("submit"):
        st.write(f"hello, {name}! welcome to ai level 2.")
    st.selectbox("select an option", ["one", "two"])
    st.multiselect("select a few options", ["one", "two"])
    st.slider("creativity", 0.1, 0.0, 0.5)

    with st.form("settings"):
        sources = st.multiselect("select a few options", ["one", "two", "three"])
        creativity = st.slider("creativity", 0.9, 0.8, 0.7)
        saved = st.form_submit_button("submit")
    if saved:
        st.write(f"saved sources: {sources} and creativity: {creativity}")

left, right = st.columns(2)
left.write("sources: 3")
right.write("creativity: 2")

prompt = st.chat_input("ask something here... ")

if prompt:
    with st.chat_message("user"):
        st.write(prompt)
    with st.chat_message("assistant"):
        # code from previous class
        load_dotenv()
        client = OpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=os.environ.get("AI_TOKEN") or st.secrets("AI_TOKEN")
        )

        r = client.chat.completions.create(
        model = "llama-3.3-70b-versatile",
        messages = [{"role": "user", "content": prompt}],
        )
        st.write(r.choices[0].message.content)
