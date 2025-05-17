import os
import re
from rdflib import Graph
from pyshacl import validate

# === Configuration ===
POLICY_FOLDER = "policy_rdf_output_fixed"
SHACL_FOLDER = "shacl_output_fixed"
REPORT_FOLDER = "compliance_reports"
SUMMARY_FILE = "compliance_summary.txt"

# Specify which articles you want to test (empty list means test all)
# Example: [14, 15, 16, 26]
SELECTED_ARTICLES = [14, 15, 16, 26]

# === Ensure report folder exists ===
os.makedirs(REPORT_FOLDER, exist_ok=True)

# === Extract article number from filename ===
def extract_article_number(filename):
    match = re.search(r'Article_(\d+)', filename)
    if match:
        return int(match.group(1))
    return None

# === Get files ===
policy_files = sorted([f for f in os.listdir(POLICY_FOLDER) if f.endswith(".ttl")])

# Filter SHACL files based on selected articles
all_shacl_files = [f for f in os.listdir(SHACL_FOLDER) if f.endswith(".ttl")]
if SELECTED_ARTICLES:
    shacl_files = [f for f in all_shacl_files 
                   if extract_article_number(f) in SELECTED_ARTICLES]
    print(f"Testing with selected articles: {', '.join(map(str, SELECTED_ARTICLES))}")
    print(f"Found {len(shacl_files)} matching SHACL files")
else:
    shacl_files = all_shacl_files
    print(f"Testing with all {len(shacl_files)} SHACL files")

# === Track overall results ===
summary_lines = []
compliant_count = 0
non_compliant_count = 0

# === Check each policy section against each selected SHACL article ===
for policy_file in policy_files:
    policy_path = os.path.join(POLICY_FOLDER, policy_file)
    policy_graph = Graph()
    policy_graph.parse(policy_path, format="turtle")

    for shacl_file in shacl_files:
        shacl_path = os.path.join(SHACL_FOLDER, shacl_file)
        try:
            shacl_graph = Graph()
            shacl_graph.parse(shacl_path, format="turtle")

            conforms, report_graph, report_text = validate(
                data_graph=policy_graph,
                shacl_graph=shacl_graph,
                inference='rdfs',
                debug=False
            )

            base_policy = policy_file.replace(".ttl", "")
            base_shacl = shacl_file.replace(".ttl", "")
            
            if conforms:
                result_label = "✅ COMPLIANT"
                compliant_count += 1
            else:
                result_label = "❌ NON-COMPLIANT"
                non_compliant_count += 1
                
                # Only save detailed report for non-compliant results
                report_filename = f"{base_policy}__VS__{base_shacl}.txt"
                report_path = os.path.join(REPORT_FOLDER, report_filename)
                with open(report_path, "w", encoding="utf-8") as f:
                    f.write("Conforms: " + str(conforms) + "\n\n")
                    f.write(report_text)
            
            summary_line = f"{base_policy} vs {base_shacl}: {result_label}"
            summary_lines.append(summary_line)
            print(f"{summary_line}")
            
        except Exception as e:
            print(f"⚠️ Error processing {shacl_file}: {e}")

# === Write overall summary file ===
with open(os.path.join(REPORT_FOLDER, SUMMARY_FILE), "w", encoding="utf-8") as f:
    f.write("\n".join(summary_lines))
    f.write(f"\n\nTotal: {compliant_count + non_compliant_count}")
    f.write(f"\nCompliant: {compliant_count}")
    f.write(f"\nNon-compliant: {non_compliant_count}")

print(f"\n🎉 Compliance checking complete.")
print(f"Found {compliant_count} compliant and {non_compliant_count} non-compliant rules.")
print(f"Summary saved to: {os.path.join(REPORT_FOLDER, SUMMARY_FILE)}")