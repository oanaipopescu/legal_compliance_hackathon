import os
import re
import time
import google.generativeai as genai

# === Setup ===
REGULATION_RDF_FOLDER = "rdf_output"
SHACL_OUTPUT_FOLDER = "shacl_output"
API_KEY_FILE = "api_key.txt"
MODEL_NAME = "models/gemini-1.5-flash"

# Configuration
START_FROM = 32  # Start processing from Article_33.ttl
WAIT_BETWEEN = 5  # Wait time between API calls to avoid rate limits

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

# Filter files to start from the specified article number
filtered_files = [f for f in rdf_files if extract_number(f) >= START_FROM]

print(f"Found {len(rdf_files)} total RDF files")
print(f"Will process {len(filtered_files)} files starting from Article_{START_FROM}")

# Define variable to store previous SHACL outputs for context
previous_shacl_outputs = []

# Try to load some context from already processed files if available
for i in range(1, START_FROM):
    shape_file = os.path.join(SHACL_OUTPUT_FOLDER, f"Article_{i}_shape.ttl")
    if os.path.exists(shape_file):
        try:
            with open(shape_file, "r", encoding="utf-8") as f:
                previous_shacl_outputs.append(f.read().strip())
            # Only keep last 3 for context to avoid token limits
            if len(previous_shacl_outputs) > 3:
                previous_shacl_outputs.pop(0)
        except Exception as e:
            print(f"Warning: Could not load context from {shape_file}: {e}")

# === Process each RDF file ===
for i, filename in enumerate(filtered_files):
    filepath = os.path.join(REGULATION_RDF_FOLDER, filename)
    with open(filepath, "r", encoding="utf-8") as f:
        rdf_text = f.read().strip()

    # Use the stored context
    context = "\n\n".join(previous_shacl_outputs)
    
    prompt = f"""
    You are a legal informatics expert. Given an RDF representation of a regulatory obligation, generate a SHACL shape that can be used to validate whether a company's policy RDF graph complies with that obligation.

Do not validate the regulation RDF itself. Instead, use it to extract the constraint logic, and generate SHACL that enforces the regulation on external data.

Your SHACL shape must be written in Turtle syntax and should include:

- `sh:NodeShape`
- `sh:targetClass` to define the type of data the rule applies to
- `sh:property` with:
    - `sh:path` to indicate the constrained property
    - constraints such as `sh:hasValue`, `sh:minCount`, `sh:pattern`, or `sh:datatype`
- `sh:message` to explain the rule
- Optional: `sh:severity` (e.g., `sh:Violation`)

Use the `:example.org#` namespace.

Only output valid SHACL in Turtle syntax — do not include commentary.

Here is the RDF input describing the regulatory obligation:
{rdf_text}
"""
    
    print(f"🔍 Translating {filename} to SHACL... ({i+1}/{len(filtered_files)})")
    try:
        response = model.generate_content(prompt)
        shacl_output = response.text.strip()
    except Exception as e:
        print(f"❌ Error generating SHACL for {filename}: {e}")
        print(f"⏱️ Waiting for 60 seconds before continuing...")
        time.sleep(60)  # Wait longer after an error
        continue

    output_filename = filename.replace(".ttl", "_shape.ttl")
    output_path = os.path.join(SHACL_OUTPUT_FOLDER, output_filename)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(shacl_output)
    
    print(f"✅ Saved SHACL shape: {output_filename}")
    
    # Add current output to previous outputs for future context
    previous_shacl_outputs.append(shacl_output)
    # Only keep last 3 for context to avoid token limits
    if len(previous_shacl_outputs) > 3:
        previous_shacl_outputs.pop(0)
    
    # Wait between requests to avoid hitting rate limits
    if i < len(filtered_files) - 1:  # Don't wait after the last file
        print(f"⏱️ Waiting {WAIT_BETWEEN} seconds to avoid rate limits...")
        time.sleep(WAIT_BETWEEN)

print("\n🎉 All SHACL shapes generated successfully!")