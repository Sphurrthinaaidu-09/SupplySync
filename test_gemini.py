import os

from dotenv import load_dotenv
from google import genai


load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY was not found")

print("Gemini key found:", bool(api_key))
print("Key prefix:", api_key[:3] + "...")


client = genai.Client(api_key=api_key)


response = client.interactions.create(
    model="gemini-3.8-flash",
    input="Say hello to SupplySync in one short sentence."
)


print("\nGemini response:")
print(response.output_text)