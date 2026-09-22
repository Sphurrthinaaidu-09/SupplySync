from ai_engine import ask_supplysync


result = ask_supplysync(
    "Which products should I reorder?"
)


print("\nQuestion:")
print(result["question"])

print("\nIntent:")
print(result["intent"])

print("\nTool used:")
print(result["tool"])

print("\nAI Answer:")
print(result["answer"])