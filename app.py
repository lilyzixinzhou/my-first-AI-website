import streamlit as st
import os
from dotenv import load_dotenv
from openai import OpenAI
from doc_helper import read_file
import chromadb

db = chromadb.PersistentClient(path="./chroma_db")
brain = db.get_or_create_collection("zeus")
memory = db.get_or_create_collection("zeus_chat")
THRESHOLD = 1.5
SYSTEM_PROMPT = ("you are lily's super smart AI, this is your first prompt")

def shorten(text, limit=500):
    return text if len(text) <= limit else text[:limit] + " ... rest removed to keep it short"

def chunk_by_sentence(text, max_size = 400):
    sentences = text.split(". ")
    chunks, current = [], ""
    for sentence in sentences:
        if len(current) + len(sentence) < max_size:
            current += sentence + ". "
        else:
            if current.strip():
                chunks.append(current.strip())
            current = sentence + ". "
    if current.strip():
        chunks.append(current.strip())
    return chunks


def store_document(file):
    text = read_file(file)
    chunks = chunk_by_sentence(text)

    prefix = file.name.replace(" ", "_")
    brain.add(
        documents=chunks,
        ids=[f"{prefix}_chunk{i}" for i in range(len(chunks))],
    )
    return len(text), len(chunks)

def remember_exchange(question, answer):
    #Put this Q and A into long term memory so the AI can remember
    memory.add(
        documents=[f"Question: {question}\n Answer: {shorten(answer)}"],
        ids=[f"turn{memory.count()}"]
    )
st.set_page_config(page_title="lily's super smart AI", page_icon="😛", layout="wide")

st.title("lily's super smart AI 🤓😛")

if "messages" not in st.session_state:
    st.session_state["messages"] = []

with st.sidebar:
    st.header("settings")
    with st.form("settings"):
        sources = st.multiselect("select answer length", ["longer, more detailed answers", "shorter, briefer answers"])
        name = st.text_input("what's your name?")
        creativity = st.slider("creativity:", 0.0, 1.0, 0.5)
        remember_documents = st.slider("how many chunks to remember", 0, 10, 3)
        remember = st.slider("recent turns to keep", 0, 10, 3)
        recall = st.slider("old exchanges to look up", 0, 10, 3)
        notes_only = st.checkbox("only answer using notes")
        saved = st.form_submit_button("save")
    if saved:
        st.write(f"{name} saved sources: {sources} and creativity: {creativity}")
    st.caption(f"In memory: {brain.count()} chunks")
    st.caption(f"Long term memory: {memory.count()} exchanges")
    st.caption(f"On screen: {len(st.session_state.messages)} messages")

    if st.button("clear chat"):
        st.session_state.messages = []
        st.rerun()
    if st.button("forget memory"):
        db.delete_collection("zeus_chat")
        st.rerun()
    if st.button("forget all documents"):
        db.delete_collection("zeus")
        st.rerun()

for old in st.session_state.messages:
    with st.chat_message(old["role"]):
        st.markdown(old["content"])

user_input = st.chat_input(
    "Ask something here...",
    accept_file=True,
    file_type=["pdf", "txt"],)

if user_input:
    prompt = user_input.text
    prompt_file = None
    if user_input.files:
        prompt_file = user_input.files[0]
    with st.chat_message("user"):
        if prompt_file:
            clean_len, n_chunks = store_document(prompt_file)
            st.write(f"📎 **{prompt_file.name}**")
            st.caption(
                f"{clean_len} characters "
                f"stored as {n_chunks} chunks"
            )
        if prompt:
            st.write(f"{prompt}")
    st.session_state.messages.append(
        {"role": "user", "content": prompt if prompt else f"attached: {prompt_file.name}"}
    )
    with st.chat_message("assistant"):
        if not prompt:
            answer = "Saved. Now ask me something about it!"
            st.write(answer)
        else:
            #1. Anything that is relevant to the uploaded docs:
            notes = ""
            docs, dists, good = [], [], []
            if brain.count() > 0:
                hits = brain.query(query_texts=[prompt], n_results=remember_documents)
                docs = hits["documents"][0]
                dists = hits["distances"][0]
                good = [d for d, s in zip(docs, dists) if s < THRESHOLD]
                notes = "\n\n".join(docs)

            #2. Anything that is relevant to the OLD conversation
            recalled = ""
            old_docs, old_dists, old_good = [], [], []
            if recall > 0 and memory.count() > remember:
                found = memory.query(query_texts=[prompt], n_results=recall)
                old_docs = found["documents"][0]
                old_dists = hits["distances"][0]
                old_good = [d for d, s in zip(docs, dists) if s < THRESHOLD]
                recalled = "\n\n".join(found["documents"][0])

            if notes or recalled:
                full_prompt = (f"Answer using only the notes below. "
                               f"If the notes don't contain the answer, say so"
                               f"The notes could contain some irrelevant information"
                               f"{notes}"
                               f"Things we talked about earlier:"
                               f"{recalled}"
                               f"User question: {prompt}")
            else:
                full_prompt = prompt

            with st.expander("What I looked up"):
                #1: notes
                st.caption("From your documents")
                if docs:
                    for d, s in zip(docs, dists):
                        mark = "kept " if s < THRESHOLD else "dropped"
                        st.text(f"{s:.3f} {mark} {d[:70]}")
                else:
                    st.text("nothing")
                #2: remember past convos
                st.caption("From earlier in our conversation")
                if old_docs:
                    for d, s in zip(old_docs, old_dists):
                        mark = "kept " if s < THRESHOLD else "dropped"
                        st.text(f"{s:.3f} {mark} {d[:70]}")
                else:
                    st.text("nothing found")
                #3: recall most recent convos
                st.caption("recent messages i can still see")
                recent = st.session_state.messages[:-1][-(remember * 2):]
                if recent:
                    for m in recent:
                        st.text(f"{m['role']}: {shorten(m['content'], 80)}")

            load_dotenv()
            client = OpenAI(
                base_url="https://api.groq.com/openai/v1",
                api_key = os.environ.get("AI_TOKEN") or st.secrets["AI_TOKEN"],
            )
            #3. The last few turns, word for word bu trimmed
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            past = st.session_state.messages[:-1]
            if remember > 0:
                for m in past[-(remember * 2):]:
                    messages.append({"role": m["role"], "content": shorten(m["content"])})
            messages.append({"role": "user", "content": full_prompt})

            if brain.count() > 0 and not good and not old_good and notes_only:
                answer = "i don't have anything about that in your notes"
                st.write(answer)
            else:
                r = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    temperature=creativity,
                    messages=messages,
                )
                answer = r.choices[0].message.content
                st.write(answer)

        remember_exchange(prompt, answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})