import os
import json

from dotenv import load_dotenv
from google import genai

from database import (
    get_supply_risks,
    get_inventory_risks,
    get_supplier_performance,
    get_product_demand,
    get_otif_performance,
    get_cost_analysis,
    get_stockout_exposure,
    get_supplier_comparison,
    get_replenishment_recommendations,
    get_supplier_risk_summary,
)

# ---------------------------------------------------------
# Gemini setup
# ---------------------------------------------------------

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY was not found")

client = genai.Client(api_key=api_key)


# ---------------------------------------------------------
# SupplySync analytical tools
# ---------------------------------------------------------

TOOLS = {
    "supply_risks": get_supply_risks,
    "inventory_risks": get_inventory_risks,
    "supplier_performance": get_supplier_performance,
    "product_demand": get_product_demand,
    "otif_performance": get_otif_performance,
    "cost_analysis": get_cost_analysis,
    "stockout_exposure": get_stockout_exposure,
    "supplier_comparison": get_supplier_comparison,
    "replenishment_recommendations": get_replenishment_recommendations,
    "supplier_risk_summary": get_supplier_risk_summary,
}


def run_tool(tool_name):
    if tool_name not in TOOLS:
        raise ValueError(f"Unknown tool: {tool_name}")

    return TOOLS[tool_name]()


# ---------------------------------------------------------
# Intent detection
# ---------------------------------------------------------

def detect_intent(question):

    question = question.lower()

    # -----------------------------------------------------
    # Replenishment
    # -----------------------------------------------------

    if any(word in question for word in [
        "reorder",
        "replenish",
        "purchase",
        "buy",
        "restock",
    ]):
        return "replenishment"

    # -----------------------------------------------------
    # Stockout
    # -----------------------------------------------------

    elif any(word in question for word in [
        "stockout",
        "run out",
        "running out",
        "shortage",
    ]):
        return "stockout"

    # -----------------------------------------------------
    # General supply-chain risk
    # -----------------------------------------------------

    elif any(word in question for word in [
        "risk",
        "risks",
        "at risk",
        "priority risk",
        "operational risk",
        "supply chain risk",
    ]):
        return "supply_risk"

    # -----------------------------------------------------
    # Supplier risk
    # -----------------------------------------------------

    elif any(word in question for word in [
        "supplier",
        "vendor",
    ]):
        return "supplier_risk"

    # -----------------------------------------------------
    # Inventory risk
    # -----------------------------------------------------

    elif any(word in question for word in [
        "inventory",
        "stock",
        "inventory level",
    ]):
        return "inventory_risk"

    # -----------------------------------------------------
    # Demand
    # -----------------------------------------------------

    elif any(word in question for word in [
        "demand",
        "sales",
        "demand trend",
    ]):
        return "demand"

    # -----------------------------------------------------
    # OTIF / delivery
    # -----------------------------------------------------

    elif any(word in question for word in [
        "otif",
        "on time",
        "delivery performance",
        "fulfillment",
    ]):
        return "otif"

    # -----------------------------------------------------
    # Cost
    # -----------------------------------------------------

    elif any(word in question for word in [
        "cost",
        "spending",
        "expense",
        "price",
    ]):
        return "cost"

    # -----------------------------------------------------
    # Unknown
    # -----------------------------------------------------

    else:
        return "unknown"


# ---------------------------------------------------------
# Intent → analytical tool
# ---------------------------------------------------------

INTENT_TO_TOOL = {
    "replenishment": "replenishment_recommendations",
    "stockout": "stockout_exposure",
    "supply_risk": "supply_risks",
    "supplier_risk": "supplier_risk_summary",
    "inventory_risk": "inventory_risks",
    "demand": "product_demand",
    "otif": "otif_performance",
    "cost": "cost_analysis",
}


# ---------------------------------------------------------
# Gemini response generation
# ---------------------------------------------------------

def generate_ai_response(question, intent, evidence):

    evidence_json = json.dumps(
        evidence,
        indent=2,
        default=str,
    )

    prompt = f"""
You are SupplySync, an AI-powered supply-chain
decision-support assistant.

Your job is to explain supply-chain data and help a
business user make informed decisions.

IMPORTANT RULES:

1. Use ONLY the evidence provided below.
2. Do NOT invent numbers, products, suppliers, dates,
   costs, risks, or recommendations.
3. If the evidence does not contain enough information,
   clearly say that the available data is insufficient.
4. Explain the most important findings first.
5. When appropriate, provide a clear business action.
6. Keep the answer concise and professional.
7. Mention important numbers from the evidence when
   they support your conclusion.
8. Do not claim that you personally performed an action.
9. You are a decision-support assistant, not the final
   decision maker.

USER QUESTION:
{question}

DETECTED INTENT:
{intent}

DATABASE EVIDENCE:
{evidence_json}

Now answer the user's question using only this evidence.
"""

    response = client.interactions.create(
        model="gemini-3.8-flash",
        input=prompt,
    )

    return response.output_text


# ---------------------------------------------------------
# Main SupplySync AI function
# ---------------------------------------------------------

def ask_supplysync(question):

    intent = detect_intent(question)

    # -----------------------------------------------------
    # Unknown intent
    # -----------------------------------------------------

    if intent == "unknown":

        return {
            "question": question,
            "intent": "unknown",
            "tool": None,
            "evidence": [],
            "answer": (
                "I couldn't determine which SupplySync "
                "analysis is relevant to your question."
            ),
        }

    # -----------------------------------------------------
    # Select analytical tool
    # -----------------------------------------------------

    tool_name = INTENT_TO_TOOL[intent]

    # -----------------------------------------------------
    # Retrieve PostgreSQL evidence
    # -----------------------------------------------------

    evidence = run_tool(tool_name)

    # Keep Gemini evidence focused and within a manageable size.
    if isinstance(evidence, list):
        evidence = evidence[:30]

    # -----------------------------------------------------
    # Generate grounded Gemini response
    # -----------------------------------------------------

    answer = generate_ai_response(
        question,
        intent,
        evidence,
    )

    # -----------------------------------------------------
    # Return complete decision-intelligence result
    # -----------------------------------------------------

    return {
        "question": question,
        "intent": intent,
        "tool": tool_name,
        "evidence": evidence,
        "answer": answer,
    }