import os
import google.generativeai as genai

# === Setup ===
SECTION_FOLDER = "policy_sections"
OUTPUT_FOLDER = "policy_rdf_output"
API_KEY_FILE = "api_key.txt"
MODEL_NAME = "models/gemini-1.5-flash"

# === Ensure output folder exists ===
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# === Load API key and configure Gemini ===
with open(API_KEY_FILE, "r", encoding="utf-8") as key_file:
    api_key = key_file.read().strip()
genai.configure(api_key=api_key)

model = genai.GenerativeModel(MODEL_NAME)

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

    # Build prompt, including previous RDF outputs if available
    context = "\n\n".join(previous_translations)
    prompt = f"""
You are an expert in legal informatics. Given a legal or policy document, extract the key legal entities, classes (like PersonalData), and obligations (like encryption requirements), and represent them as RDF triples in Turtle format. Use a namespace prefix like:
  @prefix : <http://example.org#> .
Use classes such as `:RegulationRule`, `:PersonalData`, `:requires`, `:appliesTo`, and attributes like `:encrypted`. Output only valid RDF in Turtle syntax.

Context from previous sections:
{context}

Do not generate any RDF triples for the text in the previous articles. Only use them for context.
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
