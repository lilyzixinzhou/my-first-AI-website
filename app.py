import streamlit as st

st.title("lily's super cool website")

st.header("header")
st.subheader("subheader")
st.write("body text")

count = 0

if st.button("click me"):
    count += 1
st.write("count is ", count)

name = st.text_input("what is your name?")
letter_count = len(name)

if st.button("submit"):
    st.write(f"hello, {name}! welcome to ai lvl 2. there are {letter_count} letters in your name")

with st.sidebar:
    st.header("settings")
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

