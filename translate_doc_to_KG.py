import os
import google.generativeai as genai

# Load text from file
with open("translated_regulations/belgium.txt", "r", encoding="utf-8") as f:
    legal_text = f.read()

# --- Set up Google Gemini API
with open("api_key.txt", "r", encoding="utf-8") as key_file:
    api_key = key_file.read().strip()

genai.configure(api_key=api_key)

# Get available models to use the correct model name
models = genai.list_models()
print("Available models:", [model.name for model in models])

# Use a different model that might have a separate quota limit
model = genai.GenerativeModel("models/gemini-1.5-flash")  # Using flash instead of pro

# Prompt to instruct Gemini
prompt = """
You are an expert in legal informatics. Given a legal or policy document, extract the key legal entities, classes (like PersonalData), and obligations (like encryption requirements), and represent them as RDF triples in Turtle format. Use a namespace prefix like:
  @prefix : <http://example.org#> .
Use classes such as `:RegulationRule`, `:PersonalData`, `:requires`, `:appliesTo`, and attributes like `:encrypted`. Output only valid RDF in Turtle syntax.

Here is the text to process:
""" + legal_text

# Get RDF response
response = model.generate_content(prompt)
rdf_output = response.text.strip()

# Save output
with open("output.ttl", "w", encoding="utf-8") as f:
    f.write(rdf_output)

print("RDF Turtle saved to output.ttl")