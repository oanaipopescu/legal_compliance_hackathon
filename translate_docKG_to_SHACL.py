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
START_FROM = 16  # Start processing from Article_16.ttl
END_AT = 16      # End processing at Article_16.ttl (inclusive)
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

# Filter files to process articles between START_FROM and END_AT (inclusive)
filtered_files = [f for f in rdf_files if START_FROM <= extract_number(f) <= END_AT]

print(f"Found {len(rdf_files)} total RDF files")
print(f"Will process {len(filtered_files)} files from Article_{START_FROM} to Article_{END_AT}")

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

You are not generating a SHACL shape for the RDF itself, but rather for the obligation it describes. The SHACL should be generic enough to apply to any RDF data that meets the obligation.

IMPORTANT: Be extremely precise about timing and quantitative constraints in the regulations:
1. If there are time limits (e.g., "within 24/72 hours"), use specific constraints to enforce them
2. If there are numerical thresholds, explicitly encode them (like minimum counts, maximum values)
3. Use `sh:pattern` for specific formats with explicit regex patterns
4. Use SPARQL-based constraints (sh:sparql) for complex validations like comparing dates or enforcing time windows
5. For date/time values, don't just validate the datatype - also validate any specific timing requirements

Generate SHACL that enforces not only the presence of values, but that the values match the decision logic from the regulation. 
For example, if functionalImpact includes '10 or more users', and informationImpact includes 'Secret Classified', then severity must be 'High'. 
Use SPARQL constraints where necessary.

The SHACL should be comprehensive and cover all aspects of the obligation.
Be very specific about the constraints and properties, be detail-oriented, and ensure that the SHACL is valid.
Use specific parameters and constraints that are relevant to the obligation described in the RDF.

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