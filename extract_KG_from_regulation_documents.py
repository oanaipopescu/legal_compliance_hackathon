import google.generativeai as genai

# 1. Configure Gemini API
genai.configure(api_key="AIzaSyCfPx5AFghEDGOzEISlpXrse3T7rys8v1w")  # Replace with your Gemini API key

# 3. Load TXT content (national implementation)
def load_txt(path):
    with open(path, 'r', encoding='utf-8') as file:
        return file.read()

# 4. Prompt for structured triple extraction
def build_prompt(eu_text, national_text):
    return f"""
You are a legal knowledge graph extraction expert.

You will receive the full text of a legal or policy document.  
Your task is to extract a complete and symbolic RDF knowledge graph in **Turtle syntax**, following the ontology of the EU NIS 2 Directive (Directive (EU) 2022/2555).

This graph will later be used to **compare a document against NIS 2**, so the structure must align.

---

### 🧩 Ontology

**Classes**:  
`:RegulationRule`, `:PolicyRule`, `:Obligation`, `:Authority`, `:LegalEntity`, `:LegalEntityClass`, `:Role`, `:TimePeriod`, `:Task`

**Properties**:  
`:requires`, `:appliesTo`, `:responsibleFor`, `:references`, `:definedBy`, `:timeLimit`, `:partOf`, `:excludedFrom`

---

### 📌 Requirements

- Use **one triple set per article or rule**
- Use symbolic URIs (e.g., `:Article14`, `:DataProtectionOfficer`, `:IncidentNotification`)
- DO NOT include labels, explanations, or natural language
- DO NOT summarize — you must go through the ENTIRE DOCUMENT
- DO NOT skip any part — especially the following articles in the national implementation:
  - **Article 11**
  - **Article 12**
  - **Article 13**
  - **Article 14**
  - **Article 15**
  - **Article 60**

You must **output all obligations**, deadlines, and responsible entities from these articles in particular.
---

---  
**EU Directive**  
\"\"\"  
{eu_text[:4000]}  
\"\"\"  

---  
**National Implementation**  
\"\"\"  
{national_text[:4000]}  
\"\"\"  
"""

# 5. Generate RDF triples using Gemini
def extract_knowledge_graph(eu_path, national_txt_path):
    eu_text = load_txt(eu_path)
    national_text = load_txt(national_txt_path)
    prompt = build_prompt(eu_text, national_text)

    model = genai.GenerativeModel(model_name="models/gemini-1.5-flash")
    response = model.generate_content(prompt)
    return response.text

# 6. Save output
def save_to_file(text, path="knowledge_graph_output.ttl"):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"Knowledge graph saved to {path}")

# 7. Run everything
if __name__ == "__main__":
    eu_path = './translated_regulations/nis2.txt'
    national_path = './translated_regulations/romania.txt'
    ttl_output = extract_knowledge_graph(eu_path, national_path)
    save_to_file(ttl_output)
