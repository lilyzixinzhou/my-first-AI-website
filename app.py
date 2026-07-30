import streamlit as st

st.title("lily's super cool website")

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

with st.chat_message("user"):
    st.write(f"hello, i am lily. welcome to ai level 2")
with st.chat_message("assistant"):
    st.write(f"hello {name}, i am billy!. welcome to ai level 2")

prompt = st.chat_input("ask something here... ")

if prompt:
    with st.chat_message("user"):
        st.write(prompt)

