import os
import google.generativeai as genai

# === Setup ===
ARTICLE_FOLDER = "greek_articles"
OUTPUT_FOLDER = "rdf_output"
API_KEY_FILE = "api_key.txt"
MODEL_NAME = "models/gemini-1.5-flash"

# === Ensure output folder exists ===
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# === Load API key and configure Gemini ===
with open(API_KEY_FILE, "r", encoding="utf-8") as key_file:
    api_key = key_file.read().strip()
genai.configure(api_key=api_key)

model = genai.GenerativeModel(MODEL_NAME)

# === Get sorted list of article files ===
article_files = sorted(
    [f for f in os.listdir(ARTICLE_FOLDER) if f.lower().startswith("article") and f.endswith(".txt")],
    key=lambda x: int("".join(filter(str.isdigit, x)))
)

previous_translations = []

# === Process each article ===
for i, filename in enumerate(article_files):
    filepath = os.path.join(ARTICLE_FOLDER, filename)
    with open(filepath, "r", encoding="utf-8") as f:
        article_text = f.read().strip()

    # Build prompt, including previous RDF outputs if available
    context = "\n\n".join(previous_translations)
    prompt = f"""
You are an expert legal knowledge extractor. Convert the following legal documents into a symbolic knowledge graph.

Use only the following ontology:

**Classes:**
- :RegulationRule
- :Obligation
- :Authority
- :LegalEntity
- :LegalEntityClass
- :TimePeriod

**Properties:**
- :requires
- :appliesTo
- :responsibleFor
- :references
- :timeLimit
- :definedBy
- :partOf

Output RDF-style triples in Turtle syntax, ensure that there are no syntax errors. Do not include labels or explanations.

Example:
:Article16 a :RegulationRule ;
:requires :IncidentNotification ;
:appliesTo :EssentialEntity .

:IncidentNotification a :Obligation ;
:timeLimit :24Hours .

:EssentialEntity a :LegalEntityClass .
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

print("\n🎉 All articles processed.")
