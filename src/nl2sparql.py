# src/nl2sparql.py
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

def clean_sparql_output(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = text.replace("```sparql", "").replace("```", "").strip()
    lines = [ln for ln in text.splitlines() if not ln.strip().lower().startswith("prefix")]
    return "\n".join(lines).strip()

def nl_to_sparql(question: str) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in .env")

    client = OpenAI(api_key=api_key)

    prompt = f"""
You are an assistant that converts natural language into SPARQL queries.
Ontology:
- foaf:Person
- foaf:name
- ex:age
- ex:worksAt
- ex:Company nodes exist as ex:Company1, ex:Company2, etc.
- People nodes exist as ex:Person1, ex:Person2, etc.

Rules:
- Always use proper prefixed URIs (ex:PersonX, ex:CompanyY)
- Output ONLY SPARQL (no markdown)
- SELECT for retrieval
- INSERT for adding triples
- DELETE for removing triples
- Do NOT include PREFIX lines
- Ensure valid rdflib SPARQL syntax

Question: "{question}"
SPARQL:
"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    raw = response.choices[0].message.content.strip()
    return clean_sparql_output(raw)
