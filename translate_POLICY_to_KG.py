import os
import google.generativeai as genai
from rdflib import Graph, Namespace, RDF

# === Setup ===
SECTION_FOLDER = "policy_sections"
OUTPUT_FOLDER = "policy_rdf_output_with_regulation_context"
REGULATION_RDF_FOLDER = "shacl_output_fixed"
API_KEY_FILE = "api_key.txt"
MODEL_NAME = "models/gemini-1.5-flash"
TARGET_SECTION = "Section_3_7.txt"  # The section to process

# === Ensure output folder exists ===
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# === Load API key and configure Gemini ===
with open(API_KEY_FILE, "r", encoding="utf-8") as key_file:
    api_key = key_file.read().strip()
genai.configure(api_key=api_key)

model = genai.GenerativeModel(MODEL_NAME)

# === Extract SHACL terms from TTL files ===
def extract_shacl_terms(shacl_folder):
    SH = Namespace("http://www.w3.org/ns/shacl#")
    class_terms = set()
    property_terms = set()

    for filename in os.listdir(shacl_folder):
        if filename.endswith(".ttl"):
            g = Graph()
            g.parse(os.path.join(shacl_folder, filename), format="turtle")

            for shape in g.subjects(RDF.type, SH.NodeShape):
                target_class = g.value(subject=shape, predicate=SH.targetClass)
                if target_class:
                    class_terms.add(str(target_class))

                for prop in g.objects(subject=shape, predicate=SH.property):
                    path = g.value(subject=prop, predicate=SH.path)
                    if path:
                        property_terms.add(str(path))

    return sorted(class_terms), sorted(property_terms)

# === Get SHACL-derived vocabulary
print("🔍 Extracting SHACL vocabulary...")
try:
    shacl_classes, shacl_properties = extract_shacl_terms(REGULATION_RDF_FOLDER)
    vocab_hint = f"""
Use only the following SHACL-derived vocabulary when naming classes and properties:

Classes:
{', '.join([c.split('#')[-1] for c in shacl_classes])}

Properties:
{', '.join([p.split('#')[-1] for p in shacl_properties])}
"""
except Exception as e:
    print(f"⚠️ Warning: Could not extract SHACL vocabulary: {e}")
    vocab_hint = ""

# === Load regulation RDF for context ===
regulation_context = []
print("📥 Loading regulation context...")
try:
    regulation_files = sorted(
        [f for f in os.listdir(REGULATION_RDF_FOLDER) if f.lower().endswith(".ttl")],
        key=lambda x: int(x.replace("Article_", "").replace(".ttl", "")) if x.replace("Article_", "").replace(".ttl", "").isdigit() else 0
    )
    for reg_file in regulation_files[:10]:
        with open(os.path.join(REGULATION_RDF_FOLDER, reg_file), "r", encoding="utf-8") as f:
            regulation_context.append(f.read().strip())
    print(f"✅ Loaded {len(regulation_context)} regulation files")
except Exception as e:
    print(f"⚠️ Warning: Could not load regulation RDF context: {e}")

# === Load other policy sections as context ===
context_sections = []
print("📥 Loading other policy sections for context...")
section_files = [f for f in os.listdir(SECTION_FOLDER)
                 if f.lower().endswith(".txt") and f != TARGET_SECTION]
try:
    for context_file in section_files[:10]:
        with open(os.path.join(SECTION_FOLDER, context_file), "r", encoding="utf-8") as f:
            context_sections.append(f"Section: {context_file}\n{f.read().strip()}")
    print(f"✅ Loaded {len(context_sections)} policy sections")
except Exception as e:
    print(f"⚠️ Warning: Could not load policy section context: {e}")

# === Load target section ===
target_path = os.path.join(SECTION_FOLDER, TARGET_SECTION)
if not os.path.exists(target_path):
    print(f"❌ Error: Target section file {TARGET_SECTION} not found!")
    exit(1)

with open(target_path, "r", encoding="utf-8") as f:
    section_text = f.read().strip()

# === Assemble Prompt ===
reg_context_str = "\n\n".join(regulation_context[:3])
policy_context_str = "\n\n".join(context_sections[:3])

prompt = f"""
You are an expert in legal informatics. Given a legal or policy document, extract the key legal entities, classes (like PersonalData), and obligations (like encryption requirements), and represent them as RDF triples in Turtle format. Use a namespace prefix like:
  @prefix : <http://example.org#> .
Use classes such as `:RegulationRule`, `:PersonalData`, `:requires`, `:appliesTo`, and attributes like `:encrypted`. Output only valid RDF in Turtle syntax.

{vocab_hint}

Here is the regulatory context from laws:
{reg_context_str}

Context from other policy sections:
{policy_context_str}

Do not generate any RDF triples for the text in previous articles or other sections. Only use them for context.
Here is the text to process and generate RDF triples for:
{section_text}
"""

# === Generate RDF ===
print(f"\n🔧 Generating RDF for {TARGET_SECTION}...")
try:
    response = model.generate_content(prompt)
    rdf_output = response.text.strip()

    output_filename = TARGET_SECTION.replace(".txt", ".ttl")
    output_path = os.path.join(OUTPUT_FOLDER, output_filename)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(rdf_output)

    print(f"✅ Saved RDF: {output_filename}")
except Exception as e:
    print(f"❌ Error during generation: {e}")

print("\n🎉 Done.")
