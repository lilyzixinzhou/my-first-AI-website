while True:
    question = str(input("what is your question? "))
    hits = memories.query(query_texts=[question], n_results=100)
    notes = "\n".join(hits["documents"][0])
    prompt = f"""answer only using the most relevant notes {notes}
    question: {question}"""

    load_dotenv()
    client = OpenAI(
    base_url="https://models.github.ai/inference",
    api_key=os.getenv("GITHUB_TOKEN"),
    )

    r = client.chat.completions.create(
    model="openai/gpt-4o-mini",
    messages=[{"role": "user", "content": prompt}],
    )

    answer = r.choices[0].message.content
    memories.add(
        documents=[f"i was asked: {question}, i answered {answer} at {datetime.now()}"],
        ids=[f"memory{memories.count() + 1}"]
    )

    print(r.choices[0].message.content)