import os
import re
import google.generativeai as genai

# === Setup ===
REGULATION_RDF_FOLDER = "rdf_output"
SHACL_OUTPUT_FOLDER = "shacl_output"
API_KEY_FILE = "api_key.txt"
MODEL_NAME = "models/gemini-1.5-flash"

# === Ensure output folder exists ===
os.makedirs(SHACL_OUTPUT_FOLDER, exist_ok=True)

# === Load API key and configure Gemini ===
with open(API_KEY_FILE, "r", encoding="utf-8") as key_file:
    api_key = key_file.read().strip()
genai.configure(api_key=api_key)

model = genai.GenerativeModel(MODEL_NAME)

# === Get all .ttl RDF files ===
# Use a proper numeric sorting function
def extract_number(filename):
    # Extract the numeric part from "Article_X.ttl"
    match = re.search(r'Article_(\d+)\.ttl', filename)
    if match:
        return int(match.group(1))
    return 0

# Get and sort files by numeric value, not string order
rdf_files = [f for f in os.listdir(REGULATION_RDF_FOLDER) if f.lower().endswith(".ttl")]
rdf_files.sort(key=extract_number)

print(f"Found {len(rdf_files)} RDF files to process: {rdf_files}")

# Define variable to store previous SHACL outputs for context
previous_shacl_outputs = []

# === Process each RDF file ===
for i, filename in enumerate(rdf_files):
    filepath = os.path.join(REGULATION_RDF_FOLDER, filename)
    with open(filepath, "r", encoding="utf-8") as f:
        rdf_text = f.read().strip()

    # Use the stored context
    context = "\n\n".join(previous_shacl_outputs)
    
    
    prompt = f"""
You are an expert in SHACL and RDF compliance rules. 
Given RDF triples representing a regulatory obligation, generate a SHACL shape in Turtle syntax that validates whether an RDF policy graph conforms to that obligation.

Your output should use SHACL constructs like:
- sh:NodeShape
- sh:targetClass
- sh:property
- sh:path
- sh:hasValue or sh:minCount/sh:pattern as appropriate
- sh:message

Do not include commentary. Only output valid SHACL Turtle.

Here is the previous SHACL output for context:
{context}
Do not generate any SHACL shapes for the text in the previous articles. Only use them for context.

Here is the RDF input to process and generate SHACL shapes for:
```turtle
{rdf_text}
```
"""
    
    print(f"🔍 Translating {filename} to SHACL... ({i+1}/{len(rdf_files)})")
    try:
        response = model.generate_content(prompt)
        shacl_output = response.text.strip()
    except Exception as e:
        print(f"❌ Error generating SHACL for {filename}: {e}")
        continue

    output_filename = filename.replace(".ttl", "_shape.ttl")
    output_path = os.path.join(SHACL_OUTPUT_FOLDER, output_filename)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(shacl_output)
    
    print(f"✅ Saved SHACL shape: {output_filename}")
    
    # Add current output to previous outputs for future context
    previous_shacl_outputs.append(shacl_output)

print("\n🎉 All SHACL shapes generated successfully!")