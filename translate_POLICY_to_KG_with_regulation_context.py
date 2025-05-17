import os
import google.generativeai as genai

# === Setup ===
SECTION_FOLDER = "policy_sections"
OUTPUT_FOLDER = "policy_rdf_output_with_regulation_context"
REGULATION_RDF_FOLDER = "rdf_output"  # Add folder for regulation RDF
API_KEY_FILE = "api_key.txt"
MODEL_NAME = "models/gemini-1.5-flash"

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
    
    # Load key regulations (limit to first few to avoid context overflow)
    for reg_file in regulation_files[:5]:  # Only include first 5 articles for context
        with open(os.path.join(REGULATION_RDF_FOLDER, reg_file), "r", encoding="utf-8") as f:
            regulation_context.append(f.read().strip())
    print(f"Loaded {len(regulation_context)} regulation files for context")
except Exception as e:
    print(f"Warning: Could not load regulation RDF context: {e}")

# === Get sorted list of section files ===
def section_sort_key(filename):
    number_part = filename.replace("Section_", "").replace(".txt", "")
    return [int(part) for part in number_part.split("_")]

section_files = sorted(
    [f for f in os.listdir(SECTION_FOLDER) if f.lower().startswith("section_") and f.endswith(".txt")],
    key=section_sort_key
)

previous_translations = []

# === Process each section ===
for i, filename in enumerate(section_files):
    filepath = os.path.join(SECTION_FOLDER, filename)
    with open(filepath, "r", encoding="utf-8") as f:
        section_text = f.read().strip()

    # Build prompt, including regulation context and previous RDF outputs
    policy_context = "\n\n".join(previous_translations)
    reg_context_str = "\n\n".join(regulation_context)
    
    prompt = f"""
You are an expert in legal informatics. Given a legal or policy document, extract the key legal entities, classes (like PersonalData), and obligations (like encryption requirements), and represent them as RDF triples in Turtle format. Use a namespace prefix like:
  @prefix : <http://example.org#> .
Use classes such as `:RegulationRule`, `:PersonalData`, `:requires`, `:appliesTo`, and attributes like `:encrypted`. Output only valid RDF in Turtle syntax.

Here is the regulatory context from laws:
{reg_context_str}

Context from previous policy sections:
{policy_context}

Do not generate any RDF triples for the text in the previous articles or regulations. Only use them for context.
Here is the text to process and generate RDF triples for:
{section_text}
"""

    # Generate RDF using Gemini
    print(f"🔍 Processing {filename}...")
    try:
        response = model.generate_content(prompt)
        rdf_output = response.text.strip()
    except Exception as e:
        print(f"❌ Error in {filename}: {e}")
        continue

    # Save RDF output
    output_filename = filename.replace(".txt", ".ttl")
    output_path = os.path.join(OUTPUT_FOLDER, output_filename)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(rdf_output)

    print(f"✅ Saved RDF: {output_filename}")

    # Store this translation for future context
    previous_translations.append(rdf_output)

print("\n🎉 All sections processed.")