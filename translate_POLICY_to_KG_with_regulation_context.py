import os
import google.generativeai as genai

# === Setup ===
SECTION_FOLDER = "policy_sections"
OUTPUT_FOLDER = "policy_rdf_output_with_regulation_context"
REGULATION_RDF_FOLDER = "shacl_output_fixed"
API_KEY_FILE = "api_key.txt"
MODEL_NAME = "models/gemini-1.5-flash"

# === Configuration ===
TARGET_SECTION = "Section_3_7.txt"  # The specific section to process

# === Ensure output folder exists ===
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# === Load API key and configure Gemini ===
with open(API_KEY_FILE, "r", encoding="utf-8") as key_file:
    api_key = key_file.read().strip()
genai.configure(api_key=api_key)

model = genai.GenerativeModel(MODEL_NAME)

# === Load regulation RDF for context ===
regulation_context = []
print("Loading regulation context...")
try:
    regulation_files = sorted(
        [f for f in os.listdir(REGULATION_RDF_FOLDER) if f.lower().endswith(".ttl")],
        key=lambda x: int(x.replace("Article_", "").replace(".ttl", "")) if x.replace("Article_", "").replace(".ttl", "").isdigit() else 0
    )
    
    # Load key regulations (limit to avoid context overflow)
    for reg_file in regulation_files[:10]:  # Include first 10 articles for context
        with open(os.path.join(REGULATION_RDF_FOLDER, reg_file), "r", encoding="utf-8") as f:
            regulation_context.append(f.read().strip())
    print(f"Loaded {len(regulation_context)} regulation files for context")
except Exception as e:
    print(f"Warning: Could not load regulation RDF context: {e}")

# === Load other policy sections as context ===
context_sections = []
print("Loading other policy sections for context...")
section_files = [f for f in os.listdir(SECTION_FOLDER) 
                if f.lower().endswith(".txt") and f != TARGET_SECTION]
try:
    for context_file in section_files[:10]:  # Limit to first 10 for context window
        with open(os.path.join(SECTION_FOLDER, context_file), "r", encoding="utf-8") as f:
            context_sections.append(f"Section: {context_file}\n{f.read().strip()}")
    print(f"Loaded {len(context_sections)} policy sections for context")
except Exception as e:
    print(f"Warning: Could not load policy section context: {e}")

# === Process the target section ===
target_path = os.path.join(SECTION_FOLDER, TARGET_SECTION)
if not os.path.exists(target_path):
    print(f"❌ Error: Target section file {TARGET_SECTION} not found!")
    exit(1)

with open(target_path, "r", encoding="utf-8") as f:
    section_text = f.read().strip()

# Build prompt with all context
reg_context_str = "\n\n".join(regulation_context[:3])  # Include just a few for brevity
policy_context_str = "\n\n".join(context_sections[:3])  # Include just a few for brevity

prompt = f"""
You are an expert in legal informatics. Given a legal or policy document, extract the key legal entities, classes (like PersonalData), and obligations (like encryption requirements), and represent them as RDF triples in Turtle format. Use a namespace prefix like:
  @prefix : <http://example.org#> .
Use classes such as `:RegulationRule`, `:PersonalData`, `:requires`, `:appliesTo`, and attributes like `:encrypted`. Output only valid RDF in Turtle syntax.

Here is the regulatory context from laws:
{reg_context_str}

Context from other policy sections:
{policy_context_str}

Do not generate any RDF triples for the text in previous articles or other sections. Only use them for context.
Here is the text to process and generate RDF triples for:
{section_text}
"""

# Generate RDF using Gemini
print(f"🔍 Processing {TARGET_SECTION}...")
try:
    response = model.generate_content(prompt)
    rdf_output = response.text.strip()

    # Save RDF output
    output_filename = TARGET_SECTION.replace(".txt", ".ttl")
    output_path = os.path.join(OUTPUT_FOLDER, output_filename)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(rdf_output)

    print(f"✅ Saved RDF: {output_filename}")

except Exception as e:
    print(f"❌ Error processing {TARGET_SECTION}: {e}")

print("\n🎉 Processing complete.")