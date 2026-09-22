from ai_engine import ask_supplysync


questions = [
    "Which products should I reorder?",
    "Which products are likely to run out?",
    "Which suppliers are causing problems?",
    "Show me inventory risks",
    "What is the demand trend?",
    "How is our OTIF performance?",
    "Which products are costing us the most?"
]


for question in questions:

    result = ask_supplysync(question)

    print("\n" + "=" * 70)
    print("QUESTION:", result["question"])
    print("INTENT:", result["intent"])
    print("TOOL:", result["tool"])
    print("EVIDENCE ROWS:", len(result["evidence"]))